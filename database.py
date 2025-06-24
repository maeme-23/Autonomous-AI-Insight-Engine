import sqlite3
from typing import Optional
import logging
from datetime import datetime

class DatabaseLogger:
    def __init__(self, db_path: str = "query_logs.db"):
        self.db_path = db_path
        self.conn = None

    def initialize(self):
        """Initialize the database connection and create tables if needed"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            
            # Create table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    query TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    sources TEXT NOT NULL,
                    prompt TEXT,
                    UNIQUE(request_id)
                )
            """)
            
            self.conn.commit()
            logging.info("Database initialized successfully")
        except Exception as e:
            logging.error(f"Database initialization failed: {str(e)}")
            raise

    def log_query(self, request_id: str, query: str, answer: str, sources: str, prompt: Optional[str] = None):
        """Log a query and its response to the database"""
        if not self.conn:
            logging.warning("Database not initialized, skipping log")
            return
            
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO query_logs (request_id, timestamp, query, answer, sources, prompt)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (request_id, datetime.now(), query, answer, sources, prompt))
            
            self.conn.commit()
            logging.info(f"Logged query with request_id: {request_id}")
        except Exception as e:
            logging.error(f"Failed to log query: {str(e)}")

    def cleanup(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
            logging.info("Database connection closed")