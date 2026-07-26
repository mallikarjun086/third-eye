package thirdeye.v2;

import java.io.*;
import java.nio.ByteBuffer;
import java.sql.*;
import java.util.ArrayList;
import java.util.List;
import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;

public class SuspectDatabase {

    private static final String DB_URL = "jdbc:sqlite:suspects.db";

    public static void init() {
        try (Connection conn = DriverManager.getConnection(DB_URL);
             Statement stmt = conn.createStatement()) {
            // Drop old table if it has the old schema (no image_blob column)
            // We detect this by trying the migration first
            boolean needsRecreate = false;
            try {
                stmt.execute("SELECT image_blob FROM suspects LIMIT 1");
            } catch (SQLException e) {
                needsRecreate = true;
            }
            if (needsRecreate) {
                stmt.execute("DROP TABLE IF EXISTS suspects");
            }
            stmt.execute("CREATE TABLE IF NOT EXISTS suspects ("
                    + "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                    + "name TEXT NOT NULL,"
                    + "case_id TEXT DEFAULT '',"
                    + "photo_path TEXT DEFAULT '',"
                    + "image_blob BLOB,"
                    + "hog_blob BLOB,"
                    + "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
                    + ")");
        } catch (SQLException e) {
            System.err.println("SuspectDB init: " + e.getMessage());
        }
    }

    public static int addSuspect(String name, String caseId, BufferedImage image, double[] hogDescriptor) {
        String sql = "INSERT INTO suspects (name, case_id, image_blob, hog_blob) VALUES (?, ?, ?, ?)";
        try (Connection conn = DriverManager.getConnection(DB_URL);
             PreparedStatement pstmt = conn.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {
            pstmt.setString(1, name);
            pstmt.setString(2, caseId != null ? caseId : "");
            if (image != null) {
                // Ensure image is a compatible type for PNG writing
                BufferedImage pngImage = image;
                if (image.getType() != BufferedImage.TYPE_INT_ARGB && image.getType() != BufferedImage.TYPE_INT_RGB) {
                    pngImage = new BufferedImage(image.getWidth(), image.getHeight(), BufferedImage.TYPE_INT_ARGB);
                    java.awt.Graphics2D g = pngImage.createGraphics();
                    g.drawImage(image, 0, 0, null);
                    g.dispose();
                }
                ByteArrayOutputStream baos = new ByteArrayOutputStream();
                boolean written = ImageIO.write(pngImage, "png", baos);
                if (!written) {
                    System.err.println("addSuspect: ImageIO.write returned false");
                    return -1;
                }
                pstmt.setBytes(3, baos.toByteArray());
            } else {
                pstmt.setNull(3, Types.BLOB);
            }
            if (hogDescriptor != null) {
                pstmt.setBytes(4, hogToBytes(hogDescriptor));
            } else {
                pstmt.setNull(4, Types.BLOB);
            }
            pstmt.executeUpdate();
            ResultSet rs = pstmt.getGeneratedKeys();
            if (rs.next()) return rs.getInt(1);
        } catch (Exception e) {
            System.err.println("addSuspect error: " + e.getMessage());
            e.printStackTrace();
        }
        return -1;
    }

    public static void deleteSuspect(int id) {
        String sql = "DELETE FROM suspects WHERE id = ?";
        try (Connection conn = DriverManager.getConnection(DB_URL);
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, id);
            pstmt.executeUpdate();
        } catch (SQLException e) {
            System.err.println("deleteSuspect: " + e.getMessage());
        }
    }

    public static List<SuspectRecord> getAllSuspects() {
        List<SuspectRecord> list = new ArrayList<>();
        String sql = "SELECT id, name, case_id, image_blob, hog_blob FROM suspects ORDER BY name";
        try (Connection conn = DriverManager.getConnection(DB_URL);
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            while (rs.next()) {
                SuspectRecord r = new SuspectRecord();
                r.id = rs.getInt("id");
                r.name = rs.getString("name");
                r.caseId = rs.getString("case_id");
                byte[] imgBytes = rs.getBytes("image_blob");
                if (imgBytes != null) {
                    r.image = ImageIO.read(new ByteArrayInputStream(imgBytes));
                }
                byte[] hogBytes = rs.getBytes("hog_blob");
                if (hogBytes != null) {
                    r.hogDescriptor = bytesToHog(hogBytes);
                }
                list.add(r);
            }
        } catch (Exception e) {
            System.err.println("getAllSuspects: " + e.getMessage());
        }
        return list;
    }

    public static List<SuspectRecord> searchSuspects(String query) {
        List<SuspectRecord> list = new ArrayList<>();
        String sql = "SELECT id, name, case_id, image_blob, hog_blob FROM suspects WHERE name LIKE ? OR case_id LIKE ? ORDER BY name";
        try (Connection conn = DriverManager.getConnection(DB_URL);
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            String like = "%" + query + "%";
            pstmt.setString(1, like);
            pstmt.setString(2, like);
            ResultSet rs = pstmt.executeQuery();
            while (rs.next()) {
                SuspectRecord r = new SuspectRecord();
                r.id = rs.getInt("id");
                r.name = rs.getString("name");
                r.caseId = rs.getString("case_id");
                byte[] imgBytes = rs.getBytes("image_blob");
                if (imgBytes != null) {
                    r.image = ImageIO.read(new ByteArrayInputStream(imgBytes));
                }
                byte[] hogBytes = rs.getBytes("hog_blob");
                if (hogBytes != null) {
                    r.hogDescriptor = bytesToHog(hogBytes);
                }
                list.add(r);
            }
        } catch (Exception e) {
            System.err.println("searchSuspects: " + e.getMessage());
        }
        return list;
    }

    public static byte[] hogToBytes(double[] hog) {
        byte[] bytes = new byte[hog.length * 8];
        ByteBuffer buf = ByteBuffer.wrap(bytes);
        for (double d : hog) {
            buf.putDouble(d);
        }
        return bytes;
    }

    public static double[] bytesToHog(byte[] bytes) {
        ByteBuffer buf = ByteBuffer.wrap(bytes);
        double[] hog = new double[bytes.length / 8];
        for (int i = 0; i < hog.length; i++) {
            hog[i] = buf.getDouble();
        }
        return hog;
    }

    public static class SuspectRecord {
        public int id;
        public String name;
        public String caseId;
        public BufferedImage image;
        public double[] hogDescriptor;

        public String getDisplayName() {
            return name + (caseId != null && !caseId.isEmpty() ? " [" + caseId + "]" : "");
        }
    }
}
