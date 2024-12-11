from YouTubeAPI import YouTubeAPI
from DataBaseManager import DatabaseManager


class VideoScanner:
    def __init__(self, api_key, db_name="TennisVideos.db"):
        self.youtube = YouTubeAPI(api_key)
        self.db = DatabaseManager(db_name)

    @staticmethod
    def calculate_score(view_count, like_count, comment_count):
        alpha, beta, gamma = 0.6, 0.3, 0.1
        return alpha * view_count + beta * like_count + gamma * comment_count

    def run_scan(self, query, scan_type="full"):
        published_after = None
        if scan_type == "delta":
            published_after = self.db.get_last_scan_date(scan_type)

        videos = self.youtube.search_videos(query, published_after=published_after)
        for video in videos:
            self.db.save_video(video)
            details = self.youtube.get_video_details(video["video_id"])
            if details:
                details["score"] = self.calculate_score(
                    details["view_count"],
                    details["like_count"],
                    details["comment_count"],
                )
                self.db.save_video_details(video["video_id"], details)

        self.db.save_scan(scan_type)
        print(
            f"{scan_type.capitalize()} scan completed with {len(videos)} videos collected."
        )

    def close(self):
        self.db.close()
