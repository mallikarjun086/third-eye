package thirdeye.v2;

import java.io.IOException;
import java.net.URL;
import java.sql.Connection;
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
import javafx.scene.input.KeyCode;
import javafx.scene.layout.AnchorPane;
import javafx.scene.text.Text;
import javafx.stage.Stage;

import at.favre.lib.crypto.bcrypt.BCrypt;

/**
 * Enterprise Authentication Controller for ThirdEye v2.
 * Supports BCrypt password hashing, automatic legacy hash migration,
 * input validation, keyboard shortcuts, and clear user feedback.
 */
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

    private static final Logger LOGGER = Logger.getLogger(Login_screenController.class.getName());

    @Override
    public void initialize(URL location, ResourceBundle resources) {
        // Keyboard Enter key triggers Sign In action
        if (password != null) {
            password.setOnKeyPressed(event -> {
                if (event.getCode() == KeyCode.ENTER) {
                    handleLogin();
                }
            });
        }
        if (email != null) {
            email.setOnKeyPressed(event -> {
                if (event.getCode() == KeyCode.ENTER) {
                    if (password != null && !password.getText().isEmpty()) {
                        handleLogin();
                    } else if (password != null) {
                        password.requestFocus();
                    }
                }
            });
        }
    }

    @FXML
    private void handleButtonAction(ActionEvent event) {
        if (event.getSource() == send) {
            handleLogin(event);
        } else if (event.getSource() == signup) {
            handleSignup();
        } else if (event.getSource() == verify) {
            if (hide.getText().equals(otp.getText())) {
                openMenu(event);
            } else {
                showError("OTP is incorrect. Please try again.");
            }
        }
    }

    private void handleLogin() {
        handleLogin(null);
    }

    private void handleLogin(ActionEvent event) {
        clearMessages();

        String e_mail = email != null ? email.getText().trim() : "";
        String pass   = password != null ? password.getText() : "";

        if (e_mail.isEmpty() || pass.isEmpty()) {
            showError("Please enter your registered email and password.");
            return;
        }

        Connection conn = connectdb.ConnectDB();
        if (conn == null) {
            showError("Database error: Could not connect to authentication store.");
            return;
        }

        String sql = "SELECT * FROM login_data WHERE LOWER(email) = LOWER(?)";
        try (PreparedStatement preparedStatement = conn.prepareStatement(sql)) {
            preparedStatement.setString(1, e_mail);
            try (ResultSet resultSet = preparedStatement.executeQuery()) {
                if (!resultSet.next()) {
                    showError("Invalid credentials. Account not found.");
                    return;
                }

                String storedPass = resultSet.getString("password");
                boolean verified = false;

                if (storedPass != null && (storedPass.startsWith("$2a$") || storedPass.startsWith("$2b$") || storedPass.startsWith("$2y$"))) {
                    BCrypt.Result result = BCrypt.verifyer().verify(pass.toCharArray(), storedPass);
                    verified = result.verified;
                } else if (storedPass != null && storedPass.equals(pass)) {
                    // Legacy plaintext match — transparent upgrade to BCrypt hash
                    verified = true;
                    try {
                        String newHash = BCrypt.withDefaults().hashToString(12, pass.toCharArray());
                        try (PreparedStatement updateStmt = conn.prepareStatement("UPDATE login_data SET password = ? WHERE LOWER(email) = LOWER(?)")) {
                            updateStmt.setString(1, newHash);
                            updateStmt.setString(2, e_mail);
                            updateStmt.executeUpdate();
                        }
                    } catch (SQLException ex) {
                        LOGGER.log(Level.WARNING, "Legacy password migration warning", ex);
                    }
                }

                if (verified) {
                    showSuccess("Login successful! Redirecting...");
                    if (event != null) {
                        openMenu(event);
                    } else if (send != null && send.getScene() != null && send.getScene().getWindow() != null) {
                        openMenuFromWindow((Stage) send.getScene().getWindow());
                    }
                } else {
                    showError("Incorrect password. Please try again.");
                }
            }
        } catch (SQLException ex) {
            LOGGER.log(Level.SEVERE, "Login database query failed", ex);
            showError("Authentication service error. Please try again.");
        } finally {
            try { conn.close(); } catch (Exception ignored) {}
        }
    }

    private void handleSignup() {
        clearMessages();

        String e_mail = email != null ? email.getText().trim() : "";
        String pass   = password != null ? password.getText() : "";

        if (e_mail.isEmpty() || pass.isEmpty()) {
            showError("Please enter email and password to create an account.");
            return;
        }

        if (!e_mail.contains("@") || !e_mail.contains(".")) {
            showError("Please enter a valid email address (e.g. officer@agency.gov).");
            return;
        }

        if (pass.length() < 4) {
            showError("Password must be at least 4 characters long.");
            return;
        }

        Connection conn = connectdb.ConnectDB();
        if (conn == null) {
            showError("Database error: Could not connect to authentication store.");
            return;
        }

        String checkSql = "SELECT email FROM login_data WHERE LOWER(email) = LOWER(?)";
        try (PreparedStatement checkStmt = conn.prepareStatement(checkSql)) {
            checkStmt.setString(1, e_mail);
            try (ResultSet rs = checkStmt.executeQuery()) {
                if (rs.next()) {
                    showError("An account with this email already exists. Please sign in.");
                    return;
                }
            }
        } catch (SQLException ex) {
            LOGGER.log(Level.WARNING, "Pre-signup check error", ex);
        }

        String hashedPassword = BCrypt.withDefaults().hashToString(12, pass.toCharArray());
        String insertSql = "INSERT INTO login_data (email, password) VALUES (?, ?)";

        try (PreparedStatement preparedStatement = conn.prepareStatement(insertSql)) {
            preparedStatement.setString(1, e_mail);
            preparedStatement.setString(2, hashedPassword);
            preparedStatement.executeUpdate();

            showSuccess("Account created successfully! You can now click SIGN IN.");
            if (password != null) {
                password.clear();
            }
        } catch (SQLException ex) {
            LOGGER.log(Level.SEVERE, "Account creation failed", ex);
            if (ex.getMessage() != null && ex.getMessage().toLowerCase().contains("unique")) {
                showError("An account with this email already exists. Please sign in.");
            } else {
                showError("Could not create account: " + ex.getMessage());
            }
        } finally {
            try { conn.close(); } catch (Exception ignored) {}
        }
    }

    private void clearMessages() {
        if (error != null) {
            error.setText("");
        }
    }

    private void showError(String msg) {
        if (error != null) {
            error.setStyle("-fx-fill: #ff6b6b;");
            error.setText(msg);
        }
    }

    private void showSuccess(String msg) {
        if (error != null) {
            error.setStyle("-fx-fill: #44ff88;");
            error.setText(msg);
        }
    }

    /** Opens the main menu screen maximized. */
    private void openMenu(ActionEvent event) {
        if (event != null && event.getSource() instanceof Node) {
            openMenuFromWindow((Stage) ((Node) event.getSource()).getScene().getWindow());
        }
    }

    private void openMenuFromWindow(Stage currentStage) {
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
            if (currentStage != null) {
                currentStage.hide();
            }
        } catch (IOException e) {
            LOGGER.log(Level.SEVERE, "Failed to open main menu", e);
            showError("Application error: Could not load main menu.");
        }
    }
}