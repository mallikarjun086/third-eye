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

    /** Result row for a single ranked suspect. */
    public static class Match {
        public String name;
        public String path;
        public double similarity;
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

    /**
     * Matches a sketch against all images in the given dataset directory.
     *
     * @param sketchFile  the composite sketch image
     * @param datasetDir  directory containing suspect photos
     * @param topN        maximum number of ranked results
     * @return ranked matches, best first
     * @throws IOException network/IO failure
     */
    public List<Match> match(File sketchFile, File datasetDir, int topN) throws IOException {
        byte[] boundary = ("----ThirdEye" + System.nanoTime()).getBytes(StandardCharsets.US_ASCII);
        byte[] body = buildMultipart(sketchFile, datasetDir, topN, boundary);

        HttpRequest req = HttpRequest.newBuilder(URI.create(baseUrl + "/match"))
                .timeout(Duration.ofSeconds(120))
                .header("Content-Type", "multipart/form-data; boundary=" + new String(boundary, StandardCharsets.US_ASCII))
                .POST(HttpRequest.BodyPublishers.ofByteArray(body))
                .build();

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
        List<Match> results = new ArrayList<>();
        JsonArray arr = json.getAsJsonArray("results");
        if (arr != null) {
            for (int i = 0; i < arr.size(); i++) {
                JsonObject o = arr.get(i).getAsJsonObject();
                Match m = new Match();
                m.name = o.has("name") ? o.get("name").getAsString() : "Unknown";
                m.path = o.has("path") ? o.get("path").getAsString() : "";
                m.similarity = o.has("similarity") ? o.get("similarity").getAsDouble() : 0.0;
                results.add(m);
            }
        }
        return results;
    }

    // ── Multipart body builder ────────────────────────────────────────────────
    private static byte[] buildMultipart(File sketchFile, File datasetDir, int topN, byte[] boundary)
            throws IOException {
        String b = new String(boundary, StandardCharsets.US_ASCII);

        // Part 1: sketch file — headers + bytes, in the correct order
        StringBuilder head = new StringBuilder();
        head.append("--").append(b).append("\r\n");
        head.append("Content-Disposition: form-data; name=\"file\"; filename=\"")
                .append(sketchFile.getName()).append("\"\r\n");
        head.append("Content-Type: application/octet-stream\r\n\r\n");
        byte[] headBytes = head.toString().getBytes(StandardCharsets.UTF_8);
        byte[] fileBytes = Files.readAllBytes(sketchFile.toPath());

        // Part 2 + 3: dataset_dir and top_n fields
        StringBuilder tail = new StringBuilder();
        tail.append("\r\n--").append(b).append("\r\n");
        tail.append("Content-Disposition: form-data; name=\"dataset_dir\"\r\n\r\n");
        tail.append(datasetDir.getAbsolutePath());
        tail.append("\r\n--").append(b).append("\r\n");
        tail.append("Content-Disposition: form-data; name=\"top_n\"\r\n\r\n");
        tail.append(topN);
        tail.append("\r\n--").append(b).append("--\r\n");
        byte[] tailBytes = tail.toString().getBytes(StandardCharsets.UTF_8);

        byte[] body = new byte[headBytes.length + fileBytes.length + tailBytes.length];
        System.arraycopy(headBytes, 0, body, 0, headBytes.length);
        System.arraycopy(fileBytes, 0, body, headBytes.length, fileBytes.length);
        System.arraycopy(tailBytes, 0, body, headBytes.length + fileBytes.length, tailBytes.length);
        return body;
    }
}
