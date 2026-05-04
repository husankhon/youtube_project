import requests
from dotenv import load_dotenv
import os
import json
from datetime import date

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_HANDLE = os.getenv("CHANNEL_HANDLE")

url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"


def get_playlist_id():
    try:
        response = requests.get(url)
        response.raise_for_status() 
    
        if response.status_code == 200:
            data = response.json()
            if "items" in data and len(data["items"]) > 0:
                uploads_playlist_id = data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
                return uploads_playlist_id
            else:
                print("No channel found with the specified handle.")
                return None
        else:
            print(f"Failed to retrieve channel details. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def get_video_ids(playlist_id):
    video_ids = []
    next_page_token = None

    while True:
        params = {
            "part": "contentDetails",
            "playlistId": playlist_id,
            "maxResults": 50,
            "key": API_KEY,
        }
        if next_page_token:
            params["pageToken"] = next_page_token

        try:
            response = requests.get("https://www.googleapis.com/youtube/v3/playlistItems", params=params)
            response.raise_for_status()
            data = response.json()

            for item in data.get("items", []):
                video_ids.append(item["contentDetails"]["videoId"])

            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break
        except Exception as e:
            print(f"An error occurred: {e}")
            break

    return video_ids


def get_video_details(video_ids):
    all_details = []

    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i + 50]
        params = {
            "part": "snippet,statistics,contentDetails",
            "id": ",".join(batch),
            "key": API_KEY,
        }
        try:
            response = requests.get("https://www.googleapis.com/youtube/v3/videos", params=params)
            response.raise_for_status()
            data = response.json()

            for item in data.get("items", []):
                all_details.append({
                    "video_id": item["id"],
                    "title": item["snippet"]["title"],
                    "published_at": item["snippet"]["publishedAt"],
                    "duration": item["contentDetails"]["duration"],
                    "views": int(item["statistics"].get("viewCount", 0)),
                    "likes": int(item["statistics"].get("likeCount", 0)),
                    "comments": int(item["statistics"].get("commentCount", 0)),
                })
        except Exception as e:
            print(f"An error occurred: {e}")

    return all_details

def save_to_json(extracted_data):
    file_path = f"./data/YT_data_{date.today()}.json"

    with open(file_path, "w", encoding="utf-8") as json_outfile:
        json.dump(extracted_data, json_outfile, indent=4, ensure_ascii=False)

def main():
    playlist_id = get_playlist_id()
    if playlist_id:
        ids = get_video_ids(playlist_id)
        print(f"Found {len(ids)} videos.")
        details = get_video_details(ids)
        save_to_json(details)
        
if __name__ == "__main__":  
    main()