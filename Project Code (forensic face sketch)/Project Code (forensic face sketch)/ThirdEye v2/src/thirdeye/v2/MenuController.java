package thirdeye.v2;

import java.io.IOException;
import java.net.URL;
import java.util.ResourceBundle;
import java.util.logging.Logger;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.fxml.Initializable;
import javafx.scene.Node;
import javafx.scene.Scene;
import javafx.scene.input.MouseEvent;
import javafx.scene.layout.VBox;
import javafx.stage.Stage;

/**
 * Main Menu Controller — opens Dashboard or Upload/Compare screen.
 */
public class MenuController implements Initializable {

    @FXML private VBox sketch;
    @FXML private VBox upload;

    @Override
    public void initialize(URL url, ResourceBundle rb) { }

    @FXML
    private void sketch(MouseEvent event) {
        try {
            FXMLLoader fxmlLoader = new FXMLLoader();
            fxmlLoader.setLocation(getClass().getResource("dashboard.fxml"));
            Scene scene = new Scene(fxmlLoader.load());
            Stage stage = new Stage();
            stage.setTitle("ThirdEye — Sketch Composer");
            stage.setScene(scene);
            stage.setResizable(true);
            stage.setMaximized(true);
            stage.show();
            ((Node) event.getSource()).getScene().getWindow().hide();
        } catch (IOException e) {
            Logger.getLogger(getClass().getName()).log(java.util.logging.Level.SEVERE, null, e);
        }
    }

    @FXML
    private void upload(MouseEvent event) {
        try {
            FXMLLoader fxmlLoader = new FXMLLoader();
            fxmlLoader.setLocation(getClass().getResource("upload_sketch.fxml"));
            Scene scene = new Scene(fxmlLoader.load());
            Stage stage = new Stage();
            stage.setTitle("ThirdEye — Face Comparison");
            stage.setScene(scene);
            stage.setResizable(true);
            stage.setMaximized(true);
            stage.show();
            ((Node) event.getSource()).getScene().getWindow().hide();
        } catch (IOException e) {
            Logger.getLogger(getClass().getName()).log(java.util.logging.Level.SEVERE, null, e);
        }
    }
}
