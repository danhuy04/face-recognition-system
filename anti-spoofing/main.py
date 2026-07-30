from ultralytics import YOLO  
import cv2
import cvzone
import math
import time
import os

confidence = 0.8

cap = cv2.VideoCapture(0)  # Dùng cho Webcam
cap.set(3, 640)
cap.set(4, 480)
# cap = cv2.VideoCapture("../Videos/motorbikes.mp4")  # Dùng cho Video mẫu

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "best.pt")

model = YOLO(MODEL_PATH)

classNames = ["fake", "real"]


prev_frame_time = 0
new_frame_time = 0


while True:
    new_frame_time = time.time()
    success, img = cap.read()
    result = model(img, stream=True, verbose=False)
    for r in result:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            w, h = x2 - x1, y2 - y1

            conf = math.ceil((box.conf[0] * 100)) / 100
            cls = int(box.cls[0])
            if conf > confidence:

                if classNames[cls] == "real":
                    color = (0, 255, 0)
                else:
                    color = (0, 0, 255)
                cvzone.cornerRect(img, (x1, y1, w, h),
                                  colorC=color, colorR=color)
                cvzone.putTextRect(img, f'{classNames[cls].upper()} {int(conf * 100)}%', (max(
                    0, x1), max(35, y1)), scale=2, thickness=4, colorR=color, colorB=color)

    fps = 1 / (new_frame_time - prev_frame_time)
    prev_frame_time = new_frame_time
    print(fps)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
