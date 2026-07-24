package thirdeye.v2;

import java.io.IOException;
import java.net.URL;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ResourceBundle;
import java.util.logging.Level;
import java.util.logging.Logger;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.fxml.Initializable;
import javafx.scene.Node;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.PasswordField;
import javafx.scene.control.TextField;
import javafx.scene.layout.AnchorPane;
import javafx.scene.text.Text;
import javafx.stage.Stage;

public class Login_screenController implements Initializable {

    // ── FXML fields ───────────────────────────────────────────────────────────
    @FXML private TextField     email;
    @FXML private PasswordField password;   // PasswordField — masks input
    @FXML private TextField     otp;
    @FXML private Text          error;
    @FXML private Button        send;
    @FXML private Button        signup;
    @FXML private Button        verify;
    @FXML private Text          hide;
    @FXML private Text          hide1;
    @FXML private Text          loginerror;
    @FXML private Text          loginmsg;
    @FXML private AnchorPane    login_page;

    // ── DB connection ─────────────────────────────────────────────────────────
    Connection conn = null;
    PreparedStatement preparedStatement = null;
    ResultSet resultSet = null;

    public Login_screenController() {
        conn = connectdb.ConnectDB();
    }

    // ── LOGIN FUNCTION ────────────────────────────────────────────────────────
    private String Login() {
        try {
            conn = DriverManager.getConnection("jdbc:sqlite:login.sqlite");
        } catch (SQLException e) {
            System.out.println(e.getMessage());
        }

        String status = "Success";
        String e_mail = email.getText();
        String pass   = password.getText();

        if (e_mail.isEmpty() || pass.isEmpty()) {
            error.setText("Please enter your email and password.");
            status = "Error";
        } else {
            String sql = "SELECT * FROM login_data WHERE email = ? AND password = ?";
            try {
                preparedStatement = conn.prepareStatement(sql);
                preparedStatement.setString(1, e_mail);
                preparedStatement.setString(2, pass);
                resultSet = preparedStatement.executeQuery();
                if (!resultSet.next()) {
                    status = "Error";
                } else {
                    loginerror.setText("successful");
                }
            } catch (SQLException ex) {
                System.err.println(ex.getMessage());
                status = "Exception";
            }
        }
        return status;
    }

    @Override
    public void initialize(URL location, ResourceBundle resources) {
        // No IP/MAC thread — removed entirely.
        // No credential printing to console.
    }

    @FXML
    private void handleButtonAction(ActionEvent event) {
        if (event.getSource() == send) {
            Login();
            if (loginerror.getText().equals(loginmsg.getText())) {
                // Login successful → open Menu maximized
                openMenu(event);
            } else {
                error.setText("Incorrect email or password. Please try again.");
            }

        } else if (event.getSource() == signup) {
            String e_mail = email.getText();
            String pass   = password.getText();
            if (e_mail.isEmpty() || pass.isEmpty()) {
                error.setText("Provide email and password to create an account.");
            } else {
                try {
                    String sql = "INSERT INTO login_data (email, password) VALUES (?, ?)";
                    preparedStatement = conn.prepareStatement(sql);
                    preparedStatement.setString(1, e_mail);
                    preparedStatement.setString(2, pass);
                    preparedStatement.executeUpdate();
                    error.setStyle("-fx-fill: #44ff88;");
                    error.setText("Account created successfully. Please sign in.");
                } catch (SQLException ex) {
                    error.setText("Error — this email may already be registered.");
                }
            }

        } else if (event.getSource() == verify) {
            if (hide.getText().equals(otp.getText())) {
                openMenu(event);
            } else {
                error.setText("OTP is incorrect. Please try again.");
            }
        }
    }

    /** Opens the main menu screen maximized. */
    private void openMenu(ActionEvent event) {
        try {
            FXMLLoader fxmlLoader = new FXMLLoader();
            fxmlLoader.setLocation(getClass().getResource("menu.fxml"));
            Scene scene = new Scene(fxmlLoader.load());
            Stage stage = new Stage();
            stage.setTitle("ThirdEye — Main Menu");
            stage.setScene(scene);
            stage.setResizable(true);
            stage.setMaximized(true);
            stage.show();
            ((Node)(event.getSource())).getScene().getWindow().hide();
        } catch (IOException e) {
            Logger.getLogger(getClass().getName()).log(Level.SEVERE, "Failed to open menu.", e);
        }
    }
}