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
import java.util.ResourceBundle;
import java.util.logging.Level;
import java.util.logging.Logger;
import javafx.application.Platform;
import javafx.concurrent.Task;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.ProgressBar;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.stage.FileChooser;
import javafx.stage.Stage;
import javax.imageio.ImageIO;

/**
 * Forensic Face Comparison Controller.
 * Uses pure Java image analysis (no external libraries).
 * Match threshold: 85% for high-accuracy results.
 *
 * Algorithm:
 *   1. Resize both images to 256×256
 *   2. Convert to grayscale
 *   3. Apply histogram equalisation (normalises lighting differences)
 *   4. Compute structural similarity score (SSIM-style RMSE)
 *   5. Compute histogram intersection score
 *   6. Weighted average → final similarity %
 *
 * @author Mallikarjun Gala
 */
public class Upload_sketchController implements Initializable {

    // ── Match threshold: 85% for high accuracy ──────────────────────────────
    private static final double MATCH_THRESHOLD = 0.85;
    private static final int    COMPARE_SIZE    = 256;

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

    private File   sketchFile;
    private File   photoFile;
    private double lastSimilarity = 0;

    @Override
    public void initialize(URL url, ResourceBundle rb) {
        compareBtn.setDisable(true);
        saveResultBtn.setDisable(true);
    }

    // ── Called by DashboardController after FXML load ───────────────────────
    public void setSketchFile(File file) {
        this.sketchFile = file;
        if (file != null && file.exists()) {
            sketchView.setImage(new Image(file.toURI().toString()));
            sketchLabel.setText(file.getName());
            setStatus("Sketch loaded: " + file.getName() + "  —  Now load a suspect photo →");
            refreshCompareButton();
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
    @FXML
    private void onCompare() {
        if (sketchFile == null || photoFile == null) {
            setStatus("⚠ Both sketch and suspect photo must be loaded first.");
            return;
        }
        compareBtn.setDisable(true);
        saveResultBtn.setDisable(true);
        setStatus("🔍 Analysing images… please wait.");
        progressBar.setProgress(-1); // indeterminate spinner

        Task<Double> task = new Task<>() {
            @Override
            protected Double call() throws Exception {
                return computeSimilarity(sketchFile, photoFile);
            }
        };

        task.setOnSucceeded(e -> {
            lastSimilarity = task.getValue();
            updateResultUI(lastSimilarity);
            compareBtn.setDisable(false);
            saveResultBtn.setDisable(false);
        });

        task.setOnFailed(e -> {
            setStatus("❌ Error: " + task.getException().getMessage());
            progressBar.setProgress(0);
            compareBtn.setDisable(false);
        });

        new Thread(task).start();
    }

    // ── Core comparison algorithm (pure Java) ───────────────────────────────
    private double computeSimilarity(File sketchF, File photoF) throws Exception {
        BufferedImage rawSketch = ImageIO.read(sketchF);
        BufferedImage rawPhoto  = ImageIO.read(photoF);

        if (rawSketch == null || rawPhoto == null)
            throw new Exception("Could not read one or both image files.");

        // 1. Resize to fixed square
        BufferedImage sketch = resize(rawSketch, COMPARE_SIZE, COMPARE_SIZE);
        BufferedImage photo  = resize(rawPhoto,  COMPARE_SIZE, COMPARE_SIZE);

        // 2. Convert to greyscale int arrays
        int[] sGrey = toGreyscale(sketch);
        int[] pGrey = toGreyscale(photo);

        // 3. Histogram equalisation (normalise brightness/contrast)
        sGrey = histogramEqualise(sGrey);
        pGrey = histogramEqualise(pGrey);

        // 4. RMSE-based structural similarity (0..1, 1 = identical)
        double rmseScore = computeRmseScore(sGrey, pGrey);

        // 5. Histogram intersection similarity (0..1)
        double histScore = computeHistogramIntersection(sGrey, pGrey);

        // 6. Weighted average — structural similarity weighted higher
        double combined = (rmseScore * 0.60) + (histScore * 0.40);
        return Math.min(1.0, Math.max(0.0, combined));
    }

    // Resize to target dimensions using bilinear interpolation
    private BufferedImage resize(BufferedImage src, int w, int h) {
        BufferedImage out = new BufferedImage(w, h, BufferedImage.TYPE_INT_RGB);
        Graphics2D g = out.createGraphics();
        g.setRenderingHint(RenderingHints.KEY_INTERPOLATION,
                           RenderingHints.VALUE_INTERPOLATION_BILINEAR);
        g.drawImage(src, 0, 0, w, h, null);
        g.dispose();
        return out;
    }

    // Convert ARGB image to greyscale pixel array (0–255)
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

    // Histogram equalisation — redistributes pixel intensities for fair comparison
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
        }
        return out;
    }

    // Root Mean Square Error → similarity (lower RMSE = higher similarity)
    private double computeRmseScore(int[] a, int[] b) {
        double sumSq = 0;
        for (int i = 0; i < a.length; i++) {
            double diff = a[i] - b[i];
            sumSq += diff * diff;
        }
        double rmse = Math.sqrt(sumSq / a.length); // 0..255
        return 1.0 - (rmse / 255.0);               // 1 = identical
    }

    // Histogram intersection: how much the two histograms overlap
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

    // ── Update UI with result ────────────────────────────────────────────────
    private void updateResultUI(double sim) {
        Platform.runLater(() -> {
            int pct = (int) Math.round(sim * 100);
            percentLabel.setText(pct + "%");
            progressBar.setProgress(sim);

            if (sim >= MATCH_THRESHOLD) {
                resultLabel.setText("✅  HIGH CONFIDENCE MATCH\nSuspect identity likely confirmed.");
                resultLabel.setStyle("-fx-text-fill: #44ff88; -fx-font-weight: bold; -fx-font-size: 14px; -fx-text-alignment: CENTER;");
                progressBar.setStyle("-fx-accent: #44ff88;");
                setStatus("🎯 MATCH FOUND — " + pct + "% similarity exceeds the 85% threshold.");
            } else if (sim >= 0.60) {
                resultLabel.setText("⚠  POSSIBLE MATCH\nRequires further investigation.");
                resultLabel.setStyle("-fx-text-fill: #ffbb44; -fx-font-weight: bold; -fx-font-size: 14px; -fx-text-alignment: CENTER;");
                progressBar.setStyle("-fx-accent: #ffbb44;");
                setStatus("⚠ Possible match at " + pct + "% — below 85% threshold.");
            } else {
                resultLabel.setText("❌  NO MATCH\nSuspect does not match the sketch.");
                resultLabel.setStyle("-fx-text-fill: #ff5555; -fx-font-weight: bold; -fx-font-size: 14px; -fx-text-alignment: CENTER;");
                progressBar.setStyle("-fx-accent: #ff5555;");
                setStatus("No match — " + pct + "% similarity is below threshold.");
            }
        });
    }

    // ── Save text report ─────────────────────────────────────────────────────
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
                String verdict = lastSimilarity >= MATCH_THRESHOLD ? "MATCH" :
                                 lastSimilarity >= 0.60            ? "POSSIBLE MATCH" : "NO MATCH";
                fw.write("==========================================\n");
                fw.write("        ThirdEye — Forensic Report\n");
                fw.write("==========================================\n");
                fw.write("Date       : " + new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date()) + "\n");
                fw.write("Analyst    : Mallikarjun Gala\n");
                fw.write("------------------------------------------\n");
                fw.write("Sketch     : " + (sketchFile != null ? sketchFile.getAbsolutePath() : "N/A") + "\n");
                fw.write("Photo      : " + (photoFile  != null ? photoFile.getAbsolutePath()  : "N/A") + "\n");
                fw.write("------------------------------------------\n");
                fw.write("Similarity : " + pct + "%\n");
                fw.write("Threshold  : " + (int)(MATCH_THRESHOLD * 100) + "%\n");
                fw.write("VERDICT    : " + verdict + "\n");
                fw.write("==========================================\n");
                setStatus("✅ Report saved: " + out.getAbsolutePath());
            } catch (IOException e) {
                setStatus("❌ Could not save report: " + e.getMessage());
                Logger.getLogger(Upload_sketchController.class.getName()).log(Level.SEVERE, null, e);
            }
        }
    }

    private void refreshCompareButton() {
        compareBtn.setDisable(sketchFile == null || photoFile == null);
    }

    private void setStatus(String msg) {
        Platform.runLater(() -> statusBar.setText(msg));
    }
}
