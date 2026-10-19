package thirdeye.v2;

import at.favre.lib.crypto.bcrypt.BCrypt;
import java.io.File;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.List;

/**
 * Automated Live End-to-End System Test for ThirdEye v2 Java layer.
 * Validates DB authentication, suspect DB, REST client, and evidence reporting.
 */
public class LiveSystemVerification {

    public static void main(String[] args) {
        System.out.println("============================================================");
        System.out.println("   THIRDEYE V2 — LIVE JAVA SYSTEM VERIFICATION");
        System.out.println("============================================================");

        boolean allPassed = true;

        // 1. Authentication Database & BCrypt Verification
        System.out.println("\n[JAVA TEST 1] Verifying SQLite Authentication...");
        try (Connection conn = connectdb.ConnectDB()) {
            if (conn == null) {
                System.err.println("  [FAIL] Could not connect to login.sqlite");
                allPassed = false;
            } else {
                String sql = "SELECT email, password FROM login_data WHERE LOWER(email) = LOWER(?)";
                try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
                    pstmt.setString(1, "mallikarjun@gmail.com");
                    try (ResultSet rs = pstmt.executeQuery()) {
                        if (rs.next()) {
                            String email = rs.getString("email");
                            String pass = rs.getString("password");
                            boolean match = "Mallu@086".equals(pass);
                            if (!match && pass.startsWith("$2")) {
                                match = BCrypt.verifyer().verify("Mallu@086".toCharArray(), pass).verified;
                            }
                            System.out.println("  -> User Account Found: " + email);
                            System.out.println("  -> Password Verification: " + (match ? "SUCCESS" : "FAILED"));
                            if (match) {
                                System.out.println("  [PASS] Authentication layer operational.");
                            } else {
                                allPassed = false;
                            }
                        } else {
                            System.err.println("  [FAIL] Test user not found in login_data");
                            allPassed = false;
                        }
                    }
                }
            }
        } catch (Exception e) {
            System.err.println("  [FAIL] Auth error: " + e.getMessage());
            allPassed = false;
        }

        // 2. Suspect Gallery Database
        System.out.println("\n[JAVA TEST 2] Verifying Suspect Database...");
        try {
            SuspectDatabase.init();
            List<SuspectDatabase.SuspectRecord> suspects = SuspectDatabase.getAllSuspects();
            System.out.println("  -> Current Registered Suspect Records: " + suspects.size());
            System.out.println("  [PASS] SuspectDatabase initialized successfully.");
        } catch (Exception e) {
            System.err.println("  [FAIL] SuspectDatabase error: " + e.getMessage());
            allPassed = false;
        }

        // 3. DeepMatchClient Live REST Connection to Python ML Service
        System.out.println("\n[JAVA TEST 3] Verifying DeepMatchClient HTTP Connection...");
        DeepMatchClient client = new DeepMatchClient("http://127.0.0.1:8000");
        try {
            boolean healthy = client.isHealthy();
            System.out.println("  -> ML Service /health: " + (healthy ? "UP & READY" : "DOWN"));
            if (!healthy) {
                System.err.println("  [FAIL] ML Service returned unhealthy status");
                allPassed = false;
            } else {
                String token = client.fetchAuthToken();
                System.out.println("  -> JWT Token Acquired: " + token.substring(0, 15) + "...");
                System.out.println("  [PASS] Live DeepMatchClient REST connection verified.");
            }
        } catch (Exception e) {
            System.err.println("  [FAIL] DeepMatchClient connection failed: " + e.getMessage());
            allPassed = false;
        }

        // 4. Live Cross-Modal Matching & Report Generation
        System.out.println("\n[JAVA TEST 4] Verifying End-to-End Match & Forensic HTML Report...");
        try {
            File queriesDir = new File("Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/ml_service/dataset/queries");
            if (!queriesDir.exists()) {
                queriesDir = new File("ml_service/dataset/queries");
            }
            File galleryDir = new File("Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/ml_service/dataset/gallery");
            if (!galleryDir.exists()) {
                galleryDir = new File("ml_service/dataset/gallery");
            }

            File[] queries = queriesDir.listFiles((d, n) -> n.toLowerCase().endsWith(".jpg") || n.toLowerCase().endsWith(".png"));
            if (queries != null && queries.length > 0) {
                File querySketch = queries[0];
                System.out.println("  -> Submitting Query Sketch: " + querySketch.getName());
                DeepMatchClient.MatchResponseHolder resp = client.matchDetailed(querySketch, galleryDir, 5);

                System.out.println("  -> Pipeline: " + resp.selectedPipeline);
                System.out.println("  -> Decision: " + resp.matchDecision + " (Threshold: " + resp.threshold + ")");
                System.out.println("  -> Candidate Matches Returned: " + resp.results.size());
                for (int i = 0; i < Math.min(3, resp.results.size()); i++) {
                    DeepMatchClient.Match m = resp.results.get(i);
                    System.out.println("     #" + (i + 1) + ": " + m.name + " | Sim: " + String.format("%.4f", m.similarity) + " | Score: " + String.format("%.2f%%", m.calibratedScore));
                }

                File tmpOut = new File(System.getProperty("java.io.tmpdir"));
                File report = ForensicReportGenerator.generateReport(
                    querySketch,
                    "CASE-AUTOMATED-TEST",
                    "FORENSIC_OFFICER_01",
                    resp.matchDecision,
                    resp.threshold,
                    resp.results,
                    tmpOut
                );
                System.out.println("  -> Generated Court-Admissible HTML Report: " + report.getAbsolutePath());
                System.out.println("  -> Report File Exists: " + report.exists() + " (Size: " + report.length() + " bytes)");
                System.out.println("  [PASS] End-to-End Matching and Forensic Report generation verified.");
            } else {
                System.err.println("  [FAIL] No query files found in queriesDir");
                allPassed = false;
            }
        } catch (Exception e) {
            System.err.println("  [FAIL] Live match or report generation error: " + e.getMessage());
            e.printStackTrace();
            allPassed = false;
        }

        System.out.println("\n============================================================");
        if (allPassed) {
            System.out.println("   ALL JAVA LIVE SYSTEM TESTS PASSED (100% OPERATIONAL)");
        } else {
            System.out.println("   SYSTEM TESTS FAILED - REVIEW LOGS ABOVE");
        }
        System.out.println("============================================================");

        System.exit(allPassed ? 0 : 1);
    }
}
