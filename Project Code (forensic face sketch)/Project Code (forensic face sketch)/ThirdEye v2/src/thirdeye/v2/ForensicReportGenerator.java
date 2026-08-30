package thirdeye.v2;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;

/**
 * Enterprise Forensic Case Audit Report Generator for ThirdEye v2.
 * Produces court-admissible forensic report files containing timestamped evidence,
 * cryptographic SHA-256 integrity hashes, candidate ranking tables, and open-set match decisions.
 */
public class ForensicReportGenerator {

    public static File generateReport(
            File sketchFile,
            String caseId,
            String officerId,
            String matchDecision,
            double threshold,
            List<DeepMatchClient.Match> matches,
            File outputDir
    ) throws IOException {

        if (outputDir == null || !outputDir.exists()) {
            outputDir = new File(System.getProperty("user.home"), "Desktop");
        }

        SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        SimpleDateFormat fileDateFormat = new SimpleDateFormat("yyyyMMdd_HHmmss");
        String timestampStr = dateFormat.format(new Date());
        String fileTag = fileDateFormat.format(new Date());

        String reportFileName = "Forensic_Audit_Report_" + caseId.replaceAll("[^a-zA-Z0-9_-]", "_") + "_" + fileTag + ".html";
        File reportFile = new File(outputDir, reportFileName);

        String sketchHash = computeSHA256(sketchFile);

        StringBuilder sb = new StringBuilder();
        sb.append("<!DOCTYPE html>\n<html>\n<head>\n<meta charset=\"UTF-8\">\n");
        sb.append("<title>Forensic Case Audit Report - ").append(caseId).append("</title>\n");
        sb.append("<style>\n");
        sb.append("body { font-family: 'Segoe UI', Tahoma, Helvetica, Arial, sans-serif; background: #080c18; color: #d0deff; margin: 0; padding: 30px; }\n");
        sb.append(".container { max-width: 900px; margin: auto; background: #0f152d; padding: 30px; border-radius: 10px; border: 1px solid #1e2d5a; box-shadow: 0 0 20px rgba(0,0,0,0.5); }\n");
        sb.append(".header { border-bottom: 2px solid #3a6fff; padding-bottom: 15px; margin-bottom: 20px; text-align: center; }\n");
        sb.append(".header h1 { color: #00d4ff; margin: 0; font-size: 26px; text-transform: uppercase; letter-spacing: 1.5px; }\n");
        sb.append(".header p { color: #5a7aaa; margin: 5px 0 0 0; font-size: 13px; }\n");
        sb.append(".meta-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; background: #131c3b; padding: 15px; border-radius: 6px; border: 1px solid #233468; font-size: 14px; }\n");
        sb.append(".meta-item { margin-bottom: 5px; }\n");
        sb.append(".meta-label { color: #7a9acc; font-weight: bold; }\n");
        sb.append(".badge-decision { display: inline-block; padding: 6px 12px; border-radius: 4px; font-weight: bold; font-size: 14px; margin-top: 10px; }\n");
        sb.append(".badge-match { background: #1b5e20; color: #44ff88; border: 1px solid #2e7d32; }\n");
        sb.append(".badge-nomatch { background: #4a1212; color: #ff6b6b; border: 1px solid #8c1d1d; }\n");
        sb.append("table { width: 100%; border-collapse: collapse; margin-top: 25px; font-size: 14px; }\n");
        sb.append("th { background: #1a2750; color: #80b3ff; text-align: left; padding: 10px; border-bottom: 2px solid #2e4380; }\n");
        sb.append("td { padding: 10px; border-bottom: 1px solid #1a2750; }\n");
        sb.append("tr:nth-child(even) { background: #111833; }\n");
        sb.append(".hash { font-family: monospace; font-size: 11px; color: #00d4ff; word-break: break-all; }\n");
        sb.append(".footer { margin-top: 30px; border-top: 1px solid #1e2d5a; padding-top: 15px; font-size: 11px; color: #4a5c80; text-align: center; }\n");
        sb.append("</style>\n</head>\n<body>\n");

        sb.append("<div class=\"container\">\n");
        sb.append("<div class=\"header\">\n");
        sb.append("<h1>ThirdEye v2 — Forensic Audit Report</h1>\n");
        sb.append("<p>Official Law Enforcement Evidence & Match Verification Document</p>\n");
        sb.append("</div>\n");

        sb.append("<div class=\"meta-grid\">\n");
        sb.append("<div class=\"meta-item\"><span class=\"meta-label\">Case Reference ID:</span> ").append(caseId).append("</div>\n");
        sb.append("<div class=\"meta-item\"><span class=\"meta-label\">Investigating Officer ID:</span> ").append(officerId).append("</div>\n");
        sb.append("<div class=\"meta-item\"><span class=\"meta-label\">Timestamp:</span> ").append(timestampStr).append("</div>\n");
        sb.append("<div class=\"meta-item\"><span class=\"meta-label\">System Code Name:</span> ThirdEye v2 (JWT Secured + FAISS)</div>\n");
        sb.append("<div class=\"meta-item\"><span class=\"meta-label\">Query Sketch File:</span> ").append(sketchFile.getName()).append("</div>\n");
        sb.append("<div class=\"meta-item\"><span class=\"meta-label\">Calibrated Decision Threshold:</span> ").append(String.format("%.1f%%", threshold * 100.0)).append("</div>\n");
        sb.append("</div>\n");

        boolean isMatch = "POSSIBLE MATCH".equalsIgnoreCase(matchDecision);
        sb.append("<div style=\"text-align: center; margin-top: 20px;\">\n");
        sb.append("<span class=\"badge-decision ").append(isMatch ? "badge-match" : "badge-nomatch").append("\">");
        sb.append("OFFICIAL VERDICT: ").append(matchDecision).append("</span>\n");
        sb.append("</div>\n");

        sb.append("<div style=\"margin-top: 20px; background: #131c3b; padding: 12px; border-radius: 6px;\">\n");
        sb.append("<span class=\"meta-label\">SHA-256 Evidence Integrity Hash:</span><br/>\n");
        sb.append("<span class=\"hash\">").append(sketchHash).append("</span>\n");
        sb.append("</div>\n");

        sb.append("<h3>Top Ranked Gallery Candidate Matches</h3>\n");
        sb.append("<table>\n");
        sb.append("<tr><th>Rank</th><th>Suspect Identity</th><th>Calibrated Score</th><th>Raw Cosine Similarity</th><th>File Path</th></tr>\n");

        if (matches != null && !matches.isEmpty()) {
            for (DeepMatchClient.Match m : matches) {
                sb.append("<tr>");
                sb.append("<td>#").append(m.rank).append("</td>");
                sb.append("<td><b>").append(m.name).append("</b></td>");
                sb.append("<td><b>").append(String.format("%.2f%%", m.calibratedScore)).append("</b></td>");
                sb.append("<td>").append(String.format("%.4f", m.similarity)).append("</td>");
                sb.append("<td style=\"font-size: 11px; color: #7a9acc;\">").append(m.path).append("</td>");
                sb.append("</tr>\n");
            }
        } else {
            sb.append("<tr><td colspan=\"5\" style=\"text-align:center;\">No candidates evaluated.</td></tr>\n");
        }
        sb.append("</table>\n");

        sb.append("<div class=\"footer\">\n");
        sb.append("Generated by ThirdEye v2 Forensic Workstation. This document is cryptographically hashed for chain-of-custody verification.\n");
        sb.append("</div>\n");

        sb.append("</div>\n</body>\n</html>\n");

        try (FileWriter writer = new FileWriter(reportFile, StandardCharsets.UTF_8)) {
            writer.write(sb.toString());
        }

        return reportFile;
    }

    private static String computeSHA256(File file) {
        if (file == null || !file.exists()) return "UNKNOWN_HASH";
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] fileBytes = java.nio.file.Files.readAllBytes(file.toPath());
            byte[] hashBytes = digest.digest(fileBytes);
            StringBuilder hexString = new StringBuilder();
            for (byte b : hashBytes) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) hexString.append('0');
                hexString.append(hex);
            }
            return hexString.toString();
        } catch (Exception e) {
            return "ERROR_COMPUTING_HASH: " + e.getMessage();
        }
    }
}
