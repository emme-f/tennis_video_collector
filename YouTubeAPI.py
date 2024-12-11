from googleapiclient.discovery import build


class YouTubeAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.service = build("youtube", "v3", developerKey=api_key)

    def search_videos(self, query, max_results=50, published_after=None):
        search_result = (
            self.service.search()
            .list(
                q=query,
                part="snippet",
                type="video",
                maxResults=max_results,
                publishedAfter=published_after,
            )
            .execute()
        )

        results = []
        for item in search_result.get("items", []):
            results.append(
                {
                    "video_id": item["id"]["videoId"],
                    "title": item["snippet"]["title"],
                    "description": item["snippet"]["description"],
                    "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                    "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
                    "published_at": item["snippet"]["publishedAt"],
                }
            )
        return results

    def get_video_details(self, video_id):
        details = (
            self.service.videos()
            .list(part="contentDetails,statistics", id=video_id)
            .execute()
        )

        if not details["items"]:
            return None  # No data found

        video_details = details["items"][0]
        content_details = video_details["contentDetails"]
        statistics = video_details.get("statistics", {})

        duration_iso = content_details.get("duration", "PT0S")
        duration_seconds = int(isodate.parse_duration(duration_iso).total_seconds())

        return {
            "duration": duration_seconds,
            "view_count": int(statistics.get("viewCount", 0)),
            "like_count": int(statistics.get("likeCount", 0)),
            "comment_count": int(statistics.get("commentCount", 0)),
        }
