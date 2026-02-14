import torch
import datetime
import os
import cv2

model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

WEAPONS = ['knife', 'scissors', 'gun']
SAVE_DIR = "static/detected"
os.makedirs(SAVE_DIR, exist_ok=True)

last_label = None
last_time = 0


def detect_weapon_from_frame(frame):
    global last_label, last_time

    results = model(frame)
    detections = results.xyxy[0]

    for det in detections:
        x1, y1, x2, y2, conf, cls = det
        label = model.names[int(cls)]

        if label in WEAPONS and conf > 0.45:

            now = datetime.datetime.now()
            now_ts = now.timestamp()

            # send alert only if new object OR 20 sec passed
            if label == last_label and now_ts - last_time < 20:
                return None

            last_label = label
            last_time = now_ts

            time_str = now.strftime("%Y-%m-%d %H:%M:%S")
            filename = f"{label}_{time_str.replace(':','-')}.jpg"
            filepath = os.path.join(SAVE_DIR, filename)

            cv2.imwrite(filepath, frame)

            return {
                "name": label,
                "image": filename,
                "time": time_str,
                "box": (int(x1), int(y1), int(x2), int(y2))
            }

    return None
