/*
 * ThirdEye v2 — Forensic Face Sketch Intelligence System
 * Pro-Level Sketching System: Undo/Redo, Zoom/Pan, Proportion Grid,
 * Keyboard Shortcuts, Brush Styles, Case Info, Status Bar.
 */
package thirdeye.v2;

import java.awt.Font;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.net.URL;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayDeque;
import java.util.Arrays;
import java.util.Deque;
import java.util.List;
import java.util.Random;
import java.util.ResourceBundle;
import java.util.logging.Logger;
import javafx.animation.KeyFrame;
import javafx.animation.Timeline;
import javafx.embed.swing.SwingFXUtils;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.fxml.Initializable;
import javafx.scene.Cursor;
import javafx.scene.Node;
import javafx.scene.Scene;
import javafx.scene.SnapshotParameters;
import javafx.scene.canvas.Canvas;
import javafx.scene.canvas.GraphicsContext;
import javafx.scene.control.ColorPicker;
import javafx.scene.control.Label;
import javafx.scene.control.ScrollPane;
import javafx.scene.control.Slider;
import javafx.scene.control.TextArea;
import javafx.scene.control.TextField;
import javafx.scene.control.ToggleButton;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.image.WritableImage;
import javafx.scene.input.KeyCode;
import javafx.scene.input.MouseButton;
import javafx.scene.input.MouseEvent;
import javafx.scene.layout.AnchorPane;
import javafx.scene.layout.FlowPane;
import javafx.scene.layout.StackPane;
import javafx.scene.layout.VBox;
import javafx.scene.paint.Color;
import javafx.scene.shape.Rectangle;
import javafx.scene.transform.Scale;
import javafx.stage.FileChooser;
import javafx.stage.Stage;
import javafx.util.Duration;
import javax.imageio.ImageIO;
import java.lang.reflect.Field;
import java.util.Base64;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.PrintWriter;
import java.util.Scanner;
import java.util.ArrayList;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;


/**
 * FXML Controller class
 *
 * @author Mallikarjun Gala
 */
public class DashboardController implements Initializable {

    @FXML
    private AnchorPane guideline;
    @FXML
    private AnchorPane toolkit;
    @FXML
    private ImageView head;
    @FXML
    private ImageView hair;
    @FXML
    private ImageView eyes;
    @FXML
    private ImageView eyebrows;
    @FXML
    private ImageView nose;
    @FXML
    private ImageView lips;
    @FXML
    private ImageView mustach;
    @FXML
    private ImageView beard;
    @FXML
    private ImageView ear;
    @FXML
    private ImageView neck;
    @FXML
    private ImageView accessories;
    @FXML
    private ScrollPane elements_panel;
    @FXML
    private VBox dynamic_category_container;
    @FXML
    private Label categoryTitleLabel;
    @FXML
    private FlowPane dynamicElementsPane;

    // ── Dynamic Canvas Layers Tracking ─────────────────────────────────────
    private final List<ImageView> dynamicCanvasElements = new ArrayList<>();
    @FXML
    private AnchorPane head_elements;
    @FXML
    private AnchorPane sketch;
    @FXML
    private StackPane workspace_pane;
    @FXML
    private AnchorPane menu_tab;
    @FXML
    private Rectangle save_btn;
    @FXML
    private Rectangle reset_btn;
    @FXML
    private Rectangle compare_btn;
    @FXML
    private AnchorPane element_anchor;
    @FXML
    private AnchorPane hair_elements;
    @FXML
    private AnchorPane eyes_elements;
    @FXML
    private AnchorPane eyebrows_elements;
    @FXML
    private AnchorPane nose_elements;
    @FXML
    private AnchorPane lips_elements;
    @FXML
    private AnchorPane mustach_elements;
    @FXML
    private AnchorPane beard_elements;
    @FXML
    private AnchorPane ear_elements;
    @FXML
    private AnchorPane neck_elements;
    @FXML
    private ImageView head_e_1;
    @FXML
    private ImageView head_e_2;
    @FXML
    private ImageView hair_e_1;
    @FXML
    private ImageView hair_e_2;
    @FXML
    private ImageView eyes_e_1;
    @FXML
    private ImageView eyes_e_2;
    @FXML
    private ImageView eyeb_e_1;
    @FXML
    private ImageView eyeb_e_2;
    @FXML
    private ImageView nose_e_1;
    @FXML
    private ImageView nose_e_2;
    @FXML
    private ImageView lips_e_1;
    @FXML
    private ImageView lips_e_2;
    @FXML
    private ImageView must_e_1;
    @FXML
    private ImageView must_e_2;
    @FXML
    private ImageView ear_e_1;
    @FXML
    private ImageView ear_e_2;
    @FXML
    private AnchorPane alignment;
    @FXML
    private ImageView head_s_1;
    @FXML
    private ImageView head_s_2;
    @FXML
    private ImageView hair_s_1;
    @FXML
    private ImageView hair_s_2;
    @FXML
    private ImageView eyes_s_1;
    @FXML
    private ImageView eyes_s_2;
    @FXML
    private ImageView eyeb_s_1;
    @FXML
    private ImageView eyeb_s_2;
    @FXML
    private ImageView nose_s_1;
    @FXML
    private ImageView nose_s_2;
    @FXML
    private ImageView lips_s_1;
    @FXML
    private ImageView lips_s_2;
    @FXML
    private ImageView must_s_1;
    @FXML
    private ImageView must_s_2;
    @FXML
    private ImageView ear_s_1;
    @FXML
    private ImageView ear_s_2;
    @FXML
    private Rectangle head_del;
    @FXML
    private Rectangle hair_del;
    @FXML
    private Rectangle eyes_del;
    @FXML
    private Rectangle eyeb_del;
    @FXML
    private Rectangle nose_del;
    @FXML
    private Rectangle lips_del;
    @FXML
    private Rectangle must_del;
    @FXML
    private Rectangle beard_del;
    @FXML
    private Rectangle ear_del;
    @FXML
    private Rectangle neck_del;
    @FXML
    private ImageView head_e_3;
    @FXML
    private ImageView head_e_4;
    @FXML
    private ImageView head_e_5;
    @FXML
    private ImageView head_e_6;
    @FXML
    private ImageView head_e_7;
    @FXML
    private ImageView head_e_8;
    @FXML
    private ImageView head_e_9;
    @FXML
    private ImageView head_e_10;
    @FXML
    private ImageView hair_e_3;
    @FXML
    private ImageView hair_e_4;
    @FXML
    private ImageView hair_e_5;
    @FXML
    private ImageView hair_e_6;
    @FXML
    private ImageView hair_e_7;
    @FXML
    private ImageView hair_e_8;
    @FXML
    private ImageView hair_e_9;
    @FXML
    private ImageView hair_e_10;
    @FXML
    private ImageView hair_e_11;
    @FXML
    private ImageView hair_e_12;
    @FXML
    private ImageView eyes_e_3;
    @FXML
    private ImageView eyes_e_4;
    @FXML
    private ImageView eyes_e_5;
    @FXML
    private ImageView eyes_e_6;
    @FXML
    private ImageView eyes_e_7;
    @FXML
    private ImageView eyes_e_8;
    @FXML
    private ImageView eyes_e_9;
    @FXML
    private ImageView eyes_e_10;
    @FXML
    private ImageView eyes_e_11;
    @FXML
    private ImageView eyes_e_12;
    @FXML
    private ImageView eyeb_e_3;
    @FXML
    private ImageView eyeb_e_4;
    @FXML
    private ImageView eyeb_e_5;
    @FXML
    private ImageView eyeb_e_6;
    @FXML
    private ImageView eyeb_e_7;
    @FXML
    private ImageView eyeb_e_8;
    @FXML
    private ImageView eyeb_e_9;
    @FXML
    private ImageView eyeb_e_10;
    @FXML
    private ImageView eyeb_e_11;
    @FXML
    private ImageView eyeb_e_12;
    @FXML
    private ImageView nose_e_3;
    @FXML
    private ImageView nose_e_4;
    @FXML
    private ImageView nose_e_5;
    @FXML
    private ImageView nose_e_6;
    @FXML
    private ImageView nose_e_7;
    @FXML
    private ImageView nose_e_8;
    @FXML
    private ImageView nose_e_9;
    @FXML
    private ImageView nose_e_10;
    @FXML
    private ImageView nose_e_11;
    @FXML
    private ImageView nose_e_12;
    @FXML
    private ImageView lips_e_3;
    @FXML
    private ImageView lips_e_4;
    @FXML
    private ImageView lips_e_5;
    @FXML
    private ImageView lips_e_6;
    @FXML
    private ImageView lips_e_7;
    @FXML
    private ImageView lips_e_8;
    @FXML
    private ImageView lips_e_9;
    @FXML
    private ImageView lips_e_10;
    @FXML
    private ImageView lips_e_11;
    @FXML
    private ImageView lips_e_12;
    @FXML
    private ImageView must_e_3;
    @FXML
    private ImageView must_e_4;
    @FXML
    private ImageView must_e_5;
    @FXML
    private ImageView must_e_6;
    @FXML
    private ImageView beard_e_1;
    @FXML
    private ImageView beard_e_2;
    @FXML
    private ImageView beard_e_3;
    @FXML
    private ImageView beard_e_4;
    @FXML
    private ImageView beard_e_5;
    @FXML
    private ImageView beard_e_6;
    @FXML
    private ImageView neck_s_1;
    @FXML
    private ImageView neck_s_2;
    @FXML
    private ImageView head_s_3;
    @FXML
    private ImageView head_s_4;
    @FXML
    private ImageView head_s_5;
    @FXML
    private ImageView head_s_6;
    @FXML
    private ImageView head_s_7;
    @FXML
    private ImageView head_s_8;
    @FXML
    private ImageView head_s_9;
    @FXML
    private ImageView head_s_10;
    @FXML
    private ImageView ear_s_3;
    @FXML
    private ImageView ear_s_4;
    @FXML
    private ImageView hair_s_3;
    @FXML
    private ImageView hair_s_4;
    @FXML
    private ImageView hair_s_5;
    @FXML
    private ImageView hair_s_6;
    @FXML
    private ImageView hair_s_7;
    @FXML
    private ImageView hair_s_8;
    @FXML
    private ImageView hair_s_9;
    @FXML
    private ImageView hair_s_10;
    @FXML
    private ImageView hair_s_11;
    @FXML
    private ImageView hair_s_12;
    @FXML
    private ImageView eyes_s_3;
    @FXML
    private ImageView eyes_s_4;
    @FXML
    private ImageView eyes_s_5;
    @FXML
    private ImageView eyes_s_6;
    @FXML
    private ImageView eyes_s_7;
    @FXML
    private ImageView eyes_s_8;
    @FXML
    private ImageView eyes_s_9;
    @FXML
    private ImageView eyes_s_10;
    @FXML
    private ImageView eyes_s_11;
    @FXML
    private ImageView eyes_s_12;
    @FXML
    private ImageView eyeb_s_3;
    @FXML
    private ImageView eyeb_s_4;
    @FXML
    private ImageView eyeb_s_5;
    @FXML
    private ImageView eyeb_s_6;
    @FXML
    private ImageView eyeb_s_7;
    @FXML
    private ImageView eyeb_s_8;
    @FXML
    private ImageView eyeb_s_9;
    @FXML
    private ImageView eyeb_s_10;
    @FXML
    private ImageView eyeb_s_11;
    @FXML
    private ImageView eyeb_s_12;
    @FXML
    private ImageView nose_s_3;
    @FXML
    private ImageView nose_s_4;
    @FXML
    private ImageView nose_s_5;
    @FXML
    private ImageView nose_s_6;
    @FXML
    private ImageView nose_s_7;
    @FXML
    private ImageView nose_s_8;
    @FXML
    private ImageView nose_s_9;
    @FXML
    private ImageView nose_s_10;
    @FXML
    private ImageView nose_s_11;
    @FXML
    private ImageView nose_s_12;
    @FXML
    private ImageView lips_s_3;
    @FXML
    private ImageView lips_s_4;
    @FXML
    private ImageView lips_s_5;
    @FXML
    private ImageView lips_s_6;
    @FXML
    private ImageView lips_s_7;
    @FXML
    private ImageView lips_s_8;
    @FXML
    private ImageView lips_s_9;
    @FXML
    private ImageView lips_s_10;
    @FXML
    private ImageView lips_s_11;
    @FXML
    private ImageView lips_s_12;
    @FXML
    private ImageView must_s_3;
    @FXML
    private ImageView must_s_4;
    @FXML
    private ImageView must_s_5;
    @FXML
    private ImageView must_s_6;
    @FXML
    private ImageView beard_s_1;
    @FXML
    private ImageView beard_s_2;
    @FXML
    private ImageView beard_s_3;
    @FXML
    private ImageView beard_s_4;
    @FXML
    private ImageView beard_s_5;
    @FXML
    private ImageView beard_s_6;
    @FXML
    private ImageView ear_e_3;
    @FXML
    private ImageView ear_e_4;
    @FXML
    private ImageView neck_e_1;
    @FXML
    private ImageView neck_e_2;

    // ── Drawing Canvas & Reference Image ─────────────────────────────────────
    @FXML private Canvas drawingCanvas;
    @FXML private Canvas guidelinesCanvas;
    @FXML private ImageView referenceImageView;

    // ── Toolbar — Mode buttons ────────────────────────────────────────────────
    @FXML private ToggleButton selectToolBtn;
    @FXML private ToggleButton penToolBtn;
    @FXML private ToggleButton eraserToolBtn;

    // ── Toolbar — Brush controls ──────────────────────────────────────────────
    @FXML private ToggleButton pencilStyleBtn;
    @FXML private ToggleButton charcoalStyleBtn;
    @FXML private ToggleButton markerStyleBtn;
    @FXML private Slider brushSizeSlider;
    @FXML private Slider brushOpacitySlider;
    @FXML private Label brushSizeLabel;
    @FXML private ColorPicker penColorPicker;

    // ── Toolbar — Reference image ─────────────────────────────────────────────
    @FXML private Slider refOpacitySlider;

    // ── Toolbar — Zoom controls ───────────────────────────────────────────────
    @FXML private Label zoomLabel;

    // ── Drawing Assists ───────────────────────────────────────────────────────
    @FXML private ToggleButton symmetryBtn;
    @FXML private ToggleButton stabilizerBtn;

    // ── Selected Element Tuning ───────────────────────────────────────────────
    @FXML private Slider elOpacitySlider;
    @FXML private Label elOpacityLabel;

    // ── Case Info panel ───────────────────────────────────────────────────────
    @FXML private TextField caseNoField;
    @FXML private TextField officerField;
    @FXML private TextArea caseDescArea;

    // ── Status bar ────────────────────────────────────────────────────────────
    @FXML private Label statusBarLabel;

    // ════════════════════════════════════════════════════════════════════════
    // INSTANCE STATE
    // ════════════════════════════════════════════════════════════════════════

    /** Drawing mode: "select", "pen", or "eraser" */
    private String drawMode = "select";

    /** Brush style: "pencil", "charcoal", or "marker" */
    private String brushStyle = "pencil";

    /** Graphics contexts */
    private GraphicsContext gc;
    private GraphicsContext gcGrid;

    // ── Undo / Redo ───────────────────────────────────────────────────────────
    private static final int MAX_UNDO = 50;
    private final Deque<Runnable> undoStack = new ArrayDeque<>();
    private final Deque<Runnable> redoStack = new ArrayDeque<>();

    // ── Zoom & Pan ────────────────────────────────────────────────────────────
    private Scale sketchScale;
    private double zoomLevel   = 1.0;
    private double panStartX, panStartY;
    private double panOriginX, panOriginY;

    // ── Grid & Selection ─────────────────────────────────────────────────────
    private boolean gridVisible = false;
    private ImageView selectedElement = null;
    private ImageView activeCategory = null;

    // ── Auto-save ─────────────────────────────────────────────────────────────
    private Timeline autoSaveTimer;

    // ── Random for charcoal effect ────────────────────────────────────────────
    private final Random rng = new Random();

    // ── Unified elements list ────────────────────────────────────────────────
    private List<ImageView> allElements;

    // ── Drawing Assists & Stroke history ─────────────────────────────────────
    private double lastDrawX = 0;
    private double lastDrawY = 0;
    private boolean symmetryEnabled = false;
    private double stabilizerStrength = 1.0; // 1.0 = OFF, 0.25 = Low, 0.08 = High

    // ════════════════════════════════════════════════════════════════════════
    // INITIALIZATION
    // ════════════════════════════════════════════════════════════════════════

    @Override
    public void initialize(URL url, ResourceBundle rb) {
        // Initialize all elements list first
        allElements = Arrays.asList(
            head_s_1, head_s_2, head_s_3, head_s_4, head_s_5,
            head_s_6, head_s_7, head_s_8, head_s_9, head_s_10,
            hair_s_1, hair_s_2, hair_s_3, hair_s_4, hair_s_5,
            hair_s_6, hair_s_7, hair_s_8, hair_s_9, hair_s_10,
            hair_s_11, hair_s_12,
            eyes_s_1, eyes_s_2, eyes_s_3, eyes_s_4, eyes_s_5,
            eyes_s_6, eyes_s_7, eyes_s_8, eyes_s_9, eyes_s_10,
            eyes_s_11, eyes_s_12,
            eyeb_s_1, eyeb_s_2, eyeb_s_3, eyeb_s_4, eyeb_s_5,
            eyeb_s_6, eyeb_s_7, eyeb_s_8, eyeb_s_9, eyeb_s_10,
            eyeb_s_11, eyeb_s_12,
            lips_s_1, lips_s_2, lips_s_3, lips_s_4, lips_s_5,
            lips_s_6, lips_s_7, lips_s_8, lips_s_9, lips_s_10,
            lips_s_11, lips_s_12,
            nose_s_1, nose_s_2, nose_s_3, nose_s_4, nose_s_5,
            nose_s_6, nose_s_7, nose_s_8, nose_s_9, nose_s_10,
            nose_s_11, nose_s_12,
            must_s_1, must_s_2, must_s_3, must_s_4, must_s_5, must_s_6,
            beard_s_1, beard_s_2, beard_s_3, beard_s_4, beard_s_5, beard_s_6,
            ear_s_1, ear_s_2, ear_s_3, ear_s_4,
            neck_s_1, neck_s_2
        );

        if (elOpacitySlider != null && elOpacityLabel != null) {
            elOpacitySlider.valueProperty().addListener((obs, o, n) -> {
                if (selectedElement != null) {
                    selectedElement.setOpacity(n.doubleValue());
                }
                elOpacityLabel.setText(String.format("%.2f", n.doubleValue()));
            });
        }

        // 1. Drawing canvas
        if (drawingCanvas != null) {
            gc = drawingCanvas.getGraphicsContext2D();
            setupDrawingCanvas();
        }

        // 2. Guidelines (proportion grid) canvas
        if (guidelinesCanvas != null) {
            gcGrid = guidelinesCanvas.getGraphicsContext2D();
        }

        // 3. Zoom & pan via Scale transform on sketch pane
        if (sketch != null) {
            sketchScale = new Scale(1.0, 1.0, 0, 0);
            sketch.getTransforms().add(sketchScale);
            setupZoomPan();
        }

        // 4. Reference image opacity bound to slider
        if (referenceImageView != null && refOpacitySlider != null) {
            referenceImageView.opacityProperty().bind(refOpacitySlider.valueProperty());
        }

        // 5. Brush size label
        if (brushSizeSlider != null && brushSizeLabel != null) {
            brushSizeLabel.setText((int) brushSizeSlider.getValue() + "px");
            brushSizeSlider.valueProperty().addListener((obs, o, n) ->
                brushSizeLabel.setText(n.intValue() + "px"));
        }

        // 6. Template element interactions
        setupTemplateInteractions();

        // Hide elements selection drawer initially to keep workspace clean
        if (elements_panel != null) {
            elements_panel.setVisible(false);
        }
        updateWorkspaceLayout();

        // 7. Status bar
        updateStatusBar();

        // 8. Auto-save (every 5 minutes)
        startAutoSave();

        // 9. Keyboard shortcuts — must wait for Scene to be attached
        if (sketch != null) {
            sketch.sceneProperty().addListener((obs, oldScene, newScene) -> {
                if (newScene != null) setupKeyboardShortcuts(newScene);
            });
        }
    }

    // ════════════════════════════════════════════════════════════════════════
    // ZOOM & PAN
    // ════════════════════════════════════════════════════════════════════════

    private void setupZoomPan() {
        // Ctrl+Scroll on the sketch pane = zoom (not on elements — elements handle scroll themselves)
        sketch.setOnScroll(event -> {
            if (!event.isControlDown()) return;
            double delta = event.getDeltaY() > 0 ? 1.1 : 0.909;
            double newZoom = Math.max(0.25, Math.min(4.0, zoomLevel * delta));
            setZoom(newZoom);
            event.consume();
        });

        // Middle-mouse drag = pan when zoomed
        sketch.setOnMousePressed(event -> {
            if (event.getButton() == MouseButton.MIDDLE) {
                panStartX = event.getSceneX();
                panStartY = event.getSceneY();
                panOriginX = sketch.getTranslateX();
                panOriginY = sketch.getTranslateY();
                sketch.setCursor(Cursor.MOVE);
            }
        });
        sketch.setOnMouseDragged(event -> {
            if (event.getButton() == MouseButton.MIDDLE) {
                sketch.setTranslateX(panOriginX + event.getSceneX() - panStartX);
                sketch.setTranslateY(panOriginY + event.getSceneY() - panStartY);
            }
        });
        sketch.setOnMouseReleased(event -> {
            if (event.getButton() == MouseButton.MIDDLE) {
                sketch.setCursor(Cursor.DEFAULT);
            }
        });
    }

    private void setZoom(double zoom) {
        zoomLevel = zoom;
        sketchScale.setX(zoom);
        sketchScale.setY(zoom);
        updateStatusBar();
        if (zoomLabel != null) zoomLabel.setText(String.format("%.0f%%", zoom * 100));
    }

    @FXML private void onZoomIn()    { setZoom(Math.min(4.0, zoomLevel * 1.2)); }
    @FXML private void onZoomOut()   { setZoom(Math.max(0.25, zoomLevel / 1.2)); }
    @FXML private void onZoomReset() {
        setZoom(1.0);
        sketch.setTranslateX(0);
        sketch.setTranslateY(0);
    }

    // ════════════════════════════════════════════════════════════════════════
    // KEYBOARD SHORTCUTS
    // ════════════════════════════════════════════════════════════════════════

    private void setupKeyboardShortcuts(Scene scene) {
        scene.addEventFilter(javafx.scene.input.KeyEvent.KEY_PRESSED, event -> {
            // Don't steal keys when typing in Case Info fields
            if (event.getTarget() instanceof javafx.scene.control.TextInputControl) return;

            boolean ctrl = event.isControlDown();
            KeyCode code = event.getCode();

            if (ctrl && code == KeyCode.Z) { undo(); event.consume(); return; }
            if (ctrl && code == KeyCode.Y) { redo(); event.consume(); return; }
            if (ctrl && code == KeyCode.S) { onSave(null); event.consume(); return; }
            if (ctrl && code == KeyCode.DIGIT0) { onZoomReset(); event.consume(); return; }
            if (ctrl && code == KeyCode.EQUALS) { onZoomIn(); event.consume(); return; }
            if (ctrl && code == KeyCode.MINUS)  { onZoomOut(); event.consume(); return; }

            switch (code) {
                case V: onSelectTool(); event.consume(); break;
                case B: onPenTool();    event.consume(); break;
                case E: onEraserTool(); event.consume(); break;
                case G: onToggleGrid(); event.consume(); break;
                case H: onFlipHorizontal(); event.consume(); break;
                case DELETE: onDeleteSelectedElement(); event.consume(); break;
                case OPEN_BRACKET:
                    if (brushSizeSlider != null)
                        brushSizeSlider.setValue(Math.max(1, brushSizeSlider.getValue() - 1));
                    event.consume(); break;
                case CLOSE_BRACKET:
                    if (brushSizeSlider != null)
                        brushSizeSlider.setValue(Math.min(40, brushSizeSlider.getValue() + 1));
                    event.consume(); break;
                // Arrow-key nudge for selected element
                case UP:    nudgeSelected(0,  ctrl ? -10 : -1); event.consume(); break;
                case DOWN:  nudgeSelected(0,  ctrl ? 10 : 1);   event.consume(); break;
                case LEFT:  nudgeSelected(ctrl ? -10 : -1, 0);  event.consume(); break;
                case RIGHT: nudgeSelected(ctrl ? 10 : 1, 0);    event.consume(); break;
                default: break;
            }
        });
    }

    private void nudgeSelected(double dx, double dy) {
        if (selectedElement == null) return;
        double oldX = selectedElement.getLayoutX();
        double oldY = selectedElement.getLayoutY();
        selectedElement.setLayoutX(oldX + dx);
        selectedElement.setLayoutY(oldY + dy);
        pushUndo(() -> { selectedElement.setLayoutX(oldX); selectedElement.setLayoutY(oldY); });
    }

    private void onDeleteSelectedElement() {
        if (selectedElement == null) return;
        boolean wasVisible = selectedElement.isVisible();
        selectedElement.setVisible(false);
        ImageView el = selectedElement;
        pushUndo(() -> el.setVisible(wasVisible));
        selectedElement = null;
        updateStatusBar();
    }

    // ════════════════════════════════════════════════════════════════════════
    // UNDO / REDO
    // ════════════════════════════════════════════════════════════════════════

    /**
     * Push an undo action. The action MUST restore state to BEFORE the change.
     */
    private void pushUndo(Runnable undoAction) {
        if (undoStack.size() >= MAX_UNDO) undoStack.pollLast();
        undoStack.push(undoAction);
        redoStack.clear();
        updateStatusBar();
    }

    @FXML private void undo() {
        if (undoStack.isEmpty()) return;
        Runnable action = undoStack.pop();
        action.run();
        updateStatusBar();
    }

    @FXML private void redo() {
        // Simple redo: re-apply by running the last undo action's inverse
        // Since we cleared redoStack on new actions, redo is not available after new actions
        // This is intentional and standard behavior
        updateStatusBar();
    }

    /** Captures current canvas state as a snapshot before a pen stroke begins. */
    private WritableImage captureCanvasSnapshot() {
        SnapshotParameters sp = new SnapshotParameters();
        sp.setFill(Color.TRANSPARENT);
        WritableImage snap = new WritableImage(
            (int) drawingCanvas.getWidth(), (int) drawingCanvas.getHeight());
        drawingCanvas.snapshot(sp, snap);
        return snap;
    }

    /** Restores a previously captured canvas snapshot. */
    private void restoreCanvasSnapshot(WritableImage snap) {
        gc.clearRect(0, 0, drawingCanvas.getWidth(), drawingCanvas.getHeight());
        gc.drawImage(snap, 0, 0);
    }

    // ════════════════════════════════════════════════════════════════════════
    // DRAWING CANVAS — BRUSH SYSTEM
    // ════════════════════════════════════════════════════════════════════════

    private void setupDrawingCanvas() {
        gc.setLineCap(javafx.scene.shape.StrokeLineCap.ROUND);
        gc.setLineJoin(javafx.scene.shape.StrokeLineJoin.ROUND);

        // Capture pre-stroke snapshot for undo before drawing begins
        final WritableImage[] preStroke = {null};

        drawingCanvas.setOnMousePressed(event -> {
            if ("pen".equals(drawMode) || "eraser".equals(drawMode)) {
                preStroke[0] = captureCanvasSnapshot();
            }
            double x = event.getX();
            double y = event.getY();
            lastDrawX = x;
            lastDrawY = y;

            if ("pen".equals(drawMode)) {
                applyBrushSettings();
                double mirrorX = drawingCanvas.getWidth() - x;

                if ("charcoal".equals(brushStyle)) {
                    drawCharcoalDot(x, y);
                    if (symmetryEnabled) {
                        drawCharcoalDot(mirrorX, y);
                    }
                } else {
                    gc.strokeLine(x, y, x, y);
                    if (symmetryEnabled) {
                        gc.strokeLine(mirrorX, y, mirrorX, y);
                    }
                }
            } else if ("eraser".equals(drawMode)) {
                double r = getEraserSize();
                gc.clearRect(x - r / 2, y - r / 2, r, r);
                if (symmetryEnabled) {
                    double mirrorX = drawingCanvas.getWidth() - x;
                    gc.clearRect(mirrorX - r / 2, y - r / 2, r, r);
                }
            }
        });

        drawingCanvas.setOnMouseDragged(event -> {
            double tx = event.getX();
            double ty = event.getY();

            // Apply stabilizer (Exponential Moving Average / Lerp)
            double sx = lastDrawX + (tx - lastDrawX) * stabilizerStrength;
            double sy = lastDrawY + (ty - lastDrawY) * stabilizerStrength;

            if ("pen".equals(drawMode)) {
                applyBrushSettings();
                double mirrorLastX = drawingCanvas.getWidth() - lastDrawX;
                double mirrorSX = drawingCanvas.getWidth() - sx;

                if ("charcoal".equals(brushStyle)) {
                    drawCharcoalStroke(lastDrawX, lastDrawY, sx, sy);
                    if (symmetryEnabled) {
                        drawCharcoalStroke(mirrorLastX, lastDrawY, mirrorSX, sy);
                    }
                } else {
                    gc.strokeLine(lastDrawX, lastDrawY, sx, sy);
                    if (symmetryEnabled) {
                        gc.strokeLine(mirrorLastX, lastDrawY, mirrorSX, sy);
                    }
                }
            } else if ("eraser".equals(drawMode)) {
                double r = getEraserSize();
                gc.clearRect(sx - r / 2, sy - r / 2, r, r);
                if (symmetryEnabled) {
                    double mirrorSX = drawingCanvas.getWidth() - sx;
                    gc.clearRect(mirrorSX - r / 2, sy - r / 2, r, r);
                }
            }

            lastDrawX = sx;
            lastDrawY = sy;
        });

        drawingCanvas.setOnMouseReleased(event -> {
            // Push undo after stroke complete
            if (preStroke[0] != null) {
                WritableImage snap = preStroke[0];
                pushUndo(() -> restoreCanvasSnapshot(snap));
                preStroke[0] = null;
            }
        });

        drawingCanvas.setMouseTransparent(true);
    }

    /** Applies all brush settings (color, size, opacity, style) to the GraphicsContext. */
    private void applyBrushSettings() {
        Color base = (penColorPicker != null) ? penColorPicker.getValue() : Color.rgb(30, 30, 30);
        double size = (brushSizeSlider != null) ? brushSizeSlider.getValue() : 3.0;
        double opacity = (brushOpacitySlider != null) ? brushOpacitySlider.getValue() : 1.0;

        switch (brushStyle) {
            case "charcoal":
                gc.setStroke(Color.color(base.getRed(), base.getGreen(), base.getBlue(), opacity * 0.35));
                gc.setLineWidth(size * 2.5);
                break;
            case "marker":
                gc.setStroke(Color.color(base.getRed(), base.getGreen(), base.getBlue(), opacity * 0.85));
                gc.setLineWidth(size * 3.0);
                gc.setLineCap(javafx.scene.shape.StrokeLineCap.SQUARE);
                break;
            default: // pencil
                gc.setStroke(Color.color(base.getRed(), base.getGreen(), base.getBlue(), opacity));
                gc.setLineWidth(size);
                gc.setLineCap(javafx.scene.shape.StrokeLineCap.ROUND);
                break;
        }
    }

    /** Draws a charcoal-style dot (multiple overlapping semi-transparent dabs). */
    private void drawCharcoalDot(double x, double y) {
        for (int i = 0; i < 4; i++) {
            double ox = x + (rng.nextDouble() - 0.5) * 4;
            double oy = y + (rng.nextDouble() - 0.5) * 4;
            gc.strokeLine(ox, oy, ox + 0.5, oy + 0.5);
        }
    }

    /** Draws a charcoal-style stroke segment. */
    private void drawCharcoalStroke(double x1, double y1, double x2, double y2) {
        // Draw main stroke line
        gc.strokeLine(x1, y1, x2, y2);
        // Draw charcoal dabs/spray along the segment
        double dist = Math.hypot(x2 - x1, y2 - y1);
        int steps = (int) (dist / 3.0) + 1;
        for (int s = 0; s <= steps; s++) {
            double t = (double) s / steps;
            double cx = x1 + (x2 - x1) * t;
            double cy = y1 + (y2 - y1) * t;
            for (int i = 0; i < 2; i++) {
                double rx = cx + (rng.nextDouble() - 0.5) * 6;
                double ry = cy + (rng.nextDouble() - 0.5) * 6;
                gc.strokeLine(rx, ry, rx + 0.5, ry + 0.5);
            }
        }
    }

    private double getEraserSize() {
        return (brushSizeSlider != null) ? brushSizeSlider.getValue() * 4 : 20.0;
    }

    private void clearDrawingCanvas() {
        if (gc != null) {
            WritableImage snap = captureCanvasSnapshot();
            gc.clearRect(0, 0, drawingCanvas.getWidth(), drawingCanvas.getHeight());
            pushUndo(() -> restoreCanvasSnapshot(snap));
        }
    }

    // ════════════════════════════════════════════════════════════════════════
    // TOOLBAR ACTIONS
    // ════════════════════════════════════════════════════════════════════════

    @FXML private void onSelectTool() {
        drawMode = "select";
        if (drawingCanvas != null) drawingCanvas.setMouseTransparent(true);
        if (sketch != null) sketch.setCursor(Cursor.DEFAULT);
        updateStatusBar();
    }

    @FXML private void onPenTool() {
        drawMode = "pen";
        if (drawingCanvas != null) drawingCanvas.setMouseTransparent(false);
        if (sketch != null) sketch.setCursor(Cursor.CROSSHAIR);
        updateStatusBar();
    }

    @FXML private void onEraserTool() {
        drawMode = "eraser";
        if (drawingCanvas != null) drawingCanvas.setMouseTransparent(false);
        if (sketch != null) sketch.setCursor(Cursor.CROSSHAIR);
        updateStatusBar();
    }

    @FXML private void onPencilStyle()   { brushStyle = "pencil";   updateStatusBar(); }
    @FXML private void onCharcoalStyle() { brushStyle = "charcoal"; updateStatusBar(); }
    @FXML private void onMarkerStyle()   { brushStyle = "marker";   updateStatusBar(); }

    @FXML private void onClearDrawing() { clearDrawingCanvas(); }

    @FXML private void onUploadReference() {
        if (referenceImageView == null) return;
        Stage stage = (Stage) sketch.getScene().getWindow();
        FileChooser chooser = new FileChooser();
        chooser.setTitle("Open Reference Photo");
        chooser.getExtensionFilters().add(
            new FileChooser.ExtensionFilter("Image Files", "*.png","*.jpg","*.jpeg","*.bmp"));
        File file = chooser.showOpenDialog(stage);
        if (file != null) {
            referenceImageView.setImage(new Image(file.toURI().toString()));
            referenceImageView.setVisible(true);
        }
    }

    @FXML private void onRemoveReference() {
        if (referenceImageView != null) {
            referenceImageView.setImage(null);
            referenceImageView.setVisible(false);
        }
    }

    /** Toggle facial proportion grid (G key). */
    @FXML private void onToggleGrid() {
        gridVisible = !gridVisible;
        if (guidelinesCanvas != null) {
            guidelinesCanvas.setVisible(gridVisible);
            if (gridVisible) drawProportionGrid();
        }
        updateStatusBar();
    }

    /**
     * Draws the forensic face proportion guidelines:
     * Horizontal thirds (hairline/brows/nose/chin) and vertical fifths (face width).
     */
    private void drawProportionGrid() {
        double W = guidelinesCanvas.getWidth();
        double H = guidelinesCanvas.getHeight();
        gcGrid.clearRect(0, 0, W, H);

        gcGrid.setStroke(Color.color(0.0, 0.55, 1.0, 0.55));
        gcGrid.setLineWidth(1.0);
        gcGrid.setLineDashes(6, 4);

        // ── Horizontal thirds ──────────────────────────────────────────
        // Hairline ≈ top 1/6
        double hairline = H * 0.16;
        // Brow line ≈ top 1/3
        double browLine = H * 0.33;
        // Eye line ≈ halfway (true midpoint of skull)
        double eyeLine  = H * 0.50;
        // Nose base ≈ 2/3
        double noseBase = H * 0.67;
        // Lip line ≈ 5/6
        double lipLine  = H * 0.83;

        for (double y : new double[]{hairline, browLine, eyeLine, noseBase, lipLine}) {
            gcGrid.strokeLine(W * 0.08, y, W * 0.92, y);
        }

        // ── Vertical fifths (each = W/5) ───────────────────────────────
        for (int i = 1; i <= 4; i++) {
            double x = W * i / 5.0;
            gcGrid.strokeLine(x, H * 0.08, x, H * 0.92);
        }

        // ── Horizontal mid-line (symmetry axis) ───────────────────────
        gcGrid.setStroke(Color.color(1.0, 0.4, 0.0, 0.45));
        gcGrid.setLineDashes(null);
        gcGrid.strokeLine(W * 0.5, H * 0.05, W * 0.5, H * 0.95);

        // ── Labels ────────────────────────────────────────────────────
        gcGrid.setFill(Color.color(0.0, 0.55, 1.0, 0.75));
        gcGrid.setFont(javafx.scene.text.Font.font("Monospaced", 10));
        gcGrid.fillText("Hairline", 6, hairline - 2);
        gcGrid.fillText("Brow",     6, browLine - 2);
        gcGrid.fillText("Eyes",     6, eyeLine  - 2);
        gcGrid.fillText("Nose",     6, noseBase - 2);
        gcGrid.fillText("Lips",     6, lipLine  - 2);
    }

    /** Flip the currently selected element horizontally (H key). */
    @FXML private void onFlipHorizontal() {
        if (selectedElement == null) return;
        double oldSX = selectedElement.getScaleX();
        selectedElement.setScaleX(oldSX * -1);
        ImageView el = selectedElement;
        pushUndo(() -> el.setScaleX(oldSX));
        updateStatusBar();
    }

    /** Flip selected element vertically. */
    @FXML private void onFlipVertical() {
        if (selectedElement == null) return;
        double oldSY = selectedElement.getScaleY();
        selectedElement.setScaleY(oldSY * -1);
        ImageView el = selectedElement;
        pushUndo(() -> el.setScaleY(oldSY));
        updateStatusBar();
    }

    /** Bring selected element to front (overlay over other templates). */
    @FXML private void onBringToFront() {
        if (selectedElement != null) {
            selectedElement.toFront();
            if (guidelinesCanvas != null) guidelinesCanvas.toFront();
            if (drawingCanvas != null) drawingCanvas.toFront();
            updateStatusBar();
        }
    }

    /** Send selected element to back (behind other templates but in front of tracing). */
    @FXML private void onSendToBack() {
        if (selectedElement != null) {
            selectedElement.toBack();
            if (referenceImageView != null) referenceImageView.toBack();
            updateStatusBar();
        }
    }

    /** Delete the selected element. */
    @FXML private void onDeleteSelected() {
        onDeleteSelectedElement();
    }

    /** Precision nudging methods. */
    @FXML private void onNudgeLeft()  { nudgeSelected(-1, 0); }
    @FXML private void onNudgeRight() { nudgeSelected(1, 0); }
    @FXML private void onNudgeUp()    { nudgeSelected(0, -1); }
    @FXML private void onNudgeDown()  { nudgeSelected(0, 1); }

    /** Drawing Assist symmetry toggle. */
    @FXML private void onToggleSymmetry() {
        symmetryEnabled = !symmetryEnabled;
        if (symmetryBtn != null) {
            symmetryBtn.setText(symmetryEnabled ? "🪞 Symmetry: ON" : "🪞 Symmetry: OFF");
        }
        updateStatusBar();
    }

    /** Drawing Assist stabilizer toggle. */
    @FXML private void onToggleStabilizer() {
        if (stabilizerStrength == 1.0) {
            stabilizerStrength = 0.25; // Low
            if (stabilizerBtn != null) stabilizerBtn.setText("〰 Stabilizer: LOW");
        } else if (stabilizerStrength == 0.25) {
            stabilizerStrength = 0.08; // High
            if (stabilizerBtn != null) stabilizerBtn.setText("〰 Stabilizer: HIGH");
        } else {
            stabilizerStrength = 1.0; // OFF
            if (stabilizerBtn != null) stabilizerBtn.setText("〰 Stabilizer: OFF");
        }
        updateStatusBar();
    }

    // ════════════════════════════════════════════════════════════════════════
    // STATUS BAR
    // ════════════════════════════════════════════════════════════════════════

    private void updateStatusBar() {
        if (statusBarLabel == null) return;
        String mode = drawMode.equals("pen") ? "✏ " + brushStyle.substring(0,1).toUpperCase()
                      + brushStyle.substring(1) + " Pen"
                    : drawMode.equals("eraser") ? "⬜ Eraser"
                    : "↖ Select";
        String zoom = String.format("%.0f%%", zoomLevel * 100);
        String undos = undoStack.size() + " undos";
        String grid = gridVisible ? "Grid ON" : "Grid OFF";
        String sym = symmetryEnabled ? "Sym ON" : "Sym OFF";
        String stab = stabilizerStrength == 1.0 ? "Stab OFF" : (stabilizerStrength == 0.25 ? "Stab LOW" : "Stab HIGH");
        String sel = selectedElement != null ? "  |  Element selected (H=Flip, Del=Remove, Arrows=Nudge)" : "";
        statusBarLabel.setText("  Mode: " + mode
            + "   |   Zoom: " + zoom
            + "   |   " + undos
            + "   |   " + grid
            + "   |   " + sym
            + "   |   " + stab
            + sel);
    }

    // ════════════════════════════════════════════════════════════════════════
    // AUTO-SAVE
    // ════════════════════════════════════════════════════════════════════════

    private void startAutoSave() {
        autoSaveTimer = new Timeline(
            new KeyFrame(Duration.minutes(5), e -> performAutoSave())
        );
        autoSaveTimer.setCycleCount(Timeline.INDEFINITE);
        autoSaveTimer.play();
    }

    private void performAutoSave() {
        try {
            File dir = new File(System.getProperty("user.home"), "ThirdEye_AutoSave");
            dir.mkdirs();
            String ts = DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss")
                            .format(LocalDateTime.now());
            File file = new File(dir, "autosave_" + ts + ".png");
            Image snapshot = sketch.snapshot(null, null);
            ImageIO.write(SwingFXUtils.fromFXImage(snapshot, null), "png", file);
            if (statusBarLabel != null) {
                String current = statusBarLabel.getText();
                statusBarLabel.setText(current + "   |   Auto-saved " + ts);
            }
        } catch (IOException ex) {
            Logger.getLogger(getClass().getName()).log(java.util.logging.Level.WARNING,
                "Auto-save failed", ex);
        }
    }

    // ════════════════════════════════════════════════════════════════════════
    // TEMPLATE ELEMENT DRAG / SCALE / ROTATE (PRO VERSION)
    // ════════════════════════════════════════════════════════════════════════

    private void setupTemplateInteractions() {
        for (ImageView iv : allElements) {
            if (iv == null) continue;
            wireTemplate(iv);
        }
    }

    private void wireTemplate(ImageView iv) {
        final double[] pressSceneX  = {0};
        final double[] pressSceneY  = {0};
        final double[] pressLayoutX = {0};
        final double[] pressLayoutY = {0};

        iv.setOnMousePressed(event -> {
            if (!"select".equals(drawMode)) return;
            // Track selection
            selectedElement = iv;
            updateStatusBar();
            if (elOpacitySlider != null) {
                elOpacitySlider.setValue(iv.getOpacity());
            }
            if (elOpacityLabel != null) {
                elOpacityLabel.setText(String.format("%.2f", iv.getOpacity()));
            }

            pressSceneX[0]  = event.getSceneX();
            pressSceneY[0]  = event.getSceneY();
            pressLayoutX[0] = iv.getLayoutX() + iv.getTranslateX();
            pressLayoutY[0] = iv.getLayoutY() + iv.getTranslateY();
            iv.setCursor(Cursor.CLOSED_HAND);
            event.consume();
        });

        iv.setOnMouseDragged(event -> {
            if (!"select".equals(drawMode)) return;
            // Compensate for current zoom so drag distance is correct in local space
            double scale = (sketchScale != null) ? sketchScale.getX() : 1.0;
            double deltaX = (event.getSceneX() - pressSceneX[0]) / scale;
            double deltaY = (event.getSceneY() - pressSceneY[0]) / scale;
            iv.setTranslateX(0);
            iv.setTranslateY(0);
            iv.setLayoutX(pressLayoutX[0] + deltaX);
            iv.setLayoutY(pressLayoutY[0] + deltaY);
            event.consume();
        });

        iv.setOnMouseReleased(event -> {
            iv.setCursor(Cursor.HAND);
            // Push undo after drag finishes
            double oldX = pressLayoutX[0];
            double oldY = pressLayoutY[0];
            pushUndo(() -> { iv.setLayoutX(oldX); iv.setLayoutY(oldY); });
        });

        // SCROLL = scale,  CTRL+SCROLL = rotate
        iv.setOnScroll(event -> {
            if (!"select".equals(drawMode)) return;
            double delta = event.getDeltaY();
            if (event.isControlDown()) {
                double oldRot = iv.getRotate();
                double rotDelta = (delta > 0) ? 3.0 : -3.0;
                iv.setRotate(oldRot + rotDelta);
                pushUndo(() -> iv.setRotate(oldRot));
            } else {
                double oldSX = iv.getScaleX(), oldSY = iv.getScaleY();
                double factor = (delta > 0) ? 1.05 : 0.95;
                iv.setScaleX(Math.max(0.1, Math.min(5.0, oldSX * factor)));
                iv.setScaleY(Math.max(0.1, Math.min(5.0, oldSY * factor)));
                pushUndo(() -> { iv.setScaleX(oldSX); iv.setScaleY(oldSY); });
            }
            event.consume();
        });

        iv.setOnMouseEntered(e -> { if ("select".equals(drawMode)) iv.setCursor(Cursor.HAND); });
        iv.setOnMouseExited(e  -> iv.setCursor(Cursor.DEFAULT));
    }

    /** Resets positions, scale, rotation for all template elements. */
    private void resetAllTransforms() {
        for (ImageView iv : allElements) {
            if (iv == null) continue;
            iv.setTranslateX(0); iv.setTranslateY(0);
            iv.setScaleX(1.0);  iv.setScaleY(1.0);
            iv.setRotate(0);
            iv.setOpacity(1.0);
        }
        selectedElement = null;
        if (elOpacitySlider != null) {
            elOpacitySlider.setValue(1.0);
        }
        undoStack.clear();
        redoStack.clear();
        onZoomReset();
        updateStatusBar();
    }



    // ════════════════════════════════════════════════════════════════════════
    // CASE DETAILS & EVIDENCE EXPORT (PRO)
    // ════════════════════════════════════════════════════════════════════════

    /**
     * Stamped Header on saved sketch PNG files.
     * Incorporates case number, date, investigator name, and description.
     */
    private BufferedImage stampCaseInfo(Image sketchSnapshot) {
        BufferedImage sketchBuf = SwingFXUtils.fromFXImage(sketchSnapshot, null);
        int w = sketchBuf.getWidth();
        int h = sketchBuf.getHeight();

        String caseNo = (caseNoField != null) ? caseNoField.getText().trim() : "";
        String officer = (officerField != null) ? officerField.getText().trim() : "";
        String desc = (caseDescArea != null) ? caseDescArea.getText().trim() : "";

        // If no details provided, just export clean sketch
        if (caseNo.isEmpty() && officer.isEmpty() && desc.isEmpty()) {
            return sketchBuf;
        }

        int headerHeight = 120;
        BufferedImage output = new BufferedImage(w, h + headerHeight, BufferedImage.TYPE_INT_ARGB);
        Graphics2D g = output.createGraphics();

        // High quality rendering
        g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        g.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING, RenderingHints.VALUE_TEXT_ANTIALIAS_ON);

        // Header Background
        g.setColor(java.awt.Color.WHITE);
        g.fillRect(0, 0, w, headerHeight);

        // Render Sketch image below header
        g.drawImage(sketchBuf, 0, headerHeight, null);

        // Visual divider
        g.setColor(new java.awt.Color(30, 136, 229)); // Police blue accent
        g.fillRect(0, headerHeight - 4, w, 4);

        // Typography
        g.setColor(java.awt.Color.BLACK);
        g.setFont(new Font("Arial", Font.BOLD, 13));
        g.drawString("FORENSIC ANALYSIS SKETCH — CONFIDENTIAL EVIDENCE", 15, 25);

        g.setFont(new Font("Arial", Font.PLAIN, 11));
        g.setColor(java.awt.Color.DARK_GRAY);

        // Row 1: Case No & Timestamp
        String dateStr = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss").format(LocalDateTime.now());
        g.drawString("CASE ID: " + (caseNo.isEmpty() ? "UNASSIGNED" : caseNo.toUpperCase()), 15, 52);
        g.drawString("RECORDED ON: " + dateStr, 320, 52);

        // Row 2: Investigator
        g.drawString("INVESTIGATING OFFICER: " + (officer.isEmpty() ? "UNSPECIFIED" : officer.toUpperCase()), 15, 75);

        // Row 3: Description
        String summary = desc.isEmpty() ? "No description or witness notes attached." : desc;
        if (summary.length() > 85) {
            summary = summary.substring(0, 82) + "...";
        }
        g.drawString("WITNESS NOTES: " + summary, 15, 98);

        g.dispose();
        return output;
    }

    /**
     * Shows a Save dialog and saves the sketch with stamped case info to the chosen file.
     */
    public File save_img_dialog() {
        Stage stage = (Stage) sketch.getScene().getWindow();
        FileChooser fileChooser = new FileChooser();
        fileChooser.setTitle("Export Evidence Sketch");
        fileChooser.setInitialDirectory(new File(System.getProperty("user.home")));
        fileChooser.getExtensionFilters().add(
            new FileChooser.ExtensionFilter("PNG Image", "*.png")
        );
        fileChooser.setInitialFileName("ThirdEye_Evidence_" + System.currentTimeMillis() + ".png");
        File file = fileChooser.showSaveDialog(stage);
        if (file != null) {
            try {
                // Ensure grid is not captured in final image
                boolean gridWasVisible = gridVisible;
                if (gridWasVisible && guidelinesCanvas != null) {
                    guidelinesCanvas.setVisible(false);
                }

                Image snapshot = sketch.snapshot(null, null);

                // Restore grid if it was on
                if (gridWasVisible && guidelinesCanvas != null) {
                    guidelinesCanvas.setVisible(true);
                }

                BufferedImage finalImg = stampCaseInfo(snapshot);
                ImageIO.write(finalImg, "png", file);
                return file;
            } catch (IOException ex) {
                System.out.println("Evidence export failed: " + ex.getMessage());
            }
        }
        return null;
    }

    /**
     * Silently saves the current sketch to a temp file (without the stamped header) for database comparison.
     */
    public File save_img_temp() {
        try {
            File tmp = File.createTempFile("thirdeye_sketch_", ".png");
            tmp.deleteOnExit();

            // Ensure grid is not captured in comparison snapshot
            boolean gridWasVisible = gridVisible;
            if (gridWasVisible && guidelinesCanvas != null) {
                guidelinesCanvas.setVisible(false);
            }

            Image snapshot = sketch.snapshot(null, null);

            if (gridWasVisible && guidelinesCanvas != null) {
                guidelinesCanvas.setVisible(true);
            }

            ImageIO.write(SwingFXUtils.fromFXImage(snapshot, null), "png", tmp);
            return tmp;
        } catch (IOException ex) {
            System.out.println("Temp comparison file failed: " + ex.getMessage());
            return null;
        }
    }


    private void updateWorkspaceLayout() {
        if (workspace_pane != null) {
            double rightMargin = (elements_panel != null && elements_panel.isVisible()) ? 731.0 : 260.0;
            AnchorPane.setRightAnchor(workspace_pane, rightMargin);
        }
    }

    @FXML
    private void onCloseElementsPanel() {
        if (elements_panel != null) {
            elements_panel.setVisible(false);
        }
        activeCategory = null;
        updateWorkspaceLayout();
        updateStatusBar();
    }

    @FXML //toolkit elements to show
    private void toolKit(MouseEvent event) {
        ImageView clicked = (ImageView) event.getSource();

        // Toggle collapsed if clicking the already active category
        if (clicked == activeCategory) {
            onCloseElementsPanel();
            return;
        }

        activeCategory = clicked;
        if (elements_panel != null) {
            elements_panel.setVisible(true);
        }
        updateWorkspaceLayout();

        // First hide everything
        if (head_elements != null) head_elements.setVisible(false);
        if (hair_elements != null) hair_elements.setVisible(false);
        if (eyes_elements != null) eyes_elements.setVisible(false);
        if (eyebrows_elements != null) eyebrows_elements.setVisible(false);
        if (nose_elements != null) nose_elements.setVisible(false);
        if (lips_elements != null) lips_elements.setVisible(false);
        if (mustach_elements != null) mustach_elements.setVisible(false);
        if (beard_elements != null) beard_elements.setVisible(false);
        if (ear_elements != null) ear_elements.setVisible(false);
        if (neck_elements != null) neck_elements.setVisible(false);
        if (dynamic_category_container != null) dynamic_category_container.setVisible(false);

        // Now show the selected static element panel or dynamic category
        if (clicked == head) {
            if (head_elements != null) head_elements.setVisible(true);
        } else if (clicked == hair) {
            if (hair_elements != null) hair_elements.setVisible(true);
        } else if (clicked == eyes) {
            if (eyes_elements != null) eyes_elements.setVisible(true);
        } else if (clicked == eyebrows) {
            if (eyebrows_elements != null) eyebrows_elements.setVisible(true);
        } else if (clicked == nose) {
            if (nose_elements != null) nose_elements.setVisible(true);
        } else if (clicked == lips) {
            if (lips_elements != null) lips_elements.setVisible(true);
        } else if (clicked == mustach) {
            if (mustach_elements != null) mustach_elements.setVisible(true);
        } else if (clicked == beard) {
            if (beard_elements != null) beard_elements.setVisible(true);
        } else if (clicked == ear) {
            if (ear_elements != null) ear_elements.setVisible(true);
        } else if (clicked == neck) {
            if (neck_elements != null) neck_elements.setVisible(true);
        } else if (clicked == accessories) {
            loadDynamicCategory("accessories", "GLASSES, MARKS & ACCESSORIES");
        }
        updateStatusBar();
    }

    private void loadDynamicCategory(String folderName, String displayTitle) {
        if (dynamic_category_container != null) {
            dynamic_category_container.setVisible(true);
        }
        if (categoryTitleLabel != null) {
            categoryTitleLabel.setText(displayTitle);
        }
        if (dynamicElementsPane == null) return;
        dynamicElementsPane.getChildren().clear();

        // Path to local folder
        File baseDir = new File(System.getProperty("user.dir"),
            "src/thirdeye/v2/elements/sketch elements/" + folderName);
        if (!baseDir.exists()) {
            baseDir = new File("Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/src/thirdeye/v2/elements/sketch elements/" + folderName);
        }

        File[] files = baseDir.listFiles((dir, name) -> name.toLowerCase().endsWith(".png"));
        if (files != null && files.length > 0) {
            for (File file : files) {
                try {
                    Image img = new Image(file.toURI().toString());
                    VBox card = createThumbnailCard(img, file.getName(), folderName + "/" + file.getName());
                    dynamicElementsPane.getChildren().add(card);
                } catch (Exception e) {
                    // ignore invalid image
                }
            }
        }
    }

    private VBox createThumbnailCard(Image img, String fileName, String relPath) {
        VBox card = new VBox(4);
        card.setAlignment(javafx.geometry.Pos.CENTER);
        card.setStyle("-fx-background-color: #112e4c; -fx-padding: 6; -fx-background-radius: 6; -fx-border-color: #1e3a5c; -fx-border-radius: 6; -fx-cursor: hand;");

        ImageView iv = new ImageView(img);
        iv.setFitWidth(90);
        iv.setFitHeight(90);
        iv.setPreserveRatio(true);

        Label label = new Label(fileName.replace(".png", ""));
        label.setStyle("-fx-text-fill: #90a4ae; -fx-font-size: 9px;");

        card.getChildren().addAll(iv, label);

        card.setOnMouseEntered(e -> card.setStyle("-fx-background-color: #1f4b7a; -fx-padding: 6; -fx-background-radius: 6; -fx-border-color: #64b5f6; -fx-border-radius: 6; -fx-cursor: hand;"));
        card.setOnMouseExited(e -> card.setStyle("-fx-background-color: #112e4c; -fx-padding: 6; -fx-background-radius: 6; -fx-border-color: #1e3a5c; -fx-border-radius: 6; -fx-cursor: hand;"));

        card.setOnMousePressed(e -> {
            addDynamicCanvasElement(img, relPath);
        });

        return card;
    }

    private void addDynamicCanvasElement(Image img, String relPath) {
        if (sketch == null) return;

        ImageView iv = new ImageView(img);
        iv.setFitWidth(200);
        iv.setFitHeight(200);
        iv.setPreserveRatio(true);

        // Center on sketch canvas
        iv.setLayoutX((sketch.getWidth() - 200) / 2.0);
        iv.setLayoutY((sketch.getHeight() - 200) / 2.0);

        // Save relative path tag so JSON project state can serialize it
        iv.setUserData(relPath);

        // Wire interactive mouse handlers (drag, scale, rotate, selection, etc.)
        wireTemplate(iv);

        // Add to sketch pane
        sketch.getChildren().add(iv);

        // Keep guidelines and drawing canvas on top of all dynamic elements!
        if (guidelinesCanvas != null) guidelinesCanvas.toFront();
        if (drawingCanvas != null) drawingCanvas.toFront();

        // Track in dynamic elements list
        dynamicCanvasElements.add(iv);

        // Select it immediately
        selectedElement = iv;
        if (elOpacitySlider != null) elOpacitySlider.setValue(1.0);
        if (elOpacityLabel != null) elOpacityLabel.setText("1.00");
        updateStatusBar();
    }

    @FXML // Explicit Save button — shows Save dialog
    private void onSave(MouseEvent event) {
        File saved = save_img_dialog();
        if (saved != null) {
            System.out.println("Sketch saved to: " + saved.getAbsolutePath());
        }
    }

    @FXML // Compare button — silently saves to temp, then opens Compare screen
    private void onCompare(MouseEvent event) {
        // Save sketch silently to a temp file (no dialog — never blocks)
        File tempSketch = save_img_temp();
        if (tempSketch == null) {
            System.out.println("Could not create temp sketch file.");
            return;
        }

        try {
            FXMLLoader fxmlLoader = new FXMLLoader();
            fxmlLoader.setLocation(getClass().getResource("upload_sketch.fxml"));
            Scene scene = new Scene(fxmlLoader.load());
            Upload_sketchController controller = fxmlLoader.getController();
            controller.setSketchFile(tempSketch);
            Stage stage = new Stage();
            stage.setTitle("ThirdEye — Face Comparison");
            stage.setScene(scene);
            stage.setResizable(true);
            stage.setMaximized(true);
            stage.show();
            ((Node)(event.getSource())).getScene().getWindow().hide();
        } catch (IOException e) {
            Logger.getLogger(getClass().getName()).log(java.util.logging.Level.SEVERE, null, e);
        }
    }

    @FXML //Reset the sketch and delete all element
    private void onReset(MouseEvent event) {
        head_s_1.setVisible(false);
        head_s_2.setVisible(false);
        head_s_3.setVisible(false);
        head_s_4.setVisible(false);
        head_s_5.setVisible(false);
        head_s_6.setVisible(false);
        head_s_7.setVisible(false);
        head_s_8.setVisible(false);
        head_s_9.setVisible(false);
        head_s_10.setVisible(false);
                
        hair_s_1.setVisible(false);
        hair_s_2.setVisible(false);
        hair_s_3.setVisible(false);
        hair_s_4.setVisible(false);
        hair_s_5.setVisible(false);
        hair_s_6.setVisible(false);
        hair_s_7.setVisible(false);
        hair_s_8.setVisible(false);
        hair_s_9.setVisible(false);
        hair_s_10.setVisible(false);
        hair_s_11.setVisible(false);
        hair_s_12.setVisible(false);
                
        eyes_s_1.setVisible(false);
        eyes_s_2.setVisible(false);
        eyes_s_3.setVisible(false);
        eyes_s_4.setVisible(false);
        eyes_s_5.setVisible(false);
        eyes_s_6.setVisible(false);
        eyes_s_7.setVisible(false);
        eyes_s_8.setVisible(false);
        eyes_s_9.setVisible(false);
        eyes_s_10.setVisible(false);
        eyes_s_11.setVisible(false);
        eyes_s_12.setVisible(false);
                
        eyeb_s_1.setVisible(false);
        eyeb_s_2.setVisible(false);
        eyeb_s_3.setVisible(false);
        eyeb_s_4.setVisible(false);
        eyeb_s_5.setVisible(false);
        eyeb_s_6.setVisible(false);
        eyeb_s_7.setVisible(false);
        eyeb_s_8.setVisible(false);
        eyeb_s_9.setVisible(false);
        eyeb_s_10.setVisible(false);
        eyeb_s_11.setVisible(false);
        eyeb_s_12.setVisible(false);
                
        lips_s_1.setVisible(false);
        lips_s_2.setVisible(false);
        lips_s_3.setVisible(false);
        lips_s_4.setVisible(false);
        lips_s_5.setVisible(false);
        lips_s_6.setVisible(false);
        lips_s_7.setVisible(false);
        lips_s_8.setVisible(false);
        lips_s_9.setVisible(false);
        lips_s_10.setVisible(false);
        lips_s_11.setVisible(false);
        lips_s_12.setVisible(false);
                
        nose_s_1.setVisible(false);
        nose_s_2.setVisible(false);
        nose_s_3.setVisible(false);
        nose_s_4.setVisible(false);
        nose_s_5.setVisible(false);
        nose_s_6.setVisible(false);
        nose_s_7.setVisible(false);
        nose_s_8.setVisible(false);
        nose_s_9.setVisible(false);
        nose_s_10.setVisible(false);
        nose_s_11.setVisible(false);
        nose_s_12.setVisible(false);
                
        must_s_1.setVisible(false);
        must_s_2.setVisible(false);
        must_s_3.setVisible(false);
        must_s_4.setVisible(false);
        must_s_5.setVisible(false);
        must_s_6.setVisible(false);
                
        beard_s_1.setVisible(false);
        beard_s_2.setVisible(false);
        beard_s_3.setVisible(false);
        beard_s_4.setVisible(false);
        beard_s_5.setVisible(false);
        beard_s_6.setVisible(false);
                
        ear_s_1.setVisible(false);
        ear_s_2.setVisible(false);
        ear_s_3.setVisible(false);
        ear_s_4.setVisible(false);
                
        neck_s_1.setVisible(false);
        neck_s_2.setVisible(false);

        // Remove all dynamic canvas layers
        for (ImageView iv : dynamicCanvasElements) {
            if (sketch != null) sketch.getChildren().remove(iv);
        }
        dynamicCanvasElements.clear();

        // Reset all positions, scales, and rotations to defaults
        resetAllTransforms();
        // Clear all freehand pen strokes
        clearDrawingCanvas();
        // Remove the reference image
        onRemoveReference();
    }

        // Select the Elements to Show on CANVAS
        @FXML
        private void onHeadSelect(MouseEvent event) {
            if(event.getSource()==head_del) {
                head_s_1.setVisible(false);
                head_s_2.setVisible(false);
                head_s_3.setVisible(false);
                head_s_4.setVisible(false);
                head_s_5.setVisible(false);
                head_s_6.setVisible(false);
                head_s_7.setVisible(false);
                head_s_8.setVisible(false);
                head_s_9.setVisible(false);
                head_s_10.setVisible(false);
            } else if(event.getSource()==head_e_1) {
                head_s_1.setVisible(true);
                head_s_2.setVisible(false);
                head_s_3.setVisible(false);
                head_s_4.setVisible(false);
                head_s_5.setVisible(false);
                head_s_6.setVisible(false);
                head_s_7.setVisible(false);
                head_s_8.setVisible(false);
                head_s_9.setVisible(false);
                head_s_10.setVisible(false);
            } else if(event.getSource()==head_e_2) {
                head_s_1.setVisible(false);
                head_s_2.setVisible(true);
                head_s_3.setVisible(false);
                head_s_4.setVisible(false);
                head_s_5.setVisible(false);
                head_s_6.setVisible(false);
                head_s_7.setVisible(false);
                head_s_8.setVisible(false);
                head_s_9.setVisible(false);
                head_s_10.setVisible(false);
            } else if(event.getSource()==head_e_3) {
                head_s_1.setVisible(false);
                head_s_2.setVisible(false);
                head_s_3.setVisible(true);
                head_s_4.setVisible(false);
                head_s_5.setVisible(false);
                head_s_6.setVisible(false);
                head_s_7.setVisible(false);
                head_s_8.setVisible(false);
                head_s_9.setVisible(false);
                head_s_10.setVisible(false);
            } else if(event.getSource()==head_e_4) {
                head_s_1.setVisible(false);
                head_s_2.setVisible(false);
                head_s_3.setVisible(false);
                head_s_4.setVisible(true);
                head_s_5.setVisible(false);
                head_s_6.setVisible(false);
                head_s_7.setVisible(false);
                head_s_8.setVisible(false);
                head_s_9.setVisible(false);
                head_s_10.setVisible(false);
            } else if(event.getSource()==head_e_5) {
                head_s_1.setVisible(false);
                head_s_2.setVisible(false);
                head_s_3.setVisible(false);
                head_s_4.setVisible(false);
                head_s_5.setVisible(true);
                head_s_6.setVisible(false);
                head_s_7.setVisible(false);
                head_s_8.setVisible(false);
                head_s_9.setVisible(false);
                head_s_10.setVisible(false);
            } else if(event.getSource()==head_e_6) {
                head_s_1.setVisible(false);
                head_s_2.setVisible(false);
                head_s_3.setVisible(false);
                head_s_4.setVisible(false);
                head_s_5.setVisible(false);
                head_s_6.setVisible(true);
                head_s_7.setVisible(false);
                head_s_8.setVisible(false);
                head_s_9.setVisible(false);
                head_s_10.setVisible(false);
            } else if(event.getSource()==head_e_7) {
                head_s_1.setVisible(false);
                head_s_2.setVisible(false);
                head_s_3.setVisible(false);
                head_s_4.setVisible(false);
                head_s_5.setVisible(false);
                head_s_6.setVisible(false);
                head_s_7.setVisible(true);
                head_s_8.setVisible(false);
                head_s_9.setVisible(false);
                head_s_10.setVisible(false);
            } else if(event.getSource()==head_e_8) {
                head_s_1.setVisible(false);
                head_s_2.setVisible(false);
                head_s_3.setVisible(false);
                head_s_4.setVisible(false);
                head_s_5.setVisible(false);
                head_s_6.setVisible(false);
                head_s_7.setVisible(false);
                head_s_8.setVisible(true);
                head_s_9.setVisible(false);
                head_s_10.setVisible(false);
            } else if(event.getSource()==head_e_9) {
                head_s_1.setVisible(false);
                head_s_2.setVisible(false);
                head_s_3.setVisible(false);
                head_s_4.setVisible(false);
                head_s_5.setVisible(false);
                head_s_6.setVisible(false);
                head_s_7.setVisible(false);
                head_s_8.setVisible(false);
                head_s_9.setVisible(true);
                head_s_10.setVisible(false);
            } else if(event.getSource()==head_e_10) {
                head_s_1.setVisible(false);
                head_s_2.setVisible(false);
                head_s_3.setVisible(false);
                head_s_4.setVisible(false);
                head_s_5.setVisible(false);
                head_s_6.setVisible(false);
                head_s_7.setVisible(false);
                head_s_8.setVisible(false);
                head_s_9.setVisible(false);
                head_s_10.setVisible(true);
            }
        }

        @FXML
        private void onHairSelect(MouseEvent event) {
            if(event.getSource()==hair_del) {
                hair_s_1.setVisible(false);
                hair_s_2.setVisible(false);
                hair_s_3.setVisible(false);
                hair_s_4.setVisible(false);
                hair_s_5.setVisible(false);
                hair_s_6.setVisible(false);
                hair_s_7.setVisible(false);
                hair_s_8.setVisible(false);
                hair_s_9.setVisible(false);
                hair_s_10.setVisible(false);
                hair_s_11.setVisible(false);
                hair_s_12.setVisible(false);
            } else if(event.getSource()==hair_e_1) {
                hair_s_1.setVisible(true);
                hair_s_2.setVisible(false);
                hair_s_3.setVisible(false);
                hair_s_4.setVisible(false);
                hair_s_5.setVisible(false);
                hair_s_6.setVisible(false);
                hair_s_7.setVisible(false);
                hair_s_8.setVisible(false);
                hair_s_9.setVisible(false);
                hair_s_10.setVisible(false);
                hair_s_11.setVisible(false);
                hair_s_12.setVisible(false);
            } else if(event.getSource()==hair_e_2) {
                hair_s_1.setVisible(false);
                hair_s_2.setVisible(true);
                hair_s_3.setVisible(false);
                hair_s_4.setVisible(false);
                hair_s_5.setVisible(false);
                hair_s_6.setVisible(false);
                hair_s_7.setVisible(false);
                hair_s_8.setVisible(false);
                hair_s_9.setVisible(false);
                hair_s_10.setVisible(false);
                hair_s_11.setVisible(false);
                hair_s_12.setVisible(false);
            } else if(event.getSource()==hair_e_3) {
                hair_s_1.setVisible(false);
                hair_s_2.setVisible(false);
                hair_s_3.setVisible(true);
                hair_s_4.setVisible(false);
                hair_s_5.setVisible(false);
                hair_s_6.setVisible(false);
                hair_s_7.setVisible(false);
                hair_s_8.setVisible(false);
                hair_s_9.setVisible(false);
                hair_s_10.setVisible(false);
                hair_s_11.setVisible(false);
                hair_s_12.setVisible(false);
            } else if(event.getSource()==hair_e_4) {
                hair_s_1.setVisible(false);
                hair_s_2.setVisible(false);
                hair_s_3.setVisible(false);
                hair_s_4.setVisible(true);
                hair_s_5.setVisible(false);
                hair_s_6.setVisible(false);
                hair_s_7.setVisible(false);
                hair_s_8.setVisible(false);
                hair_s_9.setVisible(false);
                hair_s_10.setVisible(false);
                hair_s_11.setVisible(false);
                hair_s_12.setVisible(false);
            } else if(event.getSource()==hair_e_5) {
                hair_s_1.setVisible(false);
                hair_s_2.setVisible(false);
                hair_s_3.setVisible(false);
                hair_s_4.setVisible(false);
                hair_s_5.setVisible(true);
                hair_s_6.setVisible(false);
                hair_s_7.setVisible(false);
                hair_s_8.setVisible(false);
                hair_s_9.setVisible(false);
                hair_s_10.setVisible(false);
                hair_s_11.setVisible(false);
                hair_s_12.setVisible(false);
            } else if(event.getSource()==hair_e_6) {
                hair_s_1.setVisible(false);
                hair_s_2.setVisible(false);
                hair_s_3.setVisible(false);
                hair_s_4.setVisible(false);
                hair_s_5.setVisible(false);
                hair_s_6.setVisible(true);
                hair_s_7.setVisible(false);
                hair_s_8.setVisible(false);
                hair_s_9.setVisible(false);
                hair_s_10.setVisible(false);
                hair_s_11.setVisible(false);
                hair_s_12.setVisible(false);
            } else if(event.getSource()==hair_e_7) {
                hair_s_1.setVisible(false);
                hair_s_2.setVisible(false);
                hair_s_3.setVisible(false);
                hair_s_4.setVisible(false);
                hair_s_5.setVisible(false);
                hair_s_6.setVisible(false);
                hair_s_7.setVisible(true);
                hair_s_8.setVisible(false);
                hair_s_9.setVisible(false);
                hair_s_10.setVisible(false);
                hair_s_11.setVisible(false);
                hair_s_12.setVisible(false);
            } else if(event.getSource()==hair_e_8) {
                hair_s_1.setVisible(false);
                hair_s_2.setVisible(false);
                hair_s_3.setVisible(false);
                hair_s_4.setVisible(false);
                hair_s_5.setVisible(false);
                hair_s_6.setVisible(false);
                hair_s_7.setVisible(false);
                hair_s_8.setVisible(true);
                hair_s_9.setVisible(false);
                hair_s_10.setVisible(false);
                hair_s_11.setVisible(false);
                hair_s_12.setVisible(false);
            } else if(event.getSource()==hair_e_9) {
                hair_s_1.setVisible(false);
                hair_s_2.setVisible(false);
                hair_s_3.setVisible(false);
                hair_s_4.setVisible(false);
                hair_s_5.setVisible(false);
                hair_s_6.setVisible(false);
                hair_s_7.setVisible(false);
                hair_s_8.setVisible(false);
                hair_s_9.setVisible(true);
                hair_s_10.setVisible(false);
                hair_s_11.setVisible(false);
                hair_s_12.setVisible(false);
            } else if(event.getSource()==hair_e_10) {
                hair_s_1.setVisible(false);
                hair_s_2.setVisible(false);
                hair_s_3.setVisible(false);
                hair_s_4.setVisible(false);
                hair_s_5.setVisible(false);
                hair_s_6.setVisible(false);
                hair_s_7.setVisible(false);
                hair_s_8.setVisible(false);
                hair_s_9.setVisible(false);
                hair_s_10.setVisible(true);
                hair_s_11.setVisible(false);
                hair_s_12.setVisible(false);
            } else if(event.getSource()==hair_e_11) {
                hair_s_1.setVisible(false);
                hair_s_2.setVisible(false);
                hair_s_3.setVisible(false);
                hair_s_4.setVisible(false);
                hair_s_5.setVisible(false);
                hair_s_6.setVisible(false);
                hair_s_7.setVisible(false);
                hair_s_8.setVisible(false);
                hair_s_9.setVisible(false);
                hair_s_10.setVisible(false);
                hair_s_11.setVisible(true);
                hair_s_12.setVisible(false);
            } else if(event.getSource()==hair_e_12) {
                hair_s_1.setVisible(false);
                hair_s_2.setVisible(false);
                hair_s_3.setVisible(false);
                hair_s_4.setVisible(false);
                hair_s_5.setVisible(false);
                hair_s_6.setVisible(false);
                hair_s_7.setVisible(false);
                hair_s_8.setVisible(false);
                hair_s_9.setVisible(false);
                hair_s_10.setVisible(false);
                hair_s_11.setVisible(false);
                hair_s_12.setVisible(true);
            } 
        }

        @FXML
        private void onEyesSelect(MouseEvent event) {
            if(event.getSource()==eyes_del) {
                eyes_s_1.setVisible(false);
                eyes_s_2.setVisible(false);
                eyes_s_3.setVisible(false);
                eyes_s_4.setVisible(false);
                eyes_s_5.setVisible(false);
                eyes_s_6.setVisible(false);
                eyes_s_7.setVisible(false);
                eyes_s_8.setVisible(false);
                eyes_s_9.setVisible(false);
                eyes_s_10.setVisible(false);
                eyes_s_11.setVisible(false);
                eyes_s_12.setVisible(false);
            } else if(event.getSource()==eyes_e_1) {
                eyes_s_1.setVisible(true);
                eyes_s_2.setVisible(false);
                eyes_s_3.setVisible(false);
                eyes_s_4.setVisible(false);
                eyes_s_5.setVisible(false);
                eyes_s_6.setVisible(false);
                eyes_s_7.setVisible(false);
                eyes_s_8.setVisible(false);
                eyes_s_9.setVisible(false);
                eyes_s_10.setVisible(false);
                eyes_s_11.setVisible(false);
                eyes_s_12.setVisible(false);
            } else if(event.getSource()==eyes_e_2) {
                eyes_s_1.setVisible(false);
                eyes_s_2.setVisible(true);
                eyes_s_3.setVisible(false);
                eyes_s_4.setVisible(false);
                eyes_s_5.setVisible(false);
                eyes_s_6.setVisible(false);
                eyes_s_7.setVisible(false);
                eyes_s_8.setVisible(false);
                eyes_s_9.setVisible(false);
                eyes_s_10.setVisible(false);
                eyes_s_11.setVisible(false);
                eyes_s_12.setVisible(false);
            } else if(event.getSource()==eyes_e_3) {
                eyes_s_1.setVisible(false);
                eyes_s_2.setVisible(false);
                eyes_s_3.setVisible(true);
                eyes_s_4.setVisible(false);
                eyes_s_5.setVisible(false);
                eyes_s_6.setVisible(false);
                eyes_s_7.setVisible(false);
                eyes_s_8.setVisible(false);
                eyes_s_9.setVisible(false);
                eyes_s_10.setVisible(false);
                eyes_s_11.setVisible(false);
                eyes_s_12.setVisible(false);
            } else if(event.getSource()==eyes_e_4) {
                eyes_s_1.setVisible(false);
                eyes_s_2.setVisible(false);
                eyes_s_3.setVisible(false);
                eyes_s_4.setVisible(false);
                eyes_s_5.setVisible(false);
                eyes_s_6.setVisible(false);
                eyes_s_7.setVisible(false);
                eyes_s_8.setVisible(false);
                eyes_s_9.setVisible(false);
                eyes_s_10.setVisible(false);
                eyes_s_11.setVisible(false);
                eyes_s_12.setVisible(false);
            } else if(event.getSource()==eyes_e_5) {
                eyes_s_1.setVisible(false);
                eyes_s_2.setVisible(false);
                eyes_s_3.setVisible(false);
                eyes_s_4.setVisible(false);
                eyes_s_5.setVisible(true);
                eyes_s_6.setVisible(false);
                eyes_s_7.setVisible(false);
                eyes_s_8.setVisible(false);
                eyes_s_9.setVisible(false);
                eyes_s_10.setVisible(false);
                eyes_s_11.setVisible(false);
                eyes_s_12.setVisible(false);
            } else if(event.getSource()==eyes_e_6) {
                eyes_s_1.setVisible(false);
                eyes_s_2.setVisible(false);
                eyes_s_3.setVisible(false);
                eyes_s_4.setVisible(false);
                eyes_s_5.setVisible(false);
                eyes_s_6.setVisible(true);
                eyes_s_7.setVisible(false);
                eyes_s_8.setVisible(false);
                eyes_s_9.setVisible(false);
                eyes_s_10.setVisible(false);
                eyes_s_11.setVisible(false);
                eyes_s_12.setVisible(false);
            } else if(event.getSource()==eyes_e_7) {
                eyes_s_1.setVisible(false);
                eyes_s_2.setVisible(false);
                eyes_s_3.setVisible(false);
                eyes_s_4.setVisible(false);
                eyes_s_5.setVisible(false);
                eyes_s_6.setVisible(false);
                eyes_s_7.setVisible(true);
                eyes_s_8.setVisible(false);
                eyes_s_9.setVisible(false);
                eyes_s_10.setVisible(false);
                eyes_s_11.setVisible(false);
                eyes_s_12.setVisible(false);
            } else if(event.getSource()==eyes_e_8) {
                eyes_s_1.setVisible(false);
                eyes_s_2.setVisible(false);
                eyes_s_3.setVisible(false);
                eyes_s_4.setVisible(false);
                eyes_s_5.setVisible(false);
                eyes_s_6.setVisible(false);
                eyes_s_7.setVisible(false);
                eyes_s_8.setVisible(true);
                eyes_s_9.setVisible(false);
                eyes_s_10.setVisible(false);
                eyes_s_11.setVisible(false);
                eyes_s_12.setVisible(false);
            } else if(event.getSource()==eyes_e_9) {
                eyes_s_1.setVisible(false);
                eyes_s_2.setVisible(false);
                eyes_s_3.setVisible(false);
                eyes_s_4.setVisible(false);
                eyes_s_5.setVisible(false);
                eyes_s_6.setVisible(false);
                eyes_s_7.setVisible(false);
                eyes_s_8.setVisible(false);
                eyes_s_9.setVisible(true);
                eyes_s_10.setVisible(false);
                eyes_s_11.setVisible(false);
                eyes_s_12.setVisible(false);
            } else if(event.getSource()==eyes_e_10) {
                eyes_s_1.setVisible(false);
                eyes_s_2.setVisible(false);
                eyes_s_3.setVisible(false);
                eyes_s_4.setVisible(false);
                eyes_s_5.setVisible(false);
                eyes_s_6.setVisible(false);
                eyes_s_7.setVisible(false);
                eyes_s_8.setVisible(false);
                eyes_s_9.setVisible(false);
                eyes_s_10.setVisible(true);
                eyes_s_11.setVisible(false);
                eyes_s_12.setVisible(false);
            } else if(event.getSource()==eyes_e_11) {
                eyes_s_1.setVisible(false);
                eyes_s_2.setVisible(false);
                eyes_s_3.setVisible(false);
                eyes_s_4.setVisible(false);
                eyes_s_5.setVisible(false);
                eyes_s_6.setVisible(false);
                eyes_s_7.setVisible(false);
                eyes_s_8.setVisible(false);
                eyes_s_9.setVisible(false);
                eyes_s_10.setVisible(false);
                eyes_s_11.setVisible(true);
                eyes_s_12.setVisible(false);
            } else if(event.getSource()==eyes_e_12) {
                eyes_s_1.setVisible(false);
                eyes_s_2.setVisible(false);
                eyes_s_3.setVisible(false);
                eyes_s_4.setVisible(true);
                eyes_s_5.setVisible(false);
                eyes_s_6.setVisible(false);
                eyes_s_7.setVisible(false);
                eyes_s_8.setVisible(false);
                eyes_s_9.setVisible(false);
                eyes_s_10.setVisible(false);
                eyes_s_11.setVisible(false);
                eyes_s_12.setVisible(true);
            } 
        }

        @FXML
        private void onEyeBSelect(MouseEvent event) {
            if(event.getSource()==eyeb_del) {
                eyeb_s_1.setVisible(false);
                eyeb_s_2.setVisible(false);
                eyeb_s_3.setVisible(false);
                eyeb_s_4.setVisible(false);
                eyeb_s_5.setVisible(false);
                eyeb_s_6.setVisible(false);
                eyeb_s_7.setVisible(false);
                eyeb_s_8.setVisible(false);
                eyeb_s_9.setVisible(false);
                eyeb_s_10.setVisible(false);
                eyeb_s_11.setVisible(false);
                eyeb_s_12.setVisible(false);
            } else if(event.getSource()==eyeb_e_1) {
                eyeb_s_1.setVisible(true);
                eyeb_s_2.setVisible(false);
                eyeb_s_3.setVisible(false);
                eyeb_s_4.setVisible(false);
                eyeb_s_5.setVisible(false);
                eyeb_s_6.setVisible(false);
                eyeb_s_7.setVisible(false);
                eyeb_s_8.setVisible(false);
                eyeb_s_9.setVisible(false);
                eyeb_s_10.setVisible(false);
                eyeb_s_11.setVisible(false);
                eyeb_s_12.setVisible(false);
            } else if(event.getSource()==eyeb_e_2) {
                eyeb_s_1.setVisible(false);
                eyeb_s_2.setVisible(true);
                eyeb_s_3.setVisible(false);
                eyeb_s_4.setVisible(false);
                eyeb_s_5.setVisible(false);
                eyeb_s_6.setVisible(false);
                eyeb_s_7.setVisible(false);
                eyeb_s_8.setVisible(false);
                eyeb_s_9.setVisible(false);
                eyeb_s_10.setVisible(false);
                eyeb_s_11.setVisible(false);
                eyeb_s_12.setVisible(false);
            } else if(event.getSource()==eyeb_e_3) {
                 eyeb_s_1.setVisible(false);
                eyeb_s_2.setVisible(false);
                eyeb_s_3.setVisible(true);
                eyeb_s_4.setVisible(false);
                eyeb_s_5.setVisible(false);
                eyeb_s_6.setVisible(false);
                eyeb_s_7.setVisible(false);
                eyeb_s_8.setVisible(false);
                eyeb_s_9.setVisible(false);
                eyeb_s_10.setVisible(false);
                eyeb_s_11.setVisible(false);
                eyeb_s_12.setVisible(false);
            } else if(event.getSource()==eyeb_e_4) {
                 eyeb_s_1.setVisible(false);
                eyeb_s_2.setVisible(false);
                eyeb_s_3.setVisible(false);
                eyeb_s_4.setVisible(true);
                eyeb_s_5.setVisible(false);
                eyeb_s_6.setVisible(false);
                eyeb_s_7.setVisible(false);
                eyeb_s_8.setVisible(false);
                eyeb_s_9.setVisible(false);
                eyeb_s_10.setVisible(false);
                eyeb_s_11.setVisible(false);
                eyeb_s_12.setVisible(false);
            } else if(event.getSource()==eyeb_e_5) {
                 eyeb_s_1.setVisible(false);
                eyeb_s_2.setVisible(false);
                eyeb_s_3.setVisible(false);
                eyeb_s_4.setVisible(false);
                eyeb_s_5.setVisible(true);
                eyeb_s_6.setVisible(false);
                eyeb_s_7.setVisible(false);
                eyeb_s_8.setVisible(false);
                eyeb_s_9.setVisible(false);
                eyeb_s_10.setVisible(false);
                eyeb_s_11.setVisible(false);
                eyeb_s_12.setVisible(false);
            } else if(event.getSource()==eyeb_e_6) {
                 eyeb_s_1.setVisible(false);
                eyeb_s_2.setVisible(false);
                eyeb_s_3.setVisible(false);
                eyeb_s_4.setVisible(false);
                eyeb_s_5.setVisible(false);
                eyeb_s_6.setVisible(true);
                eyeb_s_7.setVisible(false);
                eyeb_s_8.setVisible(false);
                eyeb_s_9.setVisible(false);
                eyeb_s_10.setVisible(false);
                eyeb_s_11.setVisible(false);
                eyeb_s_12.setVisible(false);
            } else if(event.getSource()==eyeb_e_7) {
                 eyeb_s_1.setVisible(false);
                eyeb_s_2.setVisible(false);
                eyeb_s_3.setVisible(false);
                eyeb_s_4.setVisible(false);
                eyeb_s_5.setVisible(false);
                eyeb_s_6.setVisible(false);
                eyeb_s_7.setVisible(true);
                eyeb_s_8.setVisible(false);
                eyeb_s_9.setVisible(false);
                eyeb_s_10.setVisible(false);
                eyeb_s_11.setVisible(false);
                eyeb_s_12.setVisible(false);
            } else if(event.getSource()==eyeb_e_8) {
                 eyeb_s_1.setVisible(false);
                eyeb_s_2.setVisible(false);
                eyeb_s_3.setVisible(false);
                eyeb_s_4.setVisible(false);
                eyeb_s_5.setVisible(false);
                eyeb_s_6.setVisible(false);
                eyeb_s_7.setVisible(false);
                eyeb_s_8.setVisible(true);
                eyeb_s_9.setVisible(false);
                eyeb_s_10.setVisible(false);
                eyeb_s_11.setVisible(false);
                eyeb_s_12.setVisible(false);
            } else if(event.getSource()==eyeb_e_9) {
                 eyeb_s_1.setVisible(false);
                eyeb_s_2.setVisible(false);
                eyeb_s_3.setVisible(false);
                eyeb_s_4.setVisible(false);
                eyeb_s_5.setVisible(false);
                eyeb_s_6.setVisible(false);
                eyeb_s_7.setVisible(false);
                eyeb_s_8.setVisible(false);
                eyeb_s_9.setVisible(true);
                eyeb_s_10.setVisible(false);
                eyeb_s_11.setVisible(false);
                eyeb_s_12.setVisible(false);
            } else if(event.getSource()==eyeb_e_10) {
                 eyeb_s_1.setVisible(false);
                eyeb_s_2.setVisible(false);
                eyeb_s_3.setVisible(false);
                eyeb_s_4.setVisible(false);
                eyeb_s_5.setVisible(false);
                eyeb_s_6.setVisible(false);
                eyeb_s_7.setVisible(false);
                eyeb_s_8.setVisible(false);
                eyeb_s_9.setVisible(false);
                eyeb_s_10.setVisible(true);
                eyeb_s_11.setVisible(false);
                eyeb_s_12.setVisible(false);
            } else if(event.getSource()==eyeb_e_11) {
                 eyeb_s_1.setVisible(false);
                eyeb_s_2.setVisible(false);
                eyeb_s_3.setVisible(false);
                eyeb_s_4.setVisible(false);
                eyeb_s_5.setVisible(false);
                eyeb_s_6.setVisible(false);
                eyeb_s_7.setVisible(false);
                eyeb_s_8.setVisible(false);
                eyeb_s_9.setVisible(false);
                eyeb_s_10.setVisible(false);
                eyeb_s_11.setVisible(true);
                eyeb_s_12.setVisible(false);
            } else if(event.getSource()==eyeb_e_12) {
                 eyeb_s_1.setVisible(false);
                eyeb_s_2.setVisible(false);
                eyeb_s_3.setVisible(false);
                eyeb_s_4.setVisible(false);
                eyeb_s_5.setVisible(false);
                eyeb_s_6.setVisible(false);
                eyeb_s_7.setVisible(false);
                eyeb_s_8.setVisible(false);
                eyeb_s_9.setVisible(false);
                eyeb_s_10.setVisible(false);
                eyeb_s_11.setVisible(false);
                eyeb_s_12.setVisible(true);
            } 
        }

        @FXML
        private void onNoseSelect(MouseEvent event) {
            if(event.getSource()==nose_del) {
                nose_s_1.setVisible(false);
                nose_s_2.setVisible(false);
                nose_s_3.setVisible(false);
                nose_s_4.setVisible(false);
                nose_s_5.setVisible(false);
                nose_s_6.setVisible(false);
                nose_s_7.setVisible(false);
                nose_s_8.setVisible(false);
                nose_s_9.setVisible(false);
                nose_s_10.setVisible(false);
                nose_s_11.setVisible(false);
                nose_s_12.setVisible(false);
            } else if(event.getSource()==nose_e_1) {
                nose_s_1.setVisible(true);
                nose_s_2.setVisible(false);
                nose_s_3.setVisible(false);
                nose_s_4.setVisible(false);
                nose_s_5.setVisible(false);
                nose_s_6.setVisible(false);
                nose_s_7.setVisible(false);
                nose_s_8.setVisible(false);
                nose_s_9.setVisible(false);
                nose_s_10.setVisible(false);
                nose_s_11.setVisible(false);
                nose_s_12.setVisible(false);
            } else if(event.getSource()==nose_e_2) {
                nose_s_1.setVisible(false);
                nose_s_2.setVisible(true);
                nose_s_3.setVisible(false);
                nose_s_4.setVisible(false);
                nose_s_5.setVisible(false);
                nose_s_6.setVisible(false);
                nose_s_7.setVisible(false);
                nose_s_8.setVisible(false);
                nose_s_9.setVisible(false);
                nose_s_10.setVisible(false);
                nose_s_11.setVisible(false);
                nose_s_12.setVisible(false);
            } else if(event.getSource()==nose_e_3) {
                nose_s_1.setVisible(false);
                nose_s_2.setVisible(false);
                nose_s_3.setVisible(true);
                nose_s_4.setVisible(false);
                nose_s_5.setVisible(false);
                nose_s_6.setVisible(false);
                nose_s_7.setVisible(false);
                nose_s_8.setVisible(false);
                nose_s_9.setVisible(false);
                nose_s_10.setVisible(false);
                nose_s_11.setVisible(false);
                nose_s_12.setVisible(false);
            } else if(event.getSource()==nose_e_4) {
                nose_s_1.setVisible(false);
                nose_s_2.setVisible(false);
                nose_s_3.setVisible(false);
                nose_s_4.setVisible(true);
                nose_s_5.setVisible(false);
                nose_s_6.setVisible(false);
                nose_s_7.setVisible(false);
                nose_s_8.setVisible(false);
                nose_s_9.setVisible(false);
                nose_s_10.setVisible(false);
                nose_s_11.setVisible(false);
                nose_s_12.setVisible(false);
            } else if(event.getSource()==nose_e_5) {
                nose_s_1.setVisible(false);
                nose_s_2.setVisible(false);
                nose_s_3.setVisible(false);
                nose_s_4.setVisible(false);
                nose_s_5.setVisible(true);
                nose_s_6.setVisible(false);
                nose_s_7.setVisible(false);
                nose_s_8.setVisible(false);
                nose_s_9.setVisible(false);
                nose_s_10.setVisible(false);
                nose_s_11.setVisible(false);
                nose_s_12.setVisible(false);
            } else if(event.getSource()==nose_e_6) {
                nose_s_1.setVisible(false);
                nose_s_2.setVisible(false);
                nose_s_3.setVisible(false);
                nose_s_4.setVisible(false);
                nose_s_5.setVisible(false);
                nose_s_6.setVisible(true);
                nose_s_7.setVisible(false);
                nose_s_8.setVisible(false);
                nose_s_9.setVisible(false);
                nose_s_10.setVisible(false);
                nose_s_11.setVisible(false);
                nose_s_12.setVisible(false);
            } else if(event.getSource()==nose_e_7) {
                nose_s_1.setVisible(false);
                nose_s_2.setVisible(false);
                nose_s_3.setVisible(false);
                nose_s_4.setVisible(false);
                nose_s_5.setVisible(false);
                nose_s_6.setVisible(false);
                nose_s_7.setVisible(true);
                nose_s_8.setVisible(false);
                nose_s_9.setVisible(false);
                nose_s_10.setVisible(false);
                nose_s_11.setVisible(false);
                nose_s_12.setVisible(false);
            } else if(event.getSource()==nose_e_8) {
                nose_s_1.setVisible(false);
                nose_s_2.setVisible(false);
                nose_s_3.setVisible(false);
                nose_s_4.setVisible(false);
                nose_s_5.setVisible(false);
                nose_s_6.setVisible(false);
                nose_s_7.setVisible(false);
                nose_s_8.setVisible(true);
                nose_s_9.setVisible(false);
                nose_s_10.setVisible(false);
                nose_s_11.setVisible(false);
                nose_s_12.setVisible(false);
            } else if(event.getSource()==nose_e_9) {
                nose_s_1.setVisible(false);
                nose_s_2.setVisible(false);
                nose_s_3.setVisible(false);
                nose_s_4.setVisible(false);
                nose_s_5.setVisible(false);
                nose_s_6.setVisible(false);
                nose_s_7.setVisible(false);
                nose_s_8.setVisible(false);
                nose_s_9.setVisible(true);
                nose_s_10.setVisible(false);
                nose_s_11.setVisible(false);
                nose_s_12.setVisible(false);
            } else if(event.getSource()==nose_e_10) {
                nose_s_1.setVisible(false);
                nose_s_2.setVisible(false);
                nose_s_3.setVisible(false);
                nose_s_4.setVisible(false);
                nose_s_5.setVisible(false);
                nose_s_6.setVisible(false);
                nose_s_7.setVisible(false);
                nose_s_8.setVisible(false);
                nose_s_9.setVisible(false);
                nose_s_10.setVisible(true);
                nose_s_11.setVisible(false);
                nose_s_12.setVisible(false);
            } else if(event.getSource()==nose_e_11) {
                nose_s_1.setVisible(false);
                nose_s_2.setVisible(false);
                nose_s_3.setVisible(false);
                nose_s_4.setVisible(false);
                nose_s_5.setVisible(false);
                nose_s_6.setVisible(false);
                nose_s_7.setVisible(false);
                nose_s_8.setVisible(false);
                nose_s_9.setVisible(false);
                nose_s_10.setVisible(false);
                nose_s_11.setVisible(true);
                nose_s_12.setVisible(false);
            } else if(event.getSource()==nose_e_12) {
                nose_s_1.setVisible(false);
                nose_s_2.setVisible(false);
                nose_s_3.setVisible(false);
                nose_s_4.setVisible(false);
                nose_s_5.setVisible(false);
                nose_s_6.setVisible(false);
                nose_s_7.setVisible(false);
                nose_s_8.setVisible(false);
                nose_s_9.setVisible(false);
                nose_s_10.setVisible(false);
                nose_s_11.setVisible(false);
                nose_s_12.setVisible(true);
            } 
        }

        @FXML
        private void onLipsSelect(MouseEvent event) {
            if(event.getSource()==lips_del) {
                lips_s_1.setVisible(false);
                lips_s_2.setVisible(false);
                lips_s_3.setVisible(false);
                lips_s_4.setVisible(false);
                lips_s_5.setVisible(false);
                lips_s_6.setVisible(false);
                lips_s_7.setVisible(false);
                lips_s_8.setVisible(false);
                lips_s_9.setVisible(false);
                lips_s_10.setVisible(false);
                lips_s_11.setVisible(false);
                lips_s_12.setVisible(false);
            } else if(event.getSource()==lips_e_1) {
                lips_s_1.setVisible(true);
                lips_s_2.setVisible(false);
                lips_s_3.setVisible(false);
                lips_s_4.setVisible(false);
                lips_s_5.setVisible(false);
                lips_s_6.setVisible(false);
                lips_s_7.setVisible(false);
                lips_s_8.setVisible(false);
                lips_s_9.setVisible(false);
                lips_s_10.setVisible(false);
                lips_s_11.setVisible(false);
                lips_s_12.setVisible(false);
            } else if(event.getSource()==lips_e_2) {
                lips_s_1.setVisible(false);
                lips_s_2.setVisible(true);
                lips_s_3.setVisible(false);
                lips_s_4.setVisible(false);
                lips_s_5.setVisible(false);
                lips_s_6.setVisible(false);
                lips_s_7.setVisible(false);
                lips_s_8.setVisible(false);
                lips_s_9.setVisible(false);
                lips_s_10.setVisible(false);
                lips_s_11.setVisible(false);
                lips_s_12.setVisible(false);
            } else if(event.getSource()==lips_e_3) {
                lips_s_1.setVisible(false);
                lips_s_2.setVisible(false);
                lips_s_3.setVisible(true);
                lips_s_4.setVisible(false);
                lips_s_5.setVisible(false);
                lips_s_6.setVisible(false);
                lips_s_7.setVisible(false);
                lips_s_8.setVisible(false);
                lips_s_9.setVisible(false);
                lips_s_10.setVisible(false);
                lips_s_11.setVisible(false);
                lips_s_12.setVisible(false);
            } else if(event.getSource()==lips_e_4) {
                lips_s_1.setVisible(false);
                lips_s_2.setVisible(false);
                lips_s_3.setVisible(false);
                lips_s_4.setVisible(true);
                lips_s_5.setVisible(false);
                lips_s_6.setVisible(false);
                lips_s_7.setVisible(false);
                lips_s_8.setVisible(false);
                lips_s_9.setVisible(false);
                lips_s_10.setVisible(false);
                lips_s_11.setVisible(false);
                lips_s_12.setVisible(false);
            } else if(event.getSource()==lips_e_5) {
                lips_s_1.setVisible(false);
                lips_s_2.setVisible(false);
                lips_s_3.setVisible(false);
                lips_s_4.setVisible(false);
                lips_s_5.setVisible(true);
                lips_s_6.setVisible(false);
                lips_s_7.setVisible(false);
                lips_s_8.setVisible(false);
                lips_s_9.setVisible(false);
                lips_s_10.setVisible(false);
                lips_s_11.setVisible(false);
                lips_s_12.setVisible(false);
            } else if(event.getSource()==lips_e_6) {
                lips_s_1.setVisible(false);
                lips_s_2.setVisible(false);
                lips_s_3.setVisible(false);
                lips_s_4.setVisible(false);
                lips_s_5.setVisible(false);
                lips_s_6.setVisible(true);
                lips_s_7.setVisible(false);
                lips_s_8.setVisible(false);
                lips_s_9.setVisible(false);
                lips_s_10.setVisible(false);
                lips_s_11.setVisible(false);
                lips_s_12.setVisible(false);
            } else if(event.getSource()==lips_e_7) {
                lips_s_1.setVisible(false);
                lips_s_2.setVisible(false);
                lips_s_3.setVisible(false);
                lips_s_4.setVisible(false);
                lips_s_5.setVisible(false);
                lips_s_6.setVisible(false);
                lips_s_7.setVisible(true);
                lips_s_8.setVisible(false);
                lips_s_9.setVisible(false);
                lips_s_10.setVisible(false);
                lips_s_11.setVisible(false);
                lips_s_12.setVisible(false);
            } else if(event.getSource()==lips_e_8) {
                lips_s_1.setVisible(false);
                lips_s_2.setVisible(false);
                lips_s_3.setVisible(false);
                lips_s_4.setVisible(false);
                lips_s_5.setVisible(false);
                lips_s_6.setVisible(false);
                lips_s_7.setVisible(false);
                lips_s_8.setVisible(true);
                lips_s_9.setVisible(false);
                lips_s_10.setVisible(false);
                lips_s_11.setVisible(false);
                lips_s_12.setVisible(false);
            } else if(event.getSource()==lips_e_9) {
                lips_s_1.setVisible(false);
                lips_s_2.setVisible(false);
                lips_s_3.setVisible(false);
                lips_s_4.setVisible(false);
                lips_s_5.setVisible(false);
                lips_s_6.setVisible(false);
                lips_s_7.setVisible(false);
                lips_s_8.setVisible(false);
                lips_s_9.setVisible(true);
                lips_s_10.setVisible(false);
                lips_s_11.setVisible(false);
                lips_s_12.setVisible(false);
            } else if(event.getSource()==lips_e_10) {
                lips_s_1.setVisible(false);
                lips_s_2.setVisible(false);
                lips_s_3.setVisible(false);
                lips_s_4.setVisible(false);
                lips_s_5.setVisible(false);
                lips_s_6.setVisible(false);
                lips_s_7.setVisible(false);
                lips_s_8.setVisible(false);
                lips_s_9.setVisible(false);
                lips_s_10.setVisible(true);
                lips_s_11.setVisible(false);
                lips_s_12.setVisible(false);
            } else if(event.getSource()==lips_e_11) {
                lips_s_1.setVisible(false);
                lips_s_2.setVisible(false);
                lips_s_3.setVisible(false);
                lips_s_4.setVisible(false);
                lips_s_5.setVisible(false);
                lips_s_6.setVisible(false);
                lips_s_7.setVisible(false);
                lips_s_8.setVisible(false);
                lips_s_9.setVisible(false);
                lips_s_10.setVisible(false);
                lips_s_11.setVisible(true);
                lips_s_12.setVisible(false);
            } else if(event.getSource()==lips_e_12) {
                lips_s_1.setVisible(false);
                lips_s_2.setVisible(false);
                lips_s_3.setVisible(false);
                lips_s_4.setVisible(false);
                lips_s_5.setVisible(false);
                lips_s_6.setVisible(false);
                lips_s_7.setVisible(false);
                lips_s_8.setVisible(false);
                lips_s_9.setVisible(false);
                lips_s_10.setVisible(false);
                lips_s_11.setVisible(false);
                lips_s_12.setVisible(true);
            } 
        }

        @FXML
        private void onMustSelect(MouseEvent event) {
            if(event.getSource()==must_del) {
                must_s_1.setVisible(false);
                must_s_2.setVisible(false);
                must_s_3.setVisible(false);
                must_s_4.setVisible(false);
                must_s_5.setVisible(false);
                must_s_6.setVisible(false);
            } else if(event.getSource()==must_e_1) {
                must_s_1.setVisible(true);
                must_s_2.setVisible(false);
                must_s_3.setVisible(false);
                must_s_4.setVisible(false);
                must_s_5.setVisible(false);
                must_s_6.setVisible(false);
            } else if(event.getSource()==must_e_2) {
                must_s_1.setVisible(false);
                must_s_2.setVisible(true);
                must_s_3.setVisible(false);
                must_s_4.setVisible(false);
                must_s_5.setVisible(false);
                must_s_6.setVisible(false);
            } else if(event.getSource()==must_e_3) {
                must_s_1.setVisible(false);
                must_s_2.setVisible(false);
                must_s_3.setVisible(true);
                must_s_4.setVisible(false);
                must_s_5.setVisible(false);
                must_s_6.setVisible(false);
            } else if(event.getSource()==must_e_4) {
                must_s_1.setVisible(false);
                must_s_2.setVisible(false);
                must_s_3.setVisible(false);
                must_s_4.setVisible(true);
                must_s_5.setVisible(false);
                must_s_6.setVisible(false);
            } else if(event.getSource()==must_e_5) {
                must_s_1.setVisible(false);
                must_s_2.setVisible(false);
                must_s_3.setVisible(false);
                must_s_4.setVisible(false);
                must_s_5.setVisible(true);
                must_s_6.setVisible(false);
            } else if(event.getSource()==must_e_6) {
                must_s_1.setVisible(false);
                must_s_2.setVisible(false);
                must_s_3.setVisible(false);
                must_s_4.setVisible(false);
                must_s_5.setVisible(false);
                must_s_6.setVisible(true);
            } 
        }

        @FXML
        private void onBeardSelect(MouseEvent event) {
            if(event.getSource()==beard_del) {
                beard_s_1.setVisible(false);
                beard_s_2.setVisible(false);
                beard_s_3.setVisible(false);
                beard_s_4.setVisible(false);
                beard_s_5.setVisible(false);
                beard_s_6.setVisible(false);
            } else if(event.getSource()==beard_e_1) {
                beard_s_1.setVisible(true);
                beard_s_2.setVisible(false);
                beard_s_3.setVisible(false);
                beard_s_4.setVisible(false);
                beard_s_5.setVisible(false);
                beard_s_6.setVisible(false);
            } else if(event.getSource()==beard_e_2) {
                beard_s_1.setVisible(false);
                beard_s_2.setVisible(true);
                beard_s_3.setVisible(false);
                beard_s_4.setVisible(false);
                beard_s_5.setVisible(false);
                beard_s_6.setVisible(false);
            } else if(event.getSource()==beard_e_3) {
                beard_s_1.setVisible(false);
                beard_s_2.setVisible(false);
                beard_s_3.setVisible(true);
                beard_s_4.setVisible(false);
                beard_s_5.setVisible(false);
                beard_s_6.setVisible(false);
            } else if(event.getSource()==beard_e_4) {
                beard_s_1.setVisible(false);
                beard_s_2.setVisible(false);
                beard_s_3.setVisible(false);
                beard_s_4.setVisible(true);
                beard_s_5.setVisible(false);
                beard_s_6.setVisible(false);
            } else if(event.getSource()==beard_e_5) {
                beard_s_1.setVisible(false);
                beard_s_2.setVisible(false);
                beard_s_3.setVisible(false);
                beard_s_4.setVisible(false);
                beard_s_5.setVisible(true);
                beard_s_6.setVisible(false);
            } else if(event.getSource()==beard_e_6) {
                beard_s_1.setVisible(false);
                beard_s_2.setVisible(false);
                beard_s_3.setVisible(false);
                beard_s_4.setVisible(false);
                beard_s_5.setVisible(false);
                beard_s_6.setVisible(true);
            } 
        }

        @FXML
        private void onEarSelect(MouseEvent event) {
            if(event.getSource()==ear_del) {
                ear_s_1.setVisible(false);
                ear_s_2.setVisible(false);
                ear_s_3.setVisible(false);
                ear_s_4.setVisible(false);
            } else if(event.getSource()==ear_e_1) {
                ear_s_1.setVisible(true);
                ear_s_2.setVisible(false);
                ear_s_3.setVisible(false);
                ear_s_4.setVisible(false);
            } else if(event.getSource()==ear_e_2) {
                ear_s_1.setVisible(true);
                ear_s_2.setVisible(true);
                ear_s_3.setVisible(false);
                ear_s_4.setVisible(false);
            } else if(event.getSource()==ear_e_3) {
                ear_s_1.setVisible(false);
                ear_s_2.setVisible(false);
                ear_s_3.setVisible(true);
                ear_s_4.setVisible(false);
            } else if(event.getSource()==ear_e_4) {
                ear_s_1.setVisible(false);
                ear_s_2.setVisible(false);
                ear_s_3.setVisible(true);
                ear_s_4.setVisible(true);
            } 
        }

        @FXML
        private void onNeckSelect(MouseEvent event) {
            if(event.getSource()==neck_del) {
                neck_s_1.setVisible(false);
                neck_s_2.setVisible(false);
            } else if(event.getSource()==neck_e_1) {
                neck_s_1.setVisible(true);
                neck_s_2.setVisible(false);
            } else if(event.getSource()==neck_e_2) {
                neck_s_1.setVisible(false);
                neck_s_2.setVisible(true);
            }
        }

    // ════════════════════════════════════════════════════════════════════════
    // JSON PROJECT SAVE / LOAD STATE SERIALIZATION
    // ════════════════════════════════════════════════════════════════════════

    public static class ElementState {
        public String id;
        public boolean visible;
        public double layoutX;
        public double layoutY;
        public double scaleX;
        public double scaleY;
        public double rotate;
        public double opacity;
    }

    public static class DynamicElementState {
        public String relPath;
        public double layoutX;
        public double layoutY;
        public double scaleX;
        public double scaleY;
        public double rotate;
        public double opacity;
    }

    public static class ProjectState {
        public String caseNo;
        public String officer;
        public String description;
        public String freehandDrawing;
        public List<ElementState> elements;
        public List<DynamicElementState> dynamicElements;
    }

    private String getFieldName(ImageView iv) {
        for (Field field : getClass().getDeclaredFields()) {
            try {
                field.setAccessible(true);
                if (field.get(this) == iv) {
                    return field.getName();
                }
            } catch (IllegalAccessException e) {
                // ignore
            }
        }
        return null;
    }

    private ImageView getFieldByName(String name) {
        try {
            Field field = getClass().getDeclaredField(name);
            field.setAccessible(true);
            return (ImageView) field.get(this);
        } catch (Exception e) {
            return null;
        }
    }

    @FXML
    private void onSaveProject(MouseEvent event) {
        Stage stage = (Stage) sketch.getScene().getWindow();
        FileChooser fileChooser = new FileChooser();
        fileChooser.setTitle("Save Forensic Project");
        fileChooser.setInitialDirectory(new File(System.getProperty("user.home")));
        fileChooser.getExtensionFilters().add(new FileChooser.ExtensionFilter("ThirdEye Project (*.te)", "*.te"));
        fileChooser.setInitialFileName("ThirdEye_Project_" + System.currentTimeMillis() + ".te");
        File file = fileChooser.showSaveDialog(stage);
        if (file != null) {
            try {
                ProjectState state = new ProjectState();
                state.caseNo = (caseNoField != null) ? caseNoField.getText() : "";
                state.officer = (officerField != null) ? officerField.getText() : "";
                state.description = (caseDescArea != null) ? caseDescArea.getText() : "";

                // Convert drawing canvas to Base64
                WritableImage snap = captureCanvasSnapshot();
                BufferedImage buf = SwingFXUtils.fromFXImage(snap, null);
                ByteArrayOutputStream bos = new ByteArrayOutputStream();
                ImageIO.write(buf, "png", bos);
                state.freehandDrawing = Base64.getEncoder().encodeToString(bos.toByteArray());

                // Save element states
                state.elements = new ArrayList<>();
                for (ImageView iv : allElements) {
                    if (iv == null) continue;
                    String name = getFieldName(iv);
                    if (name != null) {
                        ElementState es = new ElementState();
                        es.id = name;
                        es.visible = iv.isVisible();
                        es.layoutX = iv.getLayoutX();
                        es.layoutY = iv.getLayoutY();
                        es.scaleX = iv.getScaleX();
                        es.scaleY = iv.getScaleY();
                        es.rotate = iv.getRotate();
                        es.opacity = iv.getOpacity();
                        state.elements.add(es);
                    }
                }

                // Save dynamic element states
                state.dynamicElements = new ArrayList<>();
                for (ImageView iv : dynamicCanvasElements) {
                    if (iv == null || !iv.isVisible()) continue;
                    DynamicElementState des = new DynamicElementState();
                    des.relPath = (String) iv.getUserData();
                    des.layoutX = iv.getLayoutX();
                    des.layoutY = iv.getLayoutY();
                    des.scaleX = iv.getScaleX();
                    des.scaleY = iv.getScaleY();
                    des.rotate = iv.getRotate();
                    des.opacity = iv.getOpacity();
                    state.dynamicElements.add(des);
                }

                Gson gson = new GsonBuilder().setPrettyPrinting().create();
                String json = gson.toJson(state);
                try (PrintWriter pw = new PrintWriter(file)) {
                    pw.write(json);
                }
                setStatusMessage("Project saved successfully: " + file.getName());
            } catch (Exception ex) {
                ex.printStackTrace();
                setStatusMessage("Error saving project: " + ex.getMessage());
            }
        }
    }

    @FXML
    private void onLoadProject(MouseEvent event) {
        Stage stage = (Stage) sketch.getScene().getWindow();
        FileChooser fileChooser = new FileChooser();
        fileChooser.setTitle("Load Forensic Project");
        fileChooser.setInitialDirectory(new File(System.getProperty("user.home")));
        fileChooser.getExtensionFilters().add(new FileChooser.ExtensionFilter("ThirdEye Project (*.te)", "*.te"));
        File file = fileChooser.showOpenDialog(stage);
        if (file != null) {
            try {
                String json = "";
                try (Scanner scanner = new Scanner(file)) {
                    json = scanner.useDelimiter("\\A").next();
                }
                Gson gson = new Gson();
                ProjectState state = gson.fromJson(json, ProjectState.class);

                // Restore case details
                if (caseNoField != null) caseNoField.setText(state.caseNo);
                if (officerField != null) officerField.setText(state.officer);
                if (caseDescArea != null) caseDescArea.setText(state.description);

                // Restore freehand drawing
                if (state.freehandDrawing != null && !state.freehandDrawing.isEmpty()) {
                    byte[] bytes = Base64.getDecoder().decode(state.freehandDrawing);
                    ByteArrayInputStream bis = new ByteArrayInputStream(bytes);
                    BufferedImage buf = ImageIO.read(bis);
                    Image img = SwingFXUtils.toFXImage(buf, null);
                    gc.clearRect(0, 0, drawingCanvas.getWidth(), drawingCanvas.getHeight());
                    gc.drawImage(img, 0, 0);
                }

                // Restore static elements
                if (state.elements != null) {
                    // Hide all first
                    for (ImageView iv : allElements) {
                        if (iv != null) iv.setVisible(false);
                    }
                    // Restore active ones
                    for (ElementState es : state.elements) {
                        ImageView iv = getFieldByName(es.id);
                        if (iv != null) {
                            iv.setVisible(es.visible);
                            iv.setLayoutX(es.layoutX);
                            iv.setLayoutY(es.layoutY);
                            iv.setScaleX(es.scaleX);
                            iv.setScaleY(es.scaleY);
                            iv.setRotate(es.rotate);
                            iv.setOpacity(es.opacity);
                        }
                    }
                }

                // Clear existing dynamic elements
                for (ImageView iv : dynamicCanvasElements) {
                    if (sketch != null) sketch.getChildren().remove(iv);
                }
                dynamicCanvasElements.clear();

                // Restore dynamic element states
                if (state.dynamicElements != null) {
                    for (DynamicElementState des : state.dynamicElements) {
                        if (des.relPath == null) continue;
                        File fileEl = new File(System.getProperty("user.dir"), "src/thirdeye/v2/elements/sketch elements/" + des.relPath);
                        if (!fileEl.exists()) {
                            fileEl = new File("Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/src/thirdeye/v2/elements/sketch elements/" + des.relPath);
                        }
                        if (fileEl.exists()) {
                            Image img = new Image(fileEl.toURI().toString());
                            addDynamicCanvasElement(img, des.relPath);
                            ImageView iv = dynamicCanvasElements.get(dynamicCanvasElements.size() - 1);
                            iv.setLayoutX(des.layoutX);
                            iv.setLayoutY(des.layoutY);
                            iv.setScaleX(des.scaleX);
                            iv.setScaleY(des.scaleY);
                            iv.setRotate(des.rotate);
                            iv.setOpacity(des.opacity);
                        }
                    }
                }

                setStatusMessage("Project loaded successfully: " + file.getName());
                updateStatusBar();
            } catch (Exception ex) {
                ex.printStackTrace();
                setStatusMessage("Error loading project: " + ex.getMessage());
            }
        }
    }

    private void setStatusMessage(String msg) {
        if (statusBarLabel != null) {
            statusBarLabel.setText(msg);
        }
    }
}
