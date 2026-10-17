import java.security.MessageDigest;
import java.sql.Statement;

class Sample {
    void digests() throws Exception {
        // ruleid: reposcan.java.weak-digest
        MessageDigest.getInstance("MD5");
        // ruleid: reposcan.java.weak-digest
        MessageDigest.getInstance("SHA-1");
        // ok: reposcan.java.weak-digest
        MessageDigest.getInstance("SHA-256");
    }

    void exec(String cmd) throws Exception {
        // ruleid: reposcan.java.runtime-exec
        Runtime.getRuntime().exec(cmd);
        // ok: reposcan.java.runtime-exec
        Runtime.getRuntime().exec("ls");
    }

    void sql(Statement s, String name) throws Exception {
        // ruleid: reposcan.java.sql-concatenation
        s.executeQuery("SELECT * FROM t WHERE n = '" + name + "'");
        // ruleid: reposcan.java.sql-concatenation
        s.executeUpdate("DELETE FROM t WHERE n = '" + name + "'");
        // ok: reposcan.java.sql-concatenation
        s.executeQuery("SELECT 1");
    }
}
