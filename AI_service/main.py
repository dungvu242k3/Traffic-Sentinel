# ai-service/main.py 

import multiprocessing
import sys
import time
from pathlib import Path

import requests
import yt_dlp

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.insert(0, str(project_root))

from .processing.detectors import red_light_detector
from .processing.video_processor import process_video_stream

# URL của Back-end API, nơi ai-service sẽ hỏi danh sách camera
API_URL = "http://127.0.0.1:8000/api/v1/cameras/" 
POLLING_INTERVAL = 30 

def fetch_cameras_from_api():
    """Gọi API để lấy danh sách camera mới nhất."""
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        cameras = response.json()
        print(f"Successfully fetched {len(cameras)} cameras from API.")
        return cameras
    except requests.exceptions.RequestException as e:
        print(f"Error fetching cameras from API: {e}")
        return []

def get_youtube_direct_url(youtube_url: str):
    """Sử dụng yt-dlp để lấy URL stream trực tiếp từ video YouTube."""
    ydl_opts = {'format': 'best[ext=mp4]','quiet': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            return info.get('url')
    except Exception as e:
        print(f"Error with yt-dlp for {youtube_url}: {e}")
        return None

def main():
    """Vòng lặp chính: Lấy camera từ API và quản lý các tiến trình xử lý."""
    active_processes = {}

    while True:
        print("\n--- Checking for camera updates ---")
        cameras_from_api = fetch_cameras_from_api()
        api_camera_ids = {camera['id'] for camera in cameras_from_api}
        
        # Dừng các tiến trình của camera đã bị xóa
        ids_to_stop = set(active_processes.keys()) - api_camera_ids
        for camera_id in ids_to_stop:
            print(f"Stopping process for deleted camera: {camera_id}")
            process = active_processes.pop(camera_id)
            process.terminate()
            process.join()

        # Bắt đầu tiến trình cho camera mới
        for camera in cameras_from_api:
            camera_id = camera['id']
            if camera_id not in active_processes:
                print(f"Found new camera, starting process for: {camera['name']} ({camera_id})")
                
                direct_video_url = get_youtube_direct_url(camera["url"])
                
                if direct_video_url:
                    process = multiprocessing.Process(
                        target=process_video_stream,
                        args=(camera_id, direct_video_url)
                    )
                    process.start()
                    active_processes[camera_id] = process
                else:
                    print(f"Warning: Could not get direct stream for {camera['url']}. Skipping.")

        print(f"--- Update check complete. {len(active_processes)} processes running. Waiting for {POLLING_INTERVAL} seconds. ---")
        time.sleep(POLLING_INTERVAL)

if __name__ == "__main__":
    print("Pre-loading AI models...")
    _ = red_light_detector.vehicle_model
    _ = red_light_detector.light_model
    print("AI models loaded. Starting main process.")
    main()