from datetime import datetime
import sqlite3


class DatabaseManager:
    def __init__(self, db_name="TennisVideos.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.conn.execute("PRAGMA foreign_keys = 1")

    def save_video(self, video):
        try:
            with self.conn:
                self.conn.execute(
                    """
                    INSERT OR IGNORE INTO video 
                    (video_id, title, description, url, thumbnail, published_at)
                    VALUES (:video_id, :title, :description, :url, :thumbnail, :published_at)
                """,
                    video,
                )
        except Exception as e:
            print(f"Error saving video: {e}")

    def save_video_details(self, video_id, details):
        try:
            with self.conn:
                self.conn.execute(
                    """
                    UPDATE video
                    SET duration = :duration,
                        view_count = :view_count,
                        like_count = :like_count,
                        comment_count = :comment_count,
                        score = :score
                    WHERE video_id = :video_id
                """,
                    {**details, "video_id": video_id},
                )
        except Exception as e:
            print(f"Error saving video details: {e}")

    def save_scan(self, scan_type):
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO scans (type, date)
                VALUES (?, ?)
            """,
                (scan_type, datetime.utcnow()),
            )

    def get_last_scan_date(self, scan_type):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT date FROM scans
            WHERE type = ?
            ORDER BY date DESC
            LIMIT 1
        """,
            (scan_type,),
        )
        result = cursor.fetchone()
        return result[0] if result else None

    def close(self):
        self.conn.close()
