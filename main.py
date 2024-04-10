import os
import requests
import subprocess
import time

# Function to read API key from a text file
def read_api_key(filename):
    try:
        script_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(script_dir, filename)
        with open(file_path, 'r') as file:
            api_key = file.read().strip()
        return api_key
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the API key from '{filename}':", e)
        return None

# Function to fetch the latest video from the given channel URL using YouTube Data API
def fetch_latest_video(api_key, channel_id):
    try:
        url = f"https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={channel_id}&part=snippet&order=date&maxResults=1"
        response = requests.get(url)
        data = response.json()

        if 'items' in data and len(data['items']) > 0:
            latest_video = data['items'][0]
            title = latest_video['snippet']['title']
            video_id = latest_video['id']['videoId']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            return title, video_url
        else:
            print("No videos found on the channel.")
            return None, None
    except Exception as e:
        print("An error occurred while fetching the latest video:", e)
        return None, None

# Function to download the video using yt-dlp
def download_video(video_url):
    try:
        # Change working directory to where yt-dlp.exe is located
        os.chdir(".//yt-dlp")

        # Run yt-dlp.exe
        subprocess.run(["yt-dlp.exe", video_url])
        print("Video downloaded successfully.")
    except Exception as e:
        print("An error occurred while downloading the video:", e)

# Main function
def main():
    api_key_filename = "api.txt"
    api_key = read_api_key(api_key_filename)
    if not api_key:
        print("Error: Unable to read the API key.")
        return

    channel_id = input("Enter the channel ID: ")

    # Initial fetch
    prev_title, prev_video_url = fetch_latest_video(api_key, channel_id)
    if prev_title and prev_video_url:
        print(f"Latest video: {prev_title}")
        print(f"Video URL: {prev_video_url}")
        # Flag to indicate whether the first download prompt has been shown
        first_download_prompt = True

    else:
        print("Error: Unable to fetch the latest video. Please check the channel ID and API key.")
        return

    # Ask if user wants to download the latest video
    download_choice = input("Do you want to download the latest video? (yes/no): ")
    if download_choice.lower() == "yes":
        download_video(prev_video_url)

    # Ask for the interval in minutes
    interval = int(input("Enter the interval between checks (in minutes): ")) * 60

    # Continuous loop to check for new videos
    while True:
        time.sleep(interval)
        title, video_url = fetch_latest_video(api_key, channel_id)
        if title and video_url and (title != prev_title or video_url != prev_video_url):
            print(f"New video found: {title}")
            download_video(video_url)
            prev_title, prev_video_url = title, video_url
        else:
            if title is not None:  # If title is None, it means no videos were found
                print(f"Latest video: {title}")
                print(f"Video URL: {video_url}")
            print("No new videos found.")

if __name__ == "__main__":
    main()
