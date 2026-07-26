package thirdeye.v2;

import java.awt.image.BufferedImage;
import java.io.*;
import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.ResourceBundle;
import java.util.function.Consumer;
import java.util.logging.Level;
import java.util.logging.Logger;
import javafx.embed.swing.SwingFXUtils;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.control.*;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.input.MouseEvent;
import javafx.scene.layout.FlowPane;
import javafx.scene.layout.VBox;
import javafx.stage.FileChooser;
import javafx.stage.Stage;
import javax.imageio.ImageIO;

public class GalleryManagerController implements Initializable {

    @FXML private TextField searchField;
    @FXML private FlowPane thumbGrid;
    @FXML private ImageView detailImage;
    @FXML private Label detailName;
    @FXML private Label detailCaseId;
    @FXML private Label detailDate;
    @FXML private Label statusLabel;

    private List<SuspectDatabase.SuspectRecord> currentSuspects;
    private SuspectDatabase.SuspectRecord selectedSuspect;
    private Consumer<File> photoCallback;

    public void setPhotoCallback(Consumer<File> callback) {
        this.photoCallback = callback;
    }

    @Override
    public void initialize(URL url, ResourceBundle rb) {
        loadSuspects(SuspectDatabase.getAllSuspects());
    }

    private void loadSuspects(List<SuspectDatabase.SuspectRecord> suspects) {
        currentSuspects = suspects;
        thumbGrid.getChildren().clear();
        for (SuspectDatabase.SuspectRecord s : suspects) {
            thumbGrid.getChildren().add(createThumbnailCard(s));
        }
        setStatus(suspects.size() + " suspect(s) loaded.");
    }

    private VBox createThumbnailCard(SuspectDatabase.SuspectRecord record) {
        VBox card = new VBox(4);
        card.setPrefWidth(110);
        card.setAlignment(javafx.geometry.Pos.CENTER);
        card.setStyle("-fx-background-color: #0f1a2e; -fx-padding: 8; -fx-background-radius: 6; -fx-border-color: #333355; -fx-border-radius: 6; -fx-cursor: hand;");

        ImageView iv = new ImageView();
        iv.setFitWidth(100);
        iv.setFitHeight(100);
        iv.setPreserveRatio(true);
        if (record.image != null) {
            iv.setImage(SwingFXUtils.toFXImage(record.image, null));
        }
        iv.setStyle("-fx-background-color: #000; -fx-background-radius: 4;");

        Label nameLabel = new Label(record.name);
        nameLabel.setStyle("-fx-text-fill: #aabbff; -fx-font-size: 10px; -fx-font-weight: bold; -fx-alignment: CENTER;");
        nameLabel.setMaxWidth(100);
        nameLabel.setWrapText(true);

        if (record.caseId != null && !record.caseId.isEmpty()) {
            Label caseLabel = new Label(record.caseId);
            caseLabel.setStyle("-fx-text-fill: #666688; -fx-font-size: 9px; -fx-alignment: CENTER;");
            card.getChildren().addAll(iv, nameLabel, caseLabel);
        } else {
            card.getChildren().addAll(iv, nameLabel);
        }

        card.setOnMousePressed(e -> selectSuspect(record, card));
        card.setOnMouseEntered(e -> card.setStyle("-fx-background-color: #1a2a4e; -fx-padding: 8; -fx-background-radius: 6; -fx-border-color: #6688cc; -fx-border-radius: 6; -fx-cursor: hand;"));
        card.setOnMouseExited(e -> card.setStyle("-fx-background-color: #0f1a2e; -fx-padding: 8; -fx-background-radius: 6; -fx-border-color: #333355; -fx-border-radius: 6; -fx-cursor: hand;"));

        return card;
    }

    private void selectSuspect(SuspectDatabase.SuspectRecord record, VBox card) {
        selectedSuspect = record;
        if (record.image != null) {
            detailImage.setImage(SwingFXUtils.toFXImage(record.image, null));
        }
        detailName.setText(record.name);
        detailCaseId.setText("Case: " + (record.caseId != null && !record.caseId.isEmpty() ? record.caseId : "N/A"));
        detailDate.setText("ID: #" + record.id);
        setStatus("Selected: " + record.name);
    }

    @FXML
    private void onSearch() {
        String query = searchField.getText().trim();
        if (query.isEmpty()) {
            loadSuspects(SuspectDatabase.getAllSuspects());
        } else {
            loadSuspects(SuspectDatabase.searchSuspects(query));
        }
    }

    @FXML
    private void onAddSuspect() {
        Stage stage = (Stage) searchField.getScene().getWindow();
        FileChooser fc = new FileChooser();
        fc.setTitle("Select Suspect Photo");
        fc.setInitialDirectory(new File(System.getProperty("user.home")));
        fc.getExtensionFilters().add(new FileChooser.ExtensionFilter("Images", "*.png", "*.jpg", "*.jpeg", "*.bmp"));
        File file = fc.showOpenDialog(stage);
        if (file == null) return;

        TextInputDialog dialog = new TextInputDialog("");
        dialog.setTitle("Add Suspect");
        dialog.setHeaderText("Enter suspect name");
        dialog.setContentText("Name:");
        dialog.showAndWait().ifPresent(name -> {
            if (name.trim().isEmpty()) {
                setStatus("Name cannot be empty.");
                return;
            }
            try {
                BufferedImage img = ImageIO.read(file);
                if (img == null) {
                    setStatus("Could not read image file.");
                    return;
                }
            int id = SuspectDatabase.addSuspect(name.trim(), "", img, null);
            if (id > 0) {
                setStatus("Added \"" + name + "\" to gallery (ID: " + id + ").");
                loadSuspects(SuspectDatabase.getAllSuspects());
            } else {
                setStatus("Failed to add suspect. Check console for errors.");
            }
        } catch (Exception e) {
            setStatus("Error: " + e.getMessage());
            e.printStackTrace();
        }
        });
    }

    @FXML
    private void onDeleteSelected() {
        if (selectedSuspect == null) {
            setStatus("No suspect selected.");
            return;
        }
        Alert confirm = new Alert(Alert.AlertType.CONFIRMATION,
                "Delete \"" + selectedSuspect.name + "\"?", ButtonType.YES, ButtonType.NO);
        if (confirm.showAndWait().orElse(ButtonType.NO) == ButtonType.YES) {
            SuspectDatabase.deleteSuspect(selectedSuspect.id);
            setStatus("Deleted \"" + selectedSuspect.name + "\".");
            selectedSuspect = null;
            detailImage.setImage(null);
            detailName.setText("No suspect selected");
            detailCaseId.setText("");
            detailDate.setText("");
            loadSuspects(SuspectDatabase.getAllSuspects());
        }
    }

    @FXML
    private void onCompareSelected() {
        if (selectedSuspect == null || selectedSuspect.image == null) {
            setStatus("No suspect selected to compare.");
            return;
        }
        try {
            File tmp = File.createTempFile("gallery_suspect_", ".png");
            tmp.deleteOnExit();
            ImageIO.write(selectedSuspect.image, "png", tmp);
            if (photoCallback != null) {
                photoCallback.accept(tmp);
            }
            ((Stage) searchField.getScene().getWindow()).close();
        } catch (IOException e) {
            setStatus("Error preparing image: " + e.getMessage());
        }
    }

    private void setStatus(String msg) {
        if (statusLabel != null) statusLabel.setText(msg);
    }
}
