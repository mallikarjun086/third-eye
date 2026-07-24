package thirdeye.v2;

import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;

/**
 * ThirdEye v2 — Forensic Face Sketch Intelligence System
 * Main application entry point.
 */
public class ThirdEyeV2 extends Application {

    @Override
    public void start(Stage stage) throws Exception {
        Parent root = FXMLLoader.load(getClass().getResource("splash_screen.fxml"));
        Scene scene = new Scene(root);
        stage.setTitle("ThirdEye — Forensic Intelligence System");
        stage.setScene(scene);
        stage.setResizable(false);
        stage.show();
    }

    public static void main(String[] args) {
        launch(args);
    }
}
