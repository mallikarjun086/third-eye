package thirdeye.v2;

import java.awt.Color;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.ResourceBundle;
import java.util.logging.Level;
import java.util.logging.Logger;
import javafx.application.Platform;
import javafx.concurrent.Task;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.control.Alert;
import javafx.scene.control.Button;
import javafx.scene.control.ButtonBar;
import javafx.scene.control.ButtonType;
import javafx.scene.control.Dialog;
import javafx.scene.control.Label;
import javafx.scene.control.ProgressBar;
import javafx.scene.control.ScrollPane;
import javafx.scene.control.TextInputDialog;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.layout.FlowPane;
import javafx.scene.layout.VBox;
import javafx.stage.FileChooser;
import javafx.stage.Stage;
import javax.imageio.ImageIO;
import javafx.fxml.FXMLLoader;
import javafx.scene.Scene;
import javafx.scene.Node;
import javafx.event.ActionEvent;

/**
 * Forensic Face Comparison Controller — Enhanced Multi-Metric Algorithm.
 * Uses pure Java image analysis (no external libraries).
 *
 * Algorithm (v2 — Enhanced):
 *   1. Resize both images to 256×256 (aspect-ratio preserving with padding)
 *   2. Convert to greyscale (luminosity formula)
 *   3. Apply histogram equalisation (normalises lighting differences)
 *   4. Compute SSIM (Structural Similarity Index) — perceptual quality metric
 *   5. Compute Sobel edge maps and edge correlation — sketch↔photo bridge
 *   6. Compute HOG (Histogram of Oriented Gradients) similarity — shape/contour
 *   7. Compute histogram intersection — tonal distribution overlap
 *   8. Weighted multi-metric fusion → final similarity %
 *
 * @author Mallikarjun Gala
 */
public class Upload_sketchController implements Initializable {

    // ── Comparison parameters ────────────────────────────────────────────────
    private static final int    COMPARE_SIZE    = 256;

    // 5-tier confidence thresholds
    private static final double STRONG_MATCH    = 0.90;
    private static final double LIKELY_MATCH    = 0.75;
    private static final double POSSIBLE_MATCH  = 0.60;
    private static final double UNLIKELY_MATCH  = 0.40;

    // Metric fusion weights — edge detection weighted highest for sketch↔photo
    // These are now instance fields adjustable via UI sliders
    private double wSsim  = 0.25;
    private double wEdge  = 0.35;
    private double wHog   = 0.25;
    private double wHist  = 0.15;

    // Current weight values (from sliders, normalized to sum 1.0)
    private double curWSsim  = 0.25;
    private double curWEdge  = 0.35;
    private double curWHog   = 0.25;
    private double curWHist  = 0.15;

    // SSIM parameters
    private static final int    SSIM_WINDOW     = 8;   // block size for local SSIM
    private static final double SSIM_C1         = (0.01 * 255) * (0.01 * 255); // stabiliser
    private static final double SSIM_C2         = (0.03 * 255) * (0.03 * 255); // stabiliser

    // HOG parameters
    private static final int    HOG_CELL_SIZE   = 8;
    private static final int    HOG_NUM_BINS    = 9;

    // ── Face region weight map ────────────────────────────────────────────────
    // Emphasizes central facial features (eyes, nose, mouth) over background/padding
    private static double[][] faceWeightMap = null;

    private static double[][] getFaceWeightMap() {
        if (faceWeightMap == null) {
            faceWeightMap = createFaceWeightMap(COMPARE_SIZE);
        }
        return faceWeightMap;
    }

    // ── Gaussian kernel for SSIM (sigma=1.5, same as original Wang et al. 2004) ──
    private static double[] ssimGaussianKernel = null;
    private static double    ssimGaussianSum   = 0;

    private static double[] getSsimGaussianKernel() {
        if (ssimGaussianKernel == null) {
            int w = SSIM_WINDOW;
            ssimGaussianKernel = new double[w * w];
            double sigma = 1.5;
            double twoSigmaSq = 2.0 * sigma * sigma;
            int half = w / 2;
            double sum = 0;
            for (int dy = 0; dy < w; dy++) {
                for (int dx = 0; dx < w; dx++) {
                    double g = Math.exp(-((dx - half) * (dx - half) + (dy - half) * (dy - half)) / twoSigmaSq);
                    ssimGaussianKernel[dy * w + dx] = g;
                    sum += g;
                }
            }
            ssimGaussianSum = sum;
        }
        return ssimGaussianKernel;
    }

    /**
     * Creates an elliptical weight map that gives higher importance to
     * central facial features and lower importance to background/padding.
     * Core face ellipse (rx=0.38, ry=0.50 of image):  weight 4.0
     * Face boundary ring:                              weight 1.5
     * Background/padding:                              weight 0.2
     */
    private static double[][] createFaceWeightMap(int size) {
        double[][] map = new double[size][size];
        double cx = size / 2.0;
        double cy = size / 2.0;
        double rx = size * 0.38;
        double ry = size * 0.50;
        for (int y = 0; y < size; y++) {
            for (int x = 0; x < size; x++) {
                double dx = (x - cx) / rx;
                double dy = (y - cy) / ry;
                double d = Math.sqrt(dx * dx + dy * dy);
                if (d < 0.5) {
                    map[y][x] = 4.0;
                } else if (d < 1.0) {
                    map[y][x] = 1.5;
                } else {
                    map[y][x] = 0.2;
                }
            }
        }
        return map;
    }

    @FXML private ImageView  sketchView;
    @FXML private ImageView  photoView;
    @FXML private Label      percentLabel;
    @FXML private Label      resultLabel;
    @FXML private Label      statusBar;
    @FXML private Label      sketchLabel;
    @FXML private Label      photoLabel;
    @FXML private Label      photoHint;
    @FXML private ProgressBar progressBar;
    @FXML private Button     compareBtn;
    @FXML private Button     saveResultBtn;
    @FXML private Button     manageGalleryBtn;
    @FXML private Button     deepMatchBtn;
    @FXML private javafx.scene.control.Slider weightSsimSlider;
    @FXML private javafx.scene.control.Slider weightEdgeSlider;
    @FXML private javafx.scene.control.Slider weightHogSlider;
    @FXML private javafx.scene.control.Slider weightHistSlider;
    @FXML private Label      weightSsimLabel;
    @FXML private Label      weightEdgeLabel;
    @FXML private Label      weightHogLabel;
    @FXML private Label      weightHistLabel;
    @FXML private Label      weightStatusLabel;

    private File   sketchFile;
    private File   photoFile;
    private double lastSimilarity = 0;

    // Per-metric scores for detailed reporting
    private double lastSsimScore  = 0;
    private double lastEdgeScore  = 0;
    private double lastHogScore   = 0;
    private double lastHistScore  = 0;

    @Override
    public void initialize(URL url, ResourceBundle rb) {
        compareBtn.setDisable(true);
        if (saveResultBtn != null) saveResultBtn.setDisable(true);
        SuspectDatabase.init();
        initWeightSliders();
    }

    private void initWeightSliders() {
        javafx.beans.value.ChangeListener<Number> listener = (obs, oldVal, newVal) -> updateWeights();
        if (weightSsimSlider != null) {
            weightSsimSlider.setValue(wSsim * 100);
            weightSsimSlider.valueProperty().addListener(listener);
        }
        if (weightEdgeSlider != null) {
            weightEdgeSlider.setValue(wEdge * 100);
            weightEdgeSlider.valueProperty().addListener(listener);
        }
        if (weightHogSlider != null) {
            weightHogSlider.setValue(wHog * 100);
            weightHogSlider.valueProperty().addListener(listener);
        }
        if (weightHistSlider != null) {
            weightHistSlider.setValue(wHist * 100);
            weightHistSlider.valueProperty().addListener(listener);
        }
        updateWeights();
    }

    private void updateWeights() {
        double s = weightSsimSlider != null ? weightSsimSlider.getValue() : wSsim * 100;
        double e = weightEdgeSlider != null ? weightEdgeSlider.getValue() : wEdge * 100;
        double h = weightHogSlider  != null ? weightHogSlider.getValue()  : wHog  * 100;
        double i = weightHistSlider != null ? weightHistSlider.getValue() : wHist * 100;
        double total = s + e + h + i;
        if (total < 1e-6) total = 1.0;
        curWSsim = s / total;
        curWEdge = e / total;
        curWHog  = h / total;
        curWHist = i / total;
        if (weightSsimLabel != null) weightSsimLabel.setText(String.format("SSIM  %3d%%", (int) Math.round(curWSsim * 100)));
        if (weightEdgeLabel != null) weightEdgeLabel.setText(String.format("Edge  %3d%%", (int) Math.round(curWEdge * 100)));
        if (weightHogLabel  != null) weightHogLabel .setText(String.format("HOG   %3d%%", (int) Math.round(curWHog  * 100)));
        if (weightHistLabel != null) weightHistLabel.setText(String.format("Hist  %3d%%", (int) Math.round(curWHist * 100)));
        if (weightStatusLabel != null) {
            String status = String.format("Weights: SSIM %d%% | Edge %d%% | HOG %d%% | Hist %d%%",
                    (int) Math.round(curWSsim * 100), (int) Math.round(curWEdge * 100),
                    (int) Math.round(curWHog * 100), (int) Math.round(curWHist * 100));
            weightStatusLabel.setText(status);
        }
    }

    // ── Called by DashboardController after FXML load ───────────────────────
    public void setSketchFile(File file) {
        this.sketchFile = file;
        if (file != null && file.exists()) {
            sketchView.setImage(new Image(file.toURI().toString()));
            sketchLabel.setText(file.getName());
            setStatus("Sketch loaded: " + file.getName() + "  —  Click COMPARE ▶ to search the dataset");
            if (compareBtn != null) compareBtn.setDisable(false);
        }
    }

    // ── Load composite sketch image ─────────────────────────────────────────
    @FXML
    private void onLoadSketch() {
        FileChooser fc = new FileChooser();
        fc.setTitle("Select Composite Sketch Image");
        fc.setInitialDirectory(new File(System.getProperty("user.home")));
        fc.getExtensionFilters().add(
                new FileChooser.ExtensionFilter("Images", "*.png", "*.jpg", "*.jpeg", "*.bmp"));
        Stage stage = (Stage) compareBtn.getScene().getWindow();
        File chosen = fc.showOpenDialog(stage);
        if (chosen != null) {
            setSketchFile(chosen);
        }
    }

    // ── Load suspect photo ───────────────────────────────────────────────────
    @FXML
    private void onLoadPhoto() {
        FileChooser fc = new FileChooser();
        fc.setTitle("Select Suspect Photo");
        fc.setInitialDirectory(new File(System.getProperty("user.home")));
        fc.getExtensionFilters().add(
                new FileChooser.ExtensionFilter("Images", "*.png", "*.jpg", "*.jpeg", "*.bmp"));
        Stage stage = (Stage) compareBtn.getScene().getWindow();
        File chosen = fc.showOpenDialog(stage);
        if (chosen != null) {
            photoFile = chosen;
            photoView.setImage(new Image(chosen.toURI().toString()));
            if (photoHint != null) photoHint.setVisible(false);
            photoLabel.setText(chosen.getName());
            setStatus("Photo loaded: " + chosen.getName() + "  —  Click COMPARE ▶");
            refreshCompareButton();
        }
    }

    // ── Run comparison in background thread ─────────────────────────────────

    /**
     * Auto-locates the suspect photo gallery folder relative to the project.
     * Checks the known dataset locations first; returns null only if none exist.
     */
    private File findGalleryFolder() {
        File[] candidates = {
            new File("ml_service/dataset"),
            new File("dataset"),
            new File(System.getProperty("user.dir") + "/ml_service/dataset"),
            new File(System.getProperty("user.dir") + "/dataset"),
            new File("ml_service/dataset/gallery"),
            new File("dataset/gallery")
        };
        for (File c : candidates) {
            if (c.isDirectory()) {
                return c;
            }
        }
        return null;
    }

    @FXML
    private void onCompare() {
        if (sketchFile == null) {
            setStatus("⚠ Load a sketch first before running a match.");
            return;
        }

        // If a single photo was uploaded, run 1-to-1 multi-metric comparison
        if (photoFile != null) {
            setStatus("🔍 Running 1-to-1 comparison...");
            compareBtn.setDisable(true);
            if (deepMatchBtn != null) deepMatchBtn.setDisable(true);

            Task<Double> task = new Task<>() {
                @Override
                protected Double call() throws Exception {
                    return computeSimilarity(sketchFile, photoFile);
                }
            };
            task.setOnSucceeded(e -> {
                compareBtn.setDisable(false);
                if (deepMatchBtn != null) deepMatchBtn.setDisable(false);
                updateResultUI(task.getValue());
                setStatus("1-to-1 comparison complete.");
            });
            task.setOnFailed(e -> {
                compareBtn.setDisable(false);
                if (deepMatchBtn != null) deepMatchBtn.setDisable(false);
                setStatus("Comparison failed: " + task.getException().getMessage());
            });
            Thread t = new Thread(task);
            t.setDaemon(true);
            t.start();
            return;
        }

        File finalDir = findGalleryFolder();
        if (finalDir == null) {
            javafx.stage.DirectoryChooser dc = new javafx.stage.DirectoryChooser();
            dc.setTitle("Select Dataset Folder of Suspect Photos");
            dc.setInitialDirectory(new File(System.getProperty("user.home")));
            finalDir = dc.showDialog(compareBtn.getScene() == null ? null : compareBtn.getScene().getWindow());
        }
        if (finalDir == null) return;
        final File datasetDir = finalDir;
        setStatus("🔍 Contacting ML service…");
        compareBtn.setDisable(true);
        if (deepMatchBtn != null) deepMatchBtn.setDisable(true);

        Task<List<DeepMatchClient.Match>> task = new Task<>() {
            @Override
            protected List<DeepMatchClient.Match> call() throws Exception {
                DeepMatchClient client = new DeepMatchClient();
                if (!client.isHealthy()) {
                    throw new IOException("ML service is not running (see ml_service/README.md).");
                }
                return client.match(sketchFile, datasetDir, 10);
            }
        };
        task.setOnSucceeded(e -> {
            List<DeepMatchClient.Match> results = task.getValue();
            compareBtn.setDisable(false);
            if (deepMatchBtn != null) deepMatchBtn.setDisable(false);
            setStatus("Compare complete — " + datasetDir.getName() + " scanned.");
            if (results.isEmpty()) {
                Alert alert = new Alert(Alert.AlertType.INFORMATION);
                alert.setTitle("Compare Results");
                alert.setHeaderText("Ranked Matches");
                alert.setContentText("No matches returned.");
                alert.showAndWait();
                return;
            }
            showMatchGrid(results, datasetDir);
        });
        task.setOnFailed(e -> {
            setStatus("Compare failed: " + task.getException().getMessage());
            compareBtn.setDisable(false);
            if (deepMatchBtn != null) deepMatchBtn.setDisable(false);
        });
        Thread t = new Thread(task);
        t.setDaemon(true);
        t.start();
    }

    /**
     * Shows the ranked matches as a grid of photo thumbnails, each with its
     * rank and similarity percentage underneath.
     */
    private void showMatchGrid(List<DeepMatchClient.Match> results, File datasetDir) {
        FlowPane grid = new FlowPane();
        grid.setHgap(16);
        grid.setVgap(16);
        grid.setPadding(new Insets(20));

        for (int i = 0; i < results.size(); i++) {
            DeepMatchClient.Match m = results.get(i);
            int pct = (int) Math.round(m.similarity * 100);
            File photo = new File(m.path != null && !m.path.isEmpty() ? m.path : "");

            VBox card = new VBox(6);
            card.setAlignment(Pos.CENTER);
            card.setStyle("-fx-background-color: #16213e; -fx-border-color: #4444aa;"
                    + "-fx-border-width: 2; -fx-border-radius: 8; -fx-background-radius: 8;"
                    + "-fx-padding: 8;");

            ImageView img = new ImageView();
            if (photo.isFile()) {
                img.setImage(new Image(photo.toURI().toString()));
            }
            img.setFitWidth(160);
            img.setFitHeight(160);
            img.setPreserveRatio(true);

            String color = pct >= 70 ? "#22c55e" : pct >= 60 ? "#3b82f6"
                        : pct >= 50 ? "#eab308" : "#ef4444";
            
            Label rank = new Label("Rank #" + (i + 1) + " • " + (m.matchTier != null ? m.matchTier : "MATCH"));
            rank.setStyle("-fx-text-fill: " + color + "; -fx-font-size: 11px; -fx-font-weight: bold;");
            
            Label name = new Label(m.name);
            name.setStyle("-fx-text-fill: #ffffff; -fx-font-size: 13px; -fx-font-weight: bold;");
            
            Label sim = new Label(pct + "% Match Score");
            sim.setStyle("-fx-text-fill: " + color + "; -fx-font-size: 16px; -fx-font-weight: bold;");

            Label breakdown = new Label(String.format("Deep: %d%% | HOG: %d%% | LBP: %d%%",
                    (int) Math.round(m.deepScore * 100),
                    (int) Math.round(m.hogScore * 100),
                    (int) Math.round(m.lbpScore * 100)));
            breakdown.setStyle("-fx-text-fill: #8899ac; -fx-font-size: 10px;");

            card.getChildren().addAll(img, rank, name, sim, breakdown);
            grid.getChildren().add(card);
        }

        ScrollPane scroll = new ScrollPane(grid);
        scroll.setFitToWidth(true);
        scroll.setStyle("-fx-background: #1a1a2e; -fx-background-color: #1a1a2e;");

        Dialog<Void> dialog = new Dialog<>();
        dialog.setTitle("Compare Results — " + datasetDir.getName());
        dialog.setHeaderText("Top Matches with Similarity %");
        dialog.getDialogPane().setPrefSize(760, 520);
        dialog.getDialogPane().setStyle("-fx-background-color: #1a1a2e;");
        ButtonType close = new ButtonType("Close", ButtonBar.ButtonData.OK_DONE);
        dialog.getDialogPane().getButtonTypes().add(close);
        dialog.getDialogPane().setContent(scroll);
        dialog.showAndWait();
    }

    // ═══════════════════════════════════════════════════════════════════════════
    //  CORE COMPARISON ALGORITHM — Enhanced Multi-Metric Fusion (pure Java)
    // ═══════════════════════════════════════════════════════════════════════════

    private double computeSimilarity(File sketchF, File photoF) throws Exception {
        BufferedImage rawSketch = ImageIO.read(sketchF);
        BufferedImage rawPhoto  = ImageIO.read(photoF);

        if (rawSketch == null || rawPhoto == null)
            throw new Exception("Could not read one or both image files.");

        // 1. Resize to fixed square — preserving aspect ratio with padding
        BufferedImage sketch = resizePreserveAspect(rawSketch, COMPARE_SIZE);
        BufferedImage photo  = resizePreserveAspect(rawPhoto,  COMPARE_SIZE);

        // 2. Convert to greyscale int arrays
        int[] sGrey = toGreyscale(sketch);
        int[] pGrey = toGreyscale(photo);

        // 3. Histogram equalisation (normalise brightness/contrast)
        sGrey = histogramEqualise(sGrey);
        pGrey = histogramEqualise(pGrey);

        // 4. Face region weight map — emphasises central features
        double[][] wMap = getFaceWeightMap();

        // 5. SSIM — Structural Similarity Index (perceptual quality)
        lastSsimScore = computeSSIM(sGrey, pGrey, COMPARE_SIZE, COMPARE_SIZE, wMap);

        // 6. Sobel edge detection → edge map correlation (sketch↔photo bridge)
        int[] sEdges = sobelEdgeDetect(sGrey, COMPARE_SIZE, COMPARE_SIZE);
        int[] pEdges = sobelEdgeDetect(pGrey, COMPARE_SIZE, COMPARE_SIZE);
        lastEdgeScore = computeWeightedCorrelation(sEdges, pEdges, wMap);

        // 7. HOG — Histogram of Oriented Gradients (shape/contour matching)
        double[] hogSketch = computeHOG(sGrey, COMPARE_SIZE, COMPARE_SIZE, wMap);
        double[] hogPhoto  = computeHOG(pGrey, COMPARE_SIZE, COMPARE_SIZE, wMap);
        lastHogScore = cosineSimilarity(hogSketch, hogPhoto);

        // 8. Histogram intersection (tonal distribution overlap)
        lastHistScore = computeHistogramIntersection(sGrey, pGrey);

        // 9. Weighted multi-metric fusion (dynamic weights from sliders)
        double combined = (lastSsimScore * curWSsim)
                         + (lastEdgeScore * curWEdge)
                         + (lastHogScore  * curWHog)
                         + (lastHistScore * curWHist);

        return Math.min(1.0, Math.max(0.0, combined));
    }

    // ═══════════════════════════════════════════════════════════════════════════
    //  IMAGE PRE-PROCESSING
    // ═══════════════════════════════════════════════════════════════════════════

    /**
     * Resize to target square dimensions, preserving aspect ratio.
     * The image is scaled to fit inside the square, then centred on a white background.
     * This avoids facial distortion caused by squashing non-square images.
     */
    private BufferedImage resizePreserveAspect(BufferedImage src, int maxDim) {
        double scale = Math.min((double) maxDim / src.getWidth(),
                                (double) maxDim / src.getHeight());
        int w = (int) (src.getWidth()  * scale);
        int h = (int) (src.getHeight() * scale);

        BufferedImage out = new BufferedImage(maxDim, maxDim, BufferedImage.TYPE_INT_RGB);
        Graphics2D g = out.createGraphics();
        g.setRenderingHint(RenderingHints.KEY_INTERPOLATION,
                           RenderingHints.VALUE_INTERPOLATION_BILINEAR);
        g.setRenderingHint(RenderingHints.KEY_ANTIALIASING,
                           RenderingHints.VALUE_ANTIALIAS_ON);
        // White background padding
        g.setColor(Color.WHITE);
        g.fillRect(0, 0, maxDim, maxDim);
        // Centre the scaled image
        g.drawImage(src, (maxDim - w) / 2, (maxDim - h) / 2, w, h, null);
        g.dispose();
        return out;
    }

    /**
     * Convert ARGB image to greyscale pixel array (0–255).
     * Uses luminosity formula matching human eye sensitivity.
     */
    private int[] toGreyscale(BufferedImage img) {
        int n = img.getWidth() * img.getHeight();
        int[] grey = new int[n];
        int idx = 0;
        for (int y = 0; y < img.getHeight(); y++) {
            for (int x = 0; x < img.getWidth(); x++) {
                Color c = new Color(img.getRGB(x, y));
                // Luminosity formula — matches human eye sensitivity
                grey[idx++] = (int)(0.299 * c.getRed()
                                  + 0.587 * c.getGreen()
                                  + 0.114 * c.getBlue());
            }
        }
        return grey;
    }

    /**
     * Histogram equalisation — redistributes pixel intensities for fair comparison.
     * Normalises brightness and contrast differences between sketch and photograph.
     */
    private int[] histogramEqualise(int[] pixels) {
        int[] hist  = new int[256];
        for (int p : pixels) hist[p]++;

        int[] cdf = new int[256];
        cdf[0] = hist[0];
        for (int i = 1; i < 256; i++) cdf[i] = cdf[i-1] + hist[i];

        int cdfMin = 0;
        for (int i = 0; i < 256; i++) { if (cdf[i] > 0) { cdfMin = cdf[i]; break; } }
        int n = pixels.length;

        int[] out = new int[pixels.length];
        for (int i = 0; i < pixels.length; i++) {
            out[i] = Math.round((float)(cdf[pixels[i]] - cdfMin) / (n - cdfMin) * 255);
            out[i] = Math.min(255, Math.max(0, out[i]));
        }
        return out;
    }

    // ═══════════════════════════════════════════════════════════════════════════
    //  METRIC 1: SSIM — Structural Similarity Index
    // ═══════════════════════════════════════════════════════════════════════════

    /**
     * Computes Structural Similarity Index (SSIM) between two greyscale images.
     * Unlike RMSE, SSIM considers luminance, contrast, and structure independently,
     * making it far more robust to minor alignment differences.
     *
     * Based on: Wang, Bovik, Sheikh & Simoncelli (2004).
     */
    private double computeSSIM(int[] a, int[] b, int width, int height, double[][] weightMap) {
        double totalSsim = 0;
        double totalWeight = 0;

        int halfW = SSIM_WINDOW / 2;
        double[] gaussKernel = getSsimGaussianKernel();

        // Slide an 8×8 window across the image
        for (int y = 0; y <= height - SSIM_WINDOW; y += SSIM_WINDOW) {
            for (int x = 0; x <= width - SSIM_WINDOW; x += SSIM_WINDOW) {

                // Gaussian-weighted means
                double muA = 0, muB = 0;
                for (int dy = 0; dy < SSIM_WINDOW; dy++) {
                    for (int dx = 0; dx < SSIM_WINDOW; dx++) {
                        double g = gaussKernel[dy * SSIM_WINDOW + dx];
                        int idx = (y + dy) * width + (x + dx);
                        muA += g * a[idx];
                        muB += g * b[idx];
                    }
                }
                muA /= ssimGaussianSum;
                muB /= ssimGaussianSum;

                // Gaussian-weighted variances and covariance
                double sigAA = 0, sigBB = 0, sigAB = 0;
                for (int dy = 0; dy < SSIM_WINDOW; dy++) {
                    for (int dx = 0; dx < SSIM_WINDOW; dx++) {
                        double g = gaussKernel[dy * SSIM_WINDOW + dx];
                        int idx = (y + dy) * width + (x + dx);
                        double da = a[idx] - muA;
                        double db = b[idx] - muB;
                        sigAA += g * da * da;
                        sigBB += g * db * db;
                        sigAB += g * da * db;
                    }
                }
                sigAA /= ssimGaussianSum;
                sigBB /= ssimGaussianSum;
                sigAB /= ssimGaussianSum;

                // SSIM formula
                double numerator   = (2 * muA * muB + SSIM_C1) * (2 * sigAB + SSIM_C2);
                double denominator = (muA * muA + muB * muB + SSIM_C1) * (sigAA + sigBB + SSIM_C2);

                // Block weight from center pixel in face region weight map
                int cx = Math.min(x + halfW, width - 1);
                int cy = Math.min(y + halfW, height - 1);
                double w = weightMap[cy][cx];

                totalSsim += w * (numerator / denominator);
                totalWeight += w;
            }
        }

        return totalWeight > 0 ? Math.max(0, totalSsim / totalWeight) : 0;
    }

    // ═══════════════════════════════════════════════════════════════════════════
    //  METRIC 2: Sobel Edge Detection + Edge Map Correlation
    // ═══════════════════════════════════════════════════════════════════════════

    /**
     * Applies Sobel edge detection to a greyscale image.
     * This is the single most important enhancement for sketch↔photo comparison,
     * because sketches are fundamentally edge-based representations.
     * By comparing edge maps instead of raw pixels, we bridge the domain gap.
     */
    private int[] sobelEdgeDetect(int[] grey, int width, int height) {
        int[] edges = new int[width * height];

        // Sobel kernels
        // Gx: [-1 0 +1]    Gy: [-1 -2 -1]
        //     [-2 0 +2]        [ 0  0  0]
        //     [-1 0 +1]        [+1 +2 +1]

        for (int y = 1; y < height - 1; y++) {
            for (int x = 1; x < width - 1; x++) {
                // Horizontal gradient (Gx)
                int gx = -grey[(y-1)*width + (x-1)] + grey[(y-1)*width + (x+1)]
                       - 2*grey[y*width + (x-1)]     + 2*grey[y*width + (x+1)]
                       - grey[(y+1)*width + (x-1)]   + grey[(y+1)*width + (x+1)];

                // Vertical gradient (Gy)
                int gy = -grey[(y-1)*width + (x-1)] - 2*grey[(y-1)*width + x] - grey[(y-1)*width + (x+1)]
                       + grey[(y+1)*width + (x-1)] + 2*grey[(y+1)*width + x] + grey[(y+1)*width + (x+1)];

                // Gradient magnitude
                int mag = (int) Math.sqrt(gx * gx + gy * gy);
                edges[y * width + x] = Math.min(255, mag);
            }
        }
        return edges;
    }

    /**
     * Weighted normalised cross-correlation between two edge maps.
     * Pixels in the face region (higher weight) contribute more to the score.
     * Returns a value in [0, 1] where 1 means identical patterns.
     */
    private double computeWeightedCorrelation(int[] a, int[] b, double[][] weightMap) {
        int width = COMPARE_SIZE;
        int height = COMPARE_SIZE;
        double totalWeight = 0;

        // Compute weighted means
        double meanA = 0, meanB = 0;
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                double w = weightMap[y][x];
                int idx = y * width + x;
                meanA += w * a[idx];
                meanB += w * b[idx];
                totalWeight += w;
            }
        }
        if (totalWeight < 1e-10) return 0;
        meanA /= totalWeight;
        meanB /= totalWeight;

        // Weighted cross-correlation and variances
        double sumAB = 0, sumAA = 0, sumBB = 0;
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                double w = weightMap[y][x];
                int idx = y * width + x;
                double da = a[idx] - meanA;
                double db = b[idx] - meanB;
                sumAB += w * da * db;
                sumAA += w * da * da;
                sumBB += w * db * db;
            }
        }

        double denom = Math.sqrt(sumAA * sumBB);
        if (denom < 1e-10) return 0;

        double ncc = sumAB / denom;
        return (ncc + 1.0) / 2.0;
    }

    // ═══════════════════════════════════════════════════════════════════════════
    //  METRIC 3: HOG — Histogram of Oriented Gradients
    // ═══════════════════════════════════════════════════════════════════════════

    /**
     * Computes HOG (Histogram of Oriented Gradients) feature descriptor.
     * HOG captures local shape and contour information by computing gradient
     * orientation histograms over cells. It's a standard feature for face
     * recognition — far more discriminative than global pixel histograms.
     *
     * Based on: Dalal & Triggs (2005).
     */
    private double[] computeHOG(int[] grey, int width, int height, double[][] weightMap) {
        int cellsX = width  / HOG_CELL_SIZE;
        int cellsY = height / HOG_CELL_SIZE;
        double[] descriptor = new double[cellsX * cellsY * HOG_NUM_BINS];

        for (int cy = 0; cy < cellsY; cy++) {
            for (int cx = 0; cx < cellsX; cx++) {
                double[] cellHist = new double[HOG_NUM_BINS];

                for (int dy = 0; dy < HOG_CELL_SIZE; dy++) {
                    for (int dx = 0; dx < HOG_CELL_SIZE; dx++) {
                        int y = cy * HOG_CELL_SIZE + dy;
                        int x = cx * HOG_CELL_SIZE + dx;

                        // Skip border pixels
                        if (x <= 0 || x >= width - 1 || y <= 0 || y >= height - 1) continue;

                        // Compute gradient using central differences
                        double gx = grey[y * width + (x + 1)] - grey[y * width + (x - 1)];
                        double gy = grey[(y + 1) * width + x] - grey[(y - 1) * width + x];

                        double magnitude = Math.sqrt(gx * gx + gy * gy);
                        // Angle in [0, 180) — unsigned gradient
                        double angle = Math.toDegrees(Math.atan2(gy, gx));
                        if (angle < 0) angle += 180;
                        if (angle >= 180) angle = 0;

                        // Bilinear interpolation into histogram bins
                        double binWidth = 180.0 / HOG_NUM_BINS;
                        double binIdx   = angle / binWidth;
                        int    bin0     = ((int) binIdx) % HOG_NUM_BINS;
                        int    bin1     = (bin0 + 1) % HOG_NUM_BINS;
                        double frac     = binIdx - (int) binIdx;

                        cellHist[bin0] += magnitude * (1 - frac);
                        cellHist[bin1] += magnitude * frac;
                    }
                }

                // Weight cell histogram by its position in the face weight map
                double cellWeight = weightMap[cy * HOG_CELL_SIZE + HOG_CELL_SIZE / 2]
                                             [cx * HOG_CELL_SIZE + HOG_CELL_SIZE / 2];
                int offset = (cy * cellsX + cx) * HOG_NUM_BINS;
                for (int b = 0; b < HOG_NUM_BINS; b++) {
                    descriptor[offset + b] = cellHist[b] * cellWeight;
                }
            }
        }

        // L2 normalisation of the full descriptor
        double norm = 0;
        for (double v : descriptor) norm += v * v;
        norm = Math.sqrt(norm);
        if (norm > 1e-10) {
            for (int i = 0; i < descriptor.length; i++) descriptor[i] /= norm;
        }

        return descriptor;
    }

    /**
     * Cosine similarity between two vectors.
     * Returns a value in [0, 1] where 1 means identical direction.
     * Ideal for comparing high-dimensional feature descriptors like HOG.
     */
    private double cosineSimilarity(double[] a, double[] b) {
        double dot = 0, normA = 0, normB = 0;
        int len = Math.min(a.length, b.length);
        for (int i = 0; i < len; i++) {
            dot   += a[i] * b[i];
            normA += a[i] * a[i];
            normB += b[i] * b[i];
        }
        double denom = Math.sqrt(normA) * Math.sqrt(normB);
        if (denom < 1e-10) return 0;
        // Clamp to [0, 1] — cosine of normalised vectors should already be ≥ 0
        return Math.max(0, Math.min(1, dot / denom));
    }

    // ═══════════════════════════════════════════════════════════════════════════
    //  METRIC 4: Histogram Intersection
    // ═══════════════════════════════════════════════════════════════════════════

    /**
     * Histogram intersection: how much the two intensity histograms overlap.
     * Measures global tonal similarity — whether the images have similar
     * brightness distributions. Least discriminative metric but adds robustness.
     */
    private double computeHistogramIntersection(int[] a, int[] b) {
        int[] hA = new int[256], hB = new int[256];
        for (int v : a) hA[v]++;
        for (int v : b) hB[v]++;

        double intersection = 0;
        for (int i = 0; i < 256; i++) {
            intersection += Math.min(hA[i], hB[i]);
        }
        return intersection / a.length; // normalised 0..1
    }

    // ═══════════════════════════════════════════════════════════════════════════
    //  UI — Result Display (5-tier confidence system)
    // ═══════════════════════════════════════════════════════════════════════════

    private void updateResultUI(double sim) {
        Platform.runLater(() -> {
            int pct = (int) Math.round(sim * 100);
            percentLabel.setText(pct + "%");
            progressBar.setProgress(sim);

            // Build metric breakdown string for display
            String metrics = String.format(
                "SSIM: %d%% | Edge: %d%%\nHOG: %d%% | Hist: %d%%",
                Math.round(lastSsimScore * 100),
                Math.round(lastEdgeScore * 100),
                Math.round(lastHogScore  * 100),
                Math.round(lastHistScore * 100));

            if (sim >= STRONG_MATCH) {
                resultLabel.setText("✅  STRONG MATCH\nVery high confidence — suspect identity likely confirmed.\n" + metrics);
                resultLabel.setStyle("-fx-text-fill: #22c55e; -fx-font-weight: bold; -fx-font-size: 13px; -fx-text-alignment: CENTER;");
                progressBar.setStyle("-fx-accent: #22c55e;");
                setStatus("🎯 STRONG MATCH — " + pct + "% similarity (≥90% threshold).");
            } else if (sim >= LIKELY_MATCH) {
                resultLabel.setText("🔵  LIKELY MATCH\nHigh confidence — strong resemblance detected.\n" + metrics);
                resultLabel.setStyle("-fx-text-fill: #3b82f6; -fx-font-weight: bold; -fx-font-size: 13px; -fx-text-alignment: CENTER;");
                progressBar.setStyle("-fx-accent: #3b82f6;");
                setStatus("🔵 LIKELY MATCH — " + pct + "% similarity (≥75% threshold).");
            } else if (sim >= POSSIBLE_MATCH) {
                resultLabel.setText("⚠  POSSIBLE MATCH\nModerate confidence — requires further investigation.\n" + metrics);
                resultLabel.setStyle("-fx-text-fill: #eab308; -fx-font-weight: bold; -fx-font-size: 13px; -fx-text-alignment: CENTER;");
                progressBar.setStyle("-fx-accent: #eab308;");
                setStatus("⚠ POSSIBLE MATCH — " + pct + "% similarity (≥60% threshold).");
            } else if (sim >= UNLIKELY_MATCH) {
                resultLabel.setText("🟠  UNLIKELY MATCH\nLow confidence — minimal resemblance.\n" + metrics);
                resultLabel.setStyle("-fx-text-fill: #f97316; -fx-font-weight: bold; -fx-font-size: 13px; -fx-text-alignment: CENTER;");
                progressBar.setStyle("-fx-accent: #f97316;");
                setStatus("🟠 UNLIKELY MATCH — " + pct + "% similarity (below 60% threshold).");
            } else {
                resultLabel.setText("❌  NO MATCH\nSuspect does not match the sketch.\n" + metrics);
                resultLabel.setStyle("-fx-text-fill: #ef4444; -fx-font-weight: bold; -fx-font-size: 13px; -fx-text-alignment: CENTER;");
                progressBar.setStyle("-fx-accent: #ef4444;");
                setStatus("❌ NO MATCH — " + pct + "% similarity is well below threshold.");
            }
        });
    }

    // ═══════════════════════════════════════════════════════════════════════════
    //  Report Generation — Enhanced Forensic Report
    // ═══════════════════════════════════════════════════════════════════════════

    @FXML
    private void onSaveReport() {
        FileChooser fc = new FileChooser();
        fc.setTitle("Save Forensic Report");
        fc.setInitialDirectory(new File(System.getProperty("user.home")));
        fc.setInitialFileName("ThirdEye_Report_" +
                new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date()) + ".txt");
        fc.getExtensionFilters().add(new FileChooser.ExtensionFilter("Text Files", "*.txt"));
        Stage stage = (Stage) compareBtn.getScene().getWindow();
        File out = fc.showSaveDialog(stage);
        if (out != null) {
            try (FileWriter fw = new FileWriter(out)) {
                int pct = (int) Math.round(lastSimilarity * 100);
                String verdict = getVerdict(lastSimilarity);
                String timestamp = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date());

                fw.write("══════════════════════════════════════════════════════\n");
                fw.write("        ThirdEye — Enhanced Forensic Report\n");
                fw.write("══════════════════════════════════════════════════════\n");
                fw.write("Date       : " + timestamp + "\n");
                fw.write("Analyst    : Mallikarjun Gala\n");
                fw.write("Algorithm  : Multi-Metric Fusion v2 (Enhanced)\n");
                fw.write("──────────────────────────────────────────────────────\n");
                fw.write("Sketch     : " + (sketchFile != null ? sketchFile.getAbsolutePath() : "N/A") + "\n");
                fw.write("Photo      : " + (photoFile  != null ? photoFile.getAbsolutePath()  : "N/A") + "\n");
                fw.write("──────────────────────────────────────────────────────\n");
                fw.write("\n");
                fw.write("                    RESULTS\n");
                fw.write("\n");
                fw.write("  Overall Similarity : " + pct + "%\n");
                fw.write("  VERDICT            : " + verdict + "\n");
                fw.write("\n");
                fw.write("──────────────────────────────────────────────────────\n");
                fw.write("\n");
                fw.write("              METRIC BREAKDOWN\n");
                fw.write("\n");
                fw.write("  SSIM  (Structural Similarity)  : " + Math.round(lastSsimScore * 100) + "%  (weight " + (int)(curWSsim*100) + "%)\n");
                fw.write("  EDGE  (Sobel Edge Correlation) : " + Math.round(lastEdgeScore * 100) + "%  (weight " + (int)(curWEdge*100) + "%)\n");
                fw.write("  HOG   (Shape/Contour Features) : " + Math.round(lastHogScore  * 100) + "%  (weight " + (int)(curWHog*100)  + "%)\n");
                fw.write("  HIST  (Histogram Intersection) : " + Math.round(lastHistScore * 100) + "%  (weight " + (int)(curWHist*100) + "%)\n");
                fw.write("\n");
                fw.write("──────────────────────────────────────────────────────\n");
                fw.write("\n");
                fw.write("              CONFIDENCE THRESHOLDS\n");
                fw.write("\n");
                fw.write("  ≥ 90%  STRONG MATCH    — Very high confidence\n");
                fw.write("  ≥ 75%  LIKELY MATCH    — High confidence\n");
                fw.write("  ≥ 60%  POSSIBLE MATCH  — Moderate confidence\n");
                fw.write("  ≥ 40%  UNLIKELY MATCH  — Low confidence\n");
                fw.write("  < 40%  NO MATCH        — Not a match\n");
                fw.write("\n");
                fw.write("══════════════════════════════════════════════════════\n");
                fw.write("  Generated by ThirdEye Enhanced Comparison Engine\n");
                fw.write("══════════════════════════════════════════════════════\n");
                setStatus("✅ Report saved: " + out.getAbsolutePath());
            } catch (IOException e) {
                setStatus("❌ Could not save report: " + e.getMessage());
                Logger.getLogger(Upload_sketchController.class.getName()).log(Level.SEVERE, null, e);
            }
        }
    }

    /**
     * Returns a human-readable verdict string based on the similarity score.
     */
    private String getVerdict(double sim) {
        if (sim >= STRONG_MATCH)   return "STRONG MATCH";
        if (sim >= LIKELY_MATCH)   return "LIKELY MATCH";
        if (sim >= POSSIBLE_MATCH) return "POSSIBLE MATCH";
        if (sim >= UNLIKELY_MATCH) return "UNLIKELY MATCH";
        return "NO MATCH";
    }

    // ═══════════════════════════════════════════════════════════════════════════
    //  Utility Methods
    // ═══════════════════════════════════════════════════════════════════════════

    private void refreshCompareButton() {
        compareBtn.setDisable(sketchFile == null);
    }

    private void setStatus(String msg) {
        Platform.runLater(() -> statusBar.setText(msg));
    }

    // ═══════════════════════════════════════════════════════════════════════════
    //  Suspect Gallery — one-to-many search with SQLite persistence
    // ═══════════════════════════════════════════════════════════════════════════

    private double[] computeHogForFile(File imageFile) throws Exception {
        BufferedImage img = ImageIO.read(imageFile);
        if (img == null) throw new Exception("Cannot read " + imageFile.getName());
        BufferedImage resized = resizePreserveAspect(img, COMPARE_SIZE);
        int[] grey = toGreyscale(resized);
        grey = histogramEqualise(grey);
        return computeHOG(grey, COMPARE_SIZE, COMPARE_SIZE, getFaceWeightMap());
    }

    @FXML
    private void onAddToGallery() {
        if (photoFile == null) {
            setStatus("Load a suspect photo first before adding to gallery.");
            return;
        }
        TextInputDialog dialog = new TextInputDialog("");
        dialog.setTitle("Add Suspect to Gallery");
        dialog.setHeaderText("Enter suspect details");
        dialog.setContentText("Suspect name:");
        dialog.showAndWait().ifPresent(name -> {
            if (name.trim().isEmpty()) {
                setStatus("Suspect name cannot be empty.");
                return;
            }
            setStatus("Indexing suspect into gallery...");
            Task<Void> task = new Task<>() {
                @Override
                protected Void call() throws Exception {
                    BufferedImage img = ImageIO.read(photoFile);
                    double[] hog = computeHogForFile(photoFile);
                    SuspectDatabase.addSuspect(name.trim(), "", img, hog);
                    return null;
                }
            };
            task.setOnSucceeded(e -> setStatus("Added \"" + name + "\" to suspect gallery."));
            task.setOnFailed(e -> setStatus("Failed to add suspect: " + task.getException().getMessage()));
            Thread t = new Thread(task);
            t.setDaemon(true);
            t.start();
        });
    }

    @FXML
    private void onSearchGallery() {
        if (sketchFile == null) {
            setStatus("Load a sketch first before searching the gallery.");
            return;
        }
        setStatus("Searching gallery...");
        compareBtn.setDisable(true);

        Task<String> task = new Task<>() {
            @Override
            protected String call() throws Exception {
                double[] sketchHog = computeHogForFile(sketchFile);
                List<SuspectDatabase.SuspectRecord> suspects = SuspectDatabase.getAllSuspects();
                if (suspects.isEmpty()) {
                    return "Gallery is empty. Add suspects first.";
                }

                BufferedImage rawSketch = ImageIO.read(sketchFile);
                BufferedImage sketchResized = resizePreserveAspect(rawSketch, COMPARE_SIZE);
                int[] sGrey = toGreyscale(sketchResized);
                sGrey = histogramEqualise(sGrey);
                int[] sEdges = sobelEdgeDetect(sGrey, COMPARE_SIZE, COMPARE_SIZE);
                double[][] wMap = getFaceWeightMap();

                StringBuilder sb = new StringBuilder();
                sb.append("═══════════════════════════════════════════════\n");
                sb.append("    GALLERY SEARCH RESULTS (ranked)\n");
                sb.append("═══════════════════════════════════════════════\n\n");

                // Collect results
                List<GalleryResult> results = new java.util.ArrayList<>();
                for (SuspectDatabase.SuspectRecord suspect : suspects) {
                    if (suspect.image == null) continue;

                    BufferedImage photoResized = resizePreserveAspect(suspect.image, COMPARE_SIZE);
                    int[] pGrey = toGreyscale(photoResized);
                    pGrey = histogramEqualise(pGrey);

                    double ssim = computeSSIM(sGrey, pGrey, COMPARE_SIZE, COMPARE_SIZE, wMap);
                    int[] pEdges = sobelEdgeDetect(pGrey, COMPARE_SIZE, COMPARE_SIZE);
                    double edge = computeWeightedCorrelation(sEdges, pEdges, wMap);
                    double hogSim;
                    if (suspect.hogDescriptor != null) {
                        hogSim = cosineSimilarity(sketchHog, suspect.hogDescriptor);
                    } else {
                        double[] pHog = computeHOG(pGrey, COMPARE_SIZE, COMPARE_SIZE, wMap);
                        hogSim = cosineSimilarity(sketchHog, pHog);
                    }
                    double hist = computeHistogramIntersection(sGrey, pGrey);
                    double combined = ssim * curWSsim + edge * curWEdge + hogSim * curWHog + hist * curWHist;
                    combined = Math.min(1.0, Math.max(0.0, combined));

                    GalleryResult gr = new GalleryResult();
                    gr.name = suspect.name;
                    gr.caseId = suspect.caseId;
                    gr.similarity = combined;
                    gr.ssim = ssim;
                    gr.edge = edge;
                    gr.hog = hogSim;
                    gr.hist = hist;
                    results.add(gr);
                }

                results.sort((a, b) -> Double.compare(b.similarity, a.similarity));

                for (int i = 0; i < results.size(); i++) {
                    GalleryResult r = results.get(i);
                    int pct = (int) Math.round(r.similarity * 100);
                    String badge = pct >= 90 ? "STRONG" : pct >= 75 ? "LIKELY" : pct >= 60 ? "POSSIBLE" : pct >= 40 ? "UNLIKELY" : "NO MATCH";
                    String caseStr = (r.caseId != null && !r.caseId.isEmpty()) ? " [" + r.caseId + "]" : "";
                    sb.append(String.format("  #%d  %-20s%s  %3d%%  (%s)\n", i + 1, r.name, caseStr, pct, badge));
                    sb.append(String.format("       SSIM:%3d%% Edge:%3d%% HOG:%3d%% Hist:%3d%%\n",
                            Math.round(r.ssim * 100), Math.round(r.edge * 100),
                            Math.round(r.hog * 100), Math.round(r.hist * 100)));
                    sb.append("\n");
                }
                sb.append("═══════════════════════════════════════════════\n");
                sb.append(results.size() + " suspects compared.\n");
                return sb.toString();
            }
        };

        task.setOnSucceeded(e -> {
            String result = task.getValue();
            Alert alert = new Alert(Alert.AlertType.INFORMATION);
            alert.setTitle("Gallery Search Results");
            alert.setHeaderText("Ranked Suspect List");
            alert.getDialogPane().setPrefWidth(520);
            alert.getDialogPane().setPrefHeight(400);
            javafx.scene.control.TextArea ta = new javafx.scene.control.TextArea(result);
            ta.setEditable(false);
            ta.setStyle("-fx-font-family: monospace; -fx-font-size: 12px;");
            alert.getDialogPane().setContent(ta);
            alert.showAndWait();
            compareBtn.setDisable(false);
            setStatus("Gallery search complete.");
        });

        task.setOnFailed(e -> {
            setStatus("Gallery search failed: " + task.getException().getMessage());
            compareBtn.setDisable(false);
        });

        Thread t = new Thread(task);
        t.setDaemon(true);
        t.start();
    }

    // ── Deep learning dataset match (Python ML service) ──────────────────────
    @FXML
    private void onDeepMatch(ActionEvent event) {
        if (sketchFile == null) {
            setStatus("Load a sketch first before running a dataset match.");
            return;
        }
        javafx.stage.DirectoryChooser dc = new javafx.stage.DirectoryChooser();
        dc.setTitle("Select Dataset Folder of Suspect Photos");
        dc.setInitialDirectory(new File(System.getProperty("user.home")));
        File datasetDir = dc.showDialog(compareBtn.getScene() == null ? null : compareBtn.getScene().getWindow());
        if (datasetDir == null) return;

        final File finalDir = datasetDir;
        setStatus("Contacting ML service…");
        compareBtn.setDisable(true);
        deepMatchBtn.setDisable(true);

        Task<String> task = new Task<>() {
            @Override
            protected String call() throws Exception {
                DeepMatchClient client = new DeepMatchClient();
                if (!client.isHealthy()) {
                    throw new IOException("ML service is not running (see ml_service/README.md).");
                }
                List<DeepMatchClient.Match> results = client.match(sketchFile, finalDir, 10);
                if (results.isEmpty()) return "No matches returned.";
                StringBuilder sb = new StringBuilder();
                sb.append("═══════════════════════════════════════════════\n");
                sb.append("    DEEP MATCH RESULTS (FaceNet embeddings)\n");
                sb.append("═══════════════════════════════════════════════\n\n");
                for (int i = 0; i < results.size(); i++) {
                    DeepMatchClient.Match m = results.get(i);
                    int pct = (int) Math.round(m.similarity * 100);
                    sb.append(String.format("  #%d  %-24s  %3d%%%n", i + 1, m.name, pct));
                    sb.append("       " + m.path + "\n\n");
                }
                sb.append(results.size() + " candidates compared.");
                return sb.toString();
            }
        };
        task.setOnSucceeded(e -> {
            Alert alert = new Alert(Alert.AlertType.INFORMATION);
            alert.setTitle("Deep Match Results");
            alert.setHeaderText("ML Dataset Match");
            alert.getDialogPane().setPrefWidth(560);
            alert.getDialogPane().setPrefHeight(420);
            javafx.scene.control.TextArea ta = new javafx.scene.control.TextArea(task.getValue());
            ta.setEditable(false);
            ta.setStyle("-fx-font-family: monospace; -fx-font-size: 12px;");
            alert.getDialogPane().setContent(ta);
            alert.showAndWait();
            compareBtn.setDisable(false);
            deepMatchBtn.setDisable(false);
            setStatus("Deep match complete.");
        });
        task.setOnFailed(e -> {
            setStatus("Deep match failed: " + task.getException().getMessage());
            compareBtn.setDisable(false);
            deepMatchBtn.setDisable(false);
        });
        Thread t = new Thread(task);
        t.setDaemon(true);
        t.start();
    }

    @FXML
    private void onOpenGallery() {
        try {
            FXMLLoader fxmlLoader = new FXMLLoader();
            fxmlLoader.setLocation(getClass().getResource("gallery_manager.fxml"));
            Scene scene = new Scene(fxmlLoader.load());
            GalleryManagerController ctrl = fxmlLoader.getController();
            ctrl.setPhotoCallback(tmpFile -> {
                Platform.runLater(() -> {
                    photoFile = tmpFile;
                    photoView.setImage(new Image(tmpFile.toURI().toString()));
                    if (photoHint != null) photoHint.setVisible(false);
                    photoLabel.setText(tmpFile.getName());
                    setStatus("Photo loaded from gallery: " + tmpFile.getName() + " — Click COMPARE ▶");
                    refreshCompareButton();
                });
            });
            Stage stage = new Stage();
            stage.setTitle("Suspect Gallery Manager");
            stage.setScene(scene);
            stage.setResizable(true);
            stage.show();
        } catch (IOException e) {
            Logger.getLogger(getClass().getName()).log(Level.SEVERE, null, e);
            setStatus("Could not open gallery: " + e.getMessage());
        }
    }

    private static class GalleryResult {
        String name;
        String caseId;
        double similarity;
        double ssim;
        double edge;
        double hog;
        double hist;
    }

    // ═══════════════════════════════════════════════════════════════════════════
    //  Navigation
    // ═══════════════════════════════════════════════════════════════════════════

    @FXML
    private void onBack(ActionEvent event) {
        try {
            FXMLLoader fxmlLoader = new FXMLLoader();
            fxmlLoader.setLocation(getClass().getResource("dashboard.fxml"));
            Scene scene = new Scene(fxmlLoader.load());
            Stage stage = new Stage();
            stage.setTitle("ThirdEye Workspace");
            stage.setScene(scene);
            stage.setResizable(true);
            stage.setMaximized(true);
            stage.show();
            // Hide the current compare window
            ((Node)(event.getSource())).getScene().getWindow().hide();
        } catch (IOException e) {
            Logger.getLogger(getClass().getName()).log(Level.SEVERE, null, e);
        }
    }
}
