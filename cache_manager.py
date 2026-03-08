import sqlite3
import os

class CacheManager:
    def __init__(self, db_path="query_cache.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sql_cache (
                    nl_query TEXT,
                    model_name TEXT,
                    generated_sql TEXT,
                    feedback INTEGER DEFAULT 0, -- 1 for up, -1 for down
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (nl_query, model_name)
                )
            """)

    def get_cached_sql(self, nl_query, model_name):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT generated_sql FROM sql_cache WHERE nl_query = ? AND model_name = ?",
                    (nl_query, model_name)
                )
                row = cursor.fetchone()
                return row[0] if row else None
        except Exception as e:
            print(f"Cache read error: {e}")
            return None

    def store_sql(self, nl_query, model_name, sql):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO sql_cache (nl_query, model_name, generated_sql) VALUES (?, ?, ?)",
                    (nl_query, model_name, sql)
                )
        except Exception as e:
            print(f"Cache write error: {e}")

    def update_feedback(self, nl_query, model_name, score):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "UPDATE sql_cache SET feedback = ? WHERE nl_query = ? AND model_name = ?",
                    (score, nl_query, model_name)
                )
        except Exception as e:
            print(f"Feedback update error: {e}")
