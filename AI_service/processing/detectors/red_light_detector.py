# ai-service/processing/detectors/red_light_detector.py

import uuid
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np
import torch
from ultralytics import YOLO

AI_PROJECT_ROOT = Path(__file__).parent.parent.parent
vehicle_model_path = AI_PROJECT_ROOT / "models/vehicles.pt" 
light_model_path = AI_PROJECT_ROOT / "models/traffic_light.pt"
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
vehicle_model = YOLO(vehicle_model_path)
vehicle_model.to(device)
vehicle_model = YOLO(vehicle_model_path)
light_model = YOLO(light_model_path)

STOP_LINE = np.array([[600, 800], [1300, 800]])

LIGHT_ROI = (1500, 200, 150, 300)

traffic_light_status = "unknown"
tracked_vehicles = {} 
violated_vehicle_ids = set()

def process_frame(frame: np.ndarray, frame_count: int):
    """
    Hàm xử lý chính cho mỗi khung hình video.
    """
    global traffic_light_status, tracked_vehicles, violated_vehicle_ids

    if frame_count % 30 == 0:
        x, y, w, h = LIGHT_ROI
        light_frame_crop = frame[y:y+h, x:x+w]
        
        results = light_model(light_frame_crop, verbose=False)
        if len(results[0].boxes) > 0:
            # Lấy đèn có độ tin cậy cao nhất
            best_light = max(results[0].boxes, key=lambda box: box.conf)
            traffic_light_status = light_model.names[int(best_light.cls)]
    
    # Vẽ vùng quan tâm của đèn và trạng thái đèn lên màn hình
    x, y, w, h = LIGHT_ROI
    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 0), 2)
    cv2.putText(frame, f"Light: {traffic_light_status}", (x, y - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    # Chỉ xử lý phương tiện khi đèn đỏ
    if traffic_light_status != "red":
        # Khi đèn không đỏ, xóa danh sách xe đã vi phạm
        violated_vehicle_ids.clear()
        return None, frame 

    tracks = vehicle_model.track(frame, persist=True, verbose=False, classes=[0,1,2,3],conf = 0.6) 

    if tracks[0].boxes.id is not None:
        boxes = tracks[0].boxes.xyxy.cpu().numpy().astype(int)
        ids = tracks[0].boxes.id.cpu().numpy().astype(int)

        for box, track_id in zip(boxes, ids):
            x1, y1, x2, y2 = box
            center_bottom = (int((x1 + x2) / 2), y2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.circle(frame, center_bottom, 5, (0, 0, 255), -1)

            # Nếu xe chưa được theo dõi, thêm nó vào
            if track_id not in tracked_vehicles:
                tracked_vehicles[track_id] = []
            
            # Lưu lại vị trí hiện tại của xe
            tracked_vehicles[track_id].append(center_bottom)
            
            # Chỉ kiểm tra nếu xe đã có ít nhất 2 vị trí (để xác định hướng đi)
            if len(tracked_vehicles[track_id]) >= 2:
                prev_pos = tracked_vehicles[track_id][-2]
                current_pos = tracked_vehicles[track_id][-1]
                
                # Kiểm tra xem xe có vượt qua vạch dừng không
                if crosses_line(prev_pos, current_pos, STOP_LINE) and track_id not in violated_vehicle_ids:
                    print(f"VIOLATION! Vehicle ID {track_id} crossed the line on RED light.")
                    violated_vehicle_ids.add(track_id)
                    
                    violation_image = frame[y1:y2, x1:x2]
                    
                    # Tạo thông tin vi phạm để trả về
                    violation_info = {
                        "violation_type": "vượt đèn đỏ",
                        "image": violation_image,
                        "license_plate": "UNKNOWN" # Tạm thời
                    }
                    return violation_info, frame

    cv2.line(frame, tuple(STOP_LINE[0]), tuple(STOP_LINE[1]), (0, 0, 255), 3)
    
    return None, frame

def crosses_line(point1, point2, line):
    """Kiểm tra xem đoạn thẳng nối point1 và point2 có cắt line không."""
    p1 = np.array(point1)
    p2 = np.array(point2)
    p3 = line[0]
    p4 = line[1]

    # Sử dụng công thức kiểm tra giao điểm của hai đoạn thẳng
    d = (p4[1] - p3[1]) * (p2[0] - p1[0]) - (p4[0] - p3[0]) * (p2[1] - p1[1])
    if d == 0:
        return False
    t = ((p3[0] - p1[0]) * (p2[1] - p1[1]) - (p3[1] - p1[1]) * (p2[0] - p1[0])) / d
    u = -((p4[1] - p3[1]) * (p3[0] - p1[0]) - (p4[0] - p3[0]) * (p3[1] - p1[1])) / d
    
    return 0 < t < 1 and 0 < u < 1