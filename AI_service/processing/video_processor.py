# ai-service/processing/video_processor.py

import traceback

import cv2

from ..connectors import message_publisher
from .detectors import red_light_detector


def process_video_stream(camera_id: str, video_url: str):
    """
    Đọc video từ URL, xử lý từng frame để phát hiện vi phạm,
    và dừng lại khi video kết thúc.
    """
    cap = cv2.VideoCapture(video_url)
    if not cap.isOpened():
        print(f"Lỗi: Không thể mở luồng video cho camera {camera_id}")
        return

    frame_count = 0
    while True:
        ret, frame = cap.read()

        if not ret:
            print(f"Video đã kết thúc hoặc luồng bị ngắt cho camera {camera_id}. Dừng tiến trình.")
            break 

        frame_count += 1
        
        # Chỉ xử lý 1 trong 3 khung hình để tiết kiệm CPU.
        if frame_count % 3 != 0:
            continue

        try:
            # Gửi frame cho detector để xử lý
            violation, processed_frame = red_light_detector.process_frame(frame, frame_count)
            
            # Nếu có vi phạm, gửi đi
            if violation:
                # Chuyển ảnh từ OpenCV (BGR) sang bytes (JPG)
                _, image_bytes = cv2.imencode('.jpg', violation["image"])

                print(f"Đang gửi thông tin vi phạm cho camera {camera_id}...")
                message_publisher.publish_violation(
                    camera_id=camera_id,
                    violation_type=violation["violation_type"],
                    license_plate=violation["license_plate"],
                    image_bytes=image_bytes.tobytes()
                )

        except Exception as e:
            print(f"LỖI khi đang xử lý khung hình {frame_count} cho camera {camera_id}: {e}")
            traceback.print_exc() 
            continue 

    print(f"Đã giải phóng tài nguyên cho camera {camera_id}.")
    cap.release()
    cv2.destroyAllWindows()