package com.taos.example.highvolume;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingDeque;

// ANCHOR: WriteTask
class WriteTask implements Runnable {
    final static int maxBatchSize = 500;
    private final BlockingQueue<String> queue;

    public WriteTask(BlockingQueue<String> taskQueue) {
        this.queue = taskQueue;
    }

    private static Connection getConnection() throws SQLException {
        String jdbcUrl = "jdbc:TAOS://localhost:6030?user=root&password=taosdata";
        return DriverManager.getConnection(jdbcUrl);
    }

    public void run() {
        int count = 0;
        try {
            Connection conn = getConnection();
            Statement stmt = conn.createStatement();
            Map<String, String> tbValues = new HashMap<>();
            while (true) {
                String line = queue.poll();
                if (line != null) {
                    processLine(tbValues, line);
                    count += 1;
                    if (count == maxBatchSize) {
                        // trigger writing when count of buffered records reached maxBachSize
                        flushValues(stmt, tbValues);
                        count = 0;
                    }
                } else if (count == 0) {
                    // if queue is empty and no buffered records, sleep a while to avoid high CPU usage.
                    Thread.sleep(500);
                } else {
                    // if queue is empty and there are buffered records then flush immediately
                    flushValues(stmt, tbValues);
                    count = 0;
                }
            }
        } catch (Exception e) {
            // handle exception
        }

    }

    private void processLine(Map<String, String> tbValues, String line) {

    }

    private void flushValues(Statement stmt, Map<String, String> tbValues) {

    }

}
// ANCHOR_END: WriteTask