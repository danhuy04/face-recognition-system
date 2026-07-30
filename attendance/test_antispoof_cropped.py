import cv2
from core.anti_spoofing import AntiSpoofing
from core.insightface_singleton import InsightFaceSingleton

# Khởi tạo
anti_spoof = AntiSpoofing(conf_threshold=0.5)
app = InsightFaceSingleton.get_instance(
    name="buffalo_l",
    providers=["CPUExecutionProvider"],
    det_size=(640, 640),
    ctx_id=0
)

# Test với webcam
cap = cv2.VideoCapture(0)
frame_count = 0
DETECT_INTERVAL = 2

print("Testing anti-spoofing trên FACE CROP... Press 'q' to quit\n")

while True:
    ret, frame_bgr = cap.read()
    if not ret:
        break

    frame_count += 1
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

    faces = []
    if frame_count % DETECT_INTERVAL == 0:
        small = cv2.resize(frame_rgb, None, fx=0.75, fy=0.75)
        faces = app.get(small)

    for face in faces:
        bbox = (face.bbox * (1 / 0.75)).astype(int)
        left, top, right, bottom = bbox

        # Crop mặt từ frame (tương tự attendance_ui)
        face_crop = frame_bgr[top:bottom, left:right]

        if face_crop.size == 0:
            continue

        # Test anti-spoofing trên cropped image
        # is_live, conf, label = anti_spoof.check_liveness(face_crop)
        # Resize face_crop to standard size before checking
        face_crop_resized = cv2.resize(face_crop, (224, 224))  # or YOLO input size
        is_live, conf, label = anti_spoof.check_liveness(face_crop_resized)

        print(
            f"Face crop size: {face_crop.shape} | is_live: {is_live}, conf: {conf:.2f}, label: {label}")

        # Vẽ kết quả
        color = (0, 255, 0) if is_live else (0, 0, 255)
        text = f"{'REAL' if is_live else 'FAKE'} {conf:.2f}"
        cv2.rectangle(frame_bgr, (left, top), (right, bottom), color, 2)
        cv2.putText(frame_bgr, text, (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    cv2.imshow("Anti-Spoofing Test (Cropped)", frame_bgr)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
