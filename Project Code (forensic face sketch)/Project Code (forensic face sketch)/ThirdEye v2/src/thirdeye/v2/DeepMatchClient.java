package thirdeye.v2;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.io.File;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;

/**
 * REST client for the ThirdEye ML service (Python/FastAPI + FaceNet).
 *
 * <p>Sends the composite sketch to the service and receives a ranked list of
 * dataset suspects by cosine similarity on face embeddings. Uses the JDK
 * built-in HttpClient — no extra dependencies required.
 */
public class DeepMatchClient {

    private static final String DEFAULT_BASE_URL = "http://127.0.0.1:8000";

    private final String baseUrl;
    private final HttpClient http;
    private String authToken;

    public DeepMatchClient() {
        this(DEFAULT_BASE_URL);
    }

    public DeepMatchClient(String baseUrl) {
        this.baseUrl = baseUrl.endsWith("/") ? baseUrl.substring(0, baseUrl.length() - 1) : baseUrl;
        this.http = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(5))
                .version(HttpClient.Version.HTTP_1_1)
                .build();
    }

    /** Fetches a new JWT access token from the ML service. */
    public String fetchAuthToken() throws IOException {
        JsonObject reqJson = new JsonObject();
        reqJson.addProperty("client_id", "thirdeye_desktop_client");

        HttpRequest req = HttpRequest.newBuilder(URI.create(baseUrl + "/auth/token"))
                .timeout(Duration.ofSeconds(10))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(reqJson.toString()))
                .build();
        try {
            HttpResponse<String> resp = http.send(req, HttpResponse.BodyHandlers.ofString());
            if (resp.statusCode() == 200) {
                JsonObject json = JsonParser.parseString(resp.body()).getAsJsonObject();
                this.authToken = json.get("access_token").getAsString();
                return this.authToken;
            } else {
                throw new IOException("Failed to obtain JWT token from ML service: HTTP " + resp.statusCode());
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new IOException("Interrupted while fetching JWT token", e);
        }
    }

    public void setAuthToken(String token) {
        this.authToken = token;
    }

    public String getAuthToken() {
        return this.authToken;
    }

    /**
     * Fetches Explainable AI (XAI) side-by-side matching heatmap PNG bytes.
     */
    public byte[] fetchMatchHeatmap(File sketchFile, String candidatePath) throws IOException {
        if (authToken == null || authToken.isEmpty()) {
            try { fetchAuthToken(); } catch (Exception ignored) {}
        }
        String b = "----ThirdEyeXAI" + System.nanoTime();
        StringBuilder bodyStr = new StringBuilder();
        bodyStr.append("--").append(b).append("\r\n");
        bodyStr.append("Content-Disposition: form-data; name=\"file\"; filename=\"").append(sketchFile.getName()).append("\"\r\n");
        bodyStr.append("Content-Type: application/octet-stream\r\n\r\n");

        byte[] headBytes = bodyStr.toString().getBytes(StandardCharsets.UTF_8);
        byte[] fileBytes = Files.readAllBytes(sketchFile.toPath());

        StringBuilder tailStr = new StringBuilder();
        tailStr.append("\r\n--").append(b).append("\r\n");
        tailStr.append("Content-Disposition: form-data; name=\"candidate_path\"\r\n\r\n");
        tailStr.append(candidatePath);
        tailStr.append("\r\n--").append(b).append("--\r\n");
        byte[] tailBytes = tailStr.toString().getBytes(StandardCharsets.UTF_8);

        byte[] body = new byte[headBytes.length + fileBytes.length + tailBytes.length];
        System.arraycopy(headBytes, 0, body, 0, headBytes.length);
        System.arraycopy(fileBytes, 0, body, headBytes.length, fileBytes.length);
        System.arraycopy(tailBytes, 0, body, headBytes.length + fileBytes.length, tailBytes.length);

        HttpRequest.Builder reqBuilder = HttpRequest.newBuilder(URI.create(baseUrl + "/explain"))
                .timeout(Duration.ofSeconds(60))
                .header("Content-Type", "multipart/form-data; boundary=" + b)
                .POST(HttpRequest.BodyPublishers.ofByteArray(body));

        if (authToken != null && !authToken.isEmpty()) {
            reqBuilder.header("Authorization", "Bearer " + authToken);
        }

        try {
            HttpResponse<byte[]> resp = http.send(reqBuilder.build(), HttpResponse.BodyHandlers.ofByteArray());
            if (resp.statusCode() == 200) {
                return resp.body();
            } else {
                throw new IOException("XAI Heatmap request failed with HTTP " + resp.statusCode());
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new IOException("Interrupted while fetching XAI heatmap", e);
        }
    }


    /** Result row for a single ranked suspect. */
    public static class Match {
        public String name;
        public String path;
        public double similarity;
        public double calibratedScore;
        public int rank;
    }

    /** Detailed response holder containing modality, pipeline selection, open-set match decision, and soft biometric filter stats. */
    public static class MatchResponseHolder {
        public String status = "ok";
        public String queryModality = "UNKNOWN";
        public String selectedPipeline = "UNKNOWN";
        public String matchDecision = "POSSIBLE MATCH";
        public double threshold = 0.55;
        public boolean demographicFilterApplied = false;
        public String genderFilter = "ALL";
        public int candidatesEvaluated = 0;
        public int candidatesPruned = 0;
        public List<String> warnings = new ArrayList<>();
        public List<Match> results = new ArrayList<>();
    }

    /**
     * Checks the service is reachable and its model is loaded.
     * @throws IOException when the service is unreachable
     */
    public boolean isHealthy() throws IOException {
        HttpRequest req = HttpRequest.newBuilder(URI.create(baseUrl + "/health"))
                .timeout(Duration.ofSeconds(3))
                .GET()
                .build();
        try {
            HttpResponse<String> resp = http.send(req, HttpResponse.BodyHandlers.ofString());
            if (resp.statusCode() != 200) return false;
            JsonObject json = JsonParser.parseString(resp.body()).getAsJsonObject();
            return "ok".equals(json.get("status").getAsString())
                    && json.get("model_loaded").getAsBoolean();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new IOException("Interrupted while checking service health", e);
        } catch (java.net.ConnectException | java.net.http.HttpConnectTimeoutException e) {
            throw new IOException("ML service is not running at " + baseUrl + ". "
                    + "Start it with: uvicorn app:app --port 8000 (see ml_service/README.md)", e);
        }
    }

    public List<Match> match(File sketchFile, File datasetDir, int topN) throws IOException {
        return matchDetailed(sketchFile, datasetDir, topN, "ALL", 0, 100).results;
    }

    public MatchResponseHolder matchDetailed(File sketchFile, File datasetDir, int topN) throws IOException {
        return matchDetailed(sketchFile, datasetDir, topN, "ALL", 0, 100);
    }

    public MatchResponseHolder matchDetailed(File sketchFile, File datasetDir, int topN,
                                           String genderFilter, int minAgeFilter, int maxAgeFilter) throws IOException {
        if (authToken == null || authToken.isEmpty()) {
            try {
                fetchAuthToken();
            } catch (Exception e) {
                System.err.println("Warning: Could not pre-fetch JWT token: " + e.getMessage());
            }
        }

        byte[] boundary = ("----ThirdEye" + System.nanoTime()).getBytes(StandardCharsets.US_ASCII);
        byte[] body = buildMultipart(sketchFile, datasetDir, topN, genderFilter, minAgeFilter, maxAgeFilter, boundary);

        HttpRequest.Builder reqBuilder = HttpRequest.newBuilder(URI.create(baseUrl + "/match"))
                .timeout(Duration.ofSeconds(120))
                .header("Content-Type", "multipart/form-data; boundary=" + new String(boundary, StandardCharsets.US_ASCII))
                .POST(HttpRequest.BodyPublishers.ofByteArray(body));

        if (authToken != null && !authToken.isEmpty()) {
            reqBuilder.header("Authorization", "Bearer " + authToken);
        }

        HttpRequest req = reqBuilder.build();

        HttpResponse<String> resp;
        try {
            resp = http.send(req, HttpResponse.BodyHandlers.ofString());
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new IOException("Interrupted while matching", e);
        } catch (java.net.ConnectException | java.net.http.HttpConnectTimeoutException e) {
            throw new IOException("ML service is not running at " + baseUrl + ". "
                    + "Start it with: uvicorn app:app --port 8000 (see ml_service/README.md)", e);
        }

        if (resp.statusCode() != 200) {
            throw new IOException("ML service returned HTTP " + resp.statusCode() + ": " + resp.body());
        }

        JsonObject json = JsonParser.parseString(resp.body()).getAsJsonObject();
        MatchResponseHolder holder = new MatchResponseHolder();
        holder.status = json.has("status") ? json.get("status").getAsString() : "ok";
        holder.queryModality = json.has("query_modality") ? json.get("query_modality").getAsString() : "UNKNOWN";
        holder.selectedPipeline = json.has("selected_pipeline") ? json.get("selected_pipeline").getAsString() : "UNKNOWN";
        holder.matchDecision = json.has("match_decision") ? json.get("match_decision").getAsString() : "POSSIBLE MATCH";
        holder.threshold = json.has("threshold") ? json.get("threshold").getAsDouble() : 0.55;
        holder.demographicFilterApplied = json.has("demographic_filter_applied") && json.get("demographic_filter_applied").getAsBoolean();
        holder.genderFilter = json.has("gender_filter") ? json.get("gender_filter").getAsString() : "ALL";
        holder.candidatesEvaluated = json.has("candidates_evaluated") ? json.get("candidates_evaluated").getAsInt() : 0;
        holder.candidatesPruned = json.has("candidates_pruned") ? json.get("candidates_pruned").getAsInt() : 0;

        if (json.has("warnings") && json.get("warnings").isJsonArray()) {
            JsonArray wArr = json.getAsJsonArray("warnings");
            for (int i = 0; i < wArr.size(); i++) {
                holder.warnings.add(wArr.get(i).getAsString());
            }
        }

        JsonArray arr = json.getAsJsonArray("results");
        if (arr != null) {
            for (int i = 0; i < arr.size(); i++) {
                JsonObject o = arr.get(i).getAsJsonObject();
                Match m = new Match();
                m.name = o.has("name") ? o.get("name").getAsString() : "Unknown";
                m.path = o.has("path") ? o.get("path").getAsString() : "";
                m.similarity = o.has("similarity") ? o.get("similarity").getAsDouble() : 0.0;
                m.calibratedScore = o.has("calibrated_score") ? o.get("calibrated_score").getAsDouble() : (m.similarity * 100.0);
                m.rank = o.has("rank") ? o.get("rank").getAsInt() : (i + 1);
                holder.results.add(m);
            }
        }
        return holder;
    }

    // ── Multipart body builder ────────────────────────────────────────────────
    private static byte[] buildMultipart(File sketchFile, File datasetDir, int topN,
                                         String genderFilter, int minAgeFilter, int maxAgeFilter,
                                         byte[] boundary) throws IOException {
        String b = new String(boundary, StandardCharsets.US_ASCII);

        // Part 1: sketch file
        StringBuilder head = new StringBuilder();
        head.append("--").append(b).append("\r\n");
        head.append("Content-Disposition: form-data; name=\"file\"; filename=\"")
                .append(sketchFile.getName()).append("\"\r\n");
        head.append("Content-Type: application/octet-stream\r\n\r\n");
        byte[] headBytes = head.toString().getBytes(StandardCharsets.UTF_8);
        byte[] fileBytes = Files.readAllBytes(sketchFile.toPath());

        // Part 2: Form fields
        StringBuilder tail = new StringBuilder();
        tail.append("\r\n--").append(b).append("\r\n");
        tail.append("Content-Disposition: form-data; name=\"dataset_dir\"\r\n\r\n");
        tail.append(datasetDir.getAbsolutePath());
        tail.append("\r\n--").append(b).append("\r\n");
        tail.append("Content-Disposition: form-data; name=\"top_n\"\r\n\r\n");
        tail.append(topN);
        tail.append("\r\n--").append(b).append("\r\n");
        tail.append("Content-Disposition: form-data; name=\"gender_filter\"\r\n\r\n");
        tail.append(genderFilter != null ? genderFilter : "ALL");
        tail.append("\r\n--").append(b).append("\r\n");
        tail.append("Content-Disposition: form-data; name=\"min_age_filter\"\r\n\r\n");
        tail.append(minAgeFilter);
        tail.append("\r\n--").append(b).append("\r\n");
        tail.append("Content-Disposition: form-data; name=\"max_age_filter\"\r\n\r\n");
        tail.append(maxAgeFilter);
        tail.append("\r\n--").append(b).append("--\r\n");
        byte[] tailBytes = tail.toString().getBytes(StandardCharsets.UTF_8);

        byte[] body = new byte[headBytes.length + fileBytes.length + tailBytes.length];
        System.arraycopy(headBytes, 0, body, 0, headBytes.length);
        System.arraycopy(fileBytes, 0, body, headBytes.length, fileBytes.length);
        System.arraycopy(tailBytes, 0, body, headBytes.length + fileBytes.length, tailBytes.length);
        return body;
    }
}

