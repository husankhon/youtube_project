import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
MRBEAST_CHANNEL_ID = "UCX6OQ3DkcsbYNE6H8uQQuVA"
MAX_VIDEOS = 20


def get_youtube_client():
    return build("youtube", "v3", developerKey=API_KEY)


def get_uploads_playlist_id(youtube):
    response = youtube.channels().list(
        part="contentDetails,statistics",
        id=MRBEAST_CHANNEL_ID,
    ).execute()

    channel = response["items"][0]
    playlist_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]
    channel_stats = channel["statistics"]

    print(f"MrBeast Channel Stats:")
    print(f"  Subscribers : {int(channel_stats['subscriberCount']):,}")
    print(f"  Total views : {int(channel_stats['viewCount']):,}")
    print(f"  Total videos: {int(channel_stats['videoCount']):,}")
    print()

    return playlist_id


def get_video_ids(youtube, playlist_id):
    video_ids = []
    next_page_token = None

    while len(video_ids) < MAX_VIDEOS:
        response = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=min(50, MAX_VIDEOS - len(video_ids)),
            pageToken=next_page_token,
        ).execute()

        for item in response["items"]:
            video_ids.append(item["contentDetails"]["videoId"])

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return video_ids


def get_video_statistics(youtube, video_ids):
    videos = []

    for i in range(0, len(video_ids), 50):
        batch = video_ids[i : i + 50]
        response = youtube.videos().list(
            part="snippet,statistics",
            id=",".join(batch),
        ).execute()
        videos.extend(response["items"])

    return videos


def print_video_stats(videos):
    print(f"{'#':<4} {'Title':<55} {'Views':>12} {'Likes':>10} {'Comments':>10}")
    print("-" * 95)

    for idx, video in enumerate(videos, start=1):
        title = video["snippet"]["title"][:54]
        stats = video.get("statistics", {})
        views = int(stats.get("viewCount", 0))
        likes = int(stats.get("likeCount", 0))
        comments = int(stats.get("commentCount", 0))

        print(f"{idx:<4} {title:<55} {views:>12,} {likes:>10,} {comments:>10,}")


def main():
    if not API_KEY:
        raise ValueError("YOUTUBE_API_KEY not found. Add it to a .env file.")

    youtube = get_youtube_client()
    playlist_id = get_uploads_playlist_id(youtube)
    video_ids = get_video_ids(youtube, playlist_id)
    videos = get_video_statistics(youtube, video_ids)

    print(f"Latest {len(videos)} MrBeast Videos:\n")
    print_video_stats(videos)


if __name__ == "__main__":
    main()
