package thirdeye.v2;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.Statement;

/**
 * SQLite Database Connection Utility for ThirdEye v2 Authentication.
 * Handles database connection lifecycle and automatic table creation.
 */
public class connectdb {

    private static String getDatabaseUrl() {
        java.io.File f1 = new java.io.File("login.sqlite");
        if (f1.exists()) {
            return "jdbc:sqlite:" + f1.getAbsolutePath();
        }
        java.io.File f2 = new java.io.File("Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/login.sqlite");
        if (f2.exists()) {
            return "jdbc:sqlite:" + f2.getAbsolutePath();
        }
        return "jdbc:sqlite:login.sqlite";
    }

    public static Connection ConnectDB() {
        try {
            Class.forName("org.sqlite.JDBC");
            Connection conn = DriverManager.getConnection(getDatabaseUrl());
            initDatabase(conn);
            return conn;
        } catch (SQLException | ClassNotFoundException e) {
            System.err.println("JavaConnect Error: " + e.getMessage());
            return null;
        }
    }

    private static void initDatabase(Connection conn) {
        if (conn == null) return;
        String sql = "CREATE TABLE IF NOT EXISTS login_data ("
                + "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                + "email TEXT UNIQUE NOT NULL, "
                + "password TEXT NOT NULL"
                + ");";
        try (Statement stmt = conn.createStatement()) {
            stmt.execute(sql);
        } catch (SQLException e) {
            System.err.println("Database initialization error: " + e.getMessage());
        }
    }
}

