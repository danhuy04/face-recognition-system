import cv2
from core.anti_spoofing import AntiSpoofing

# Test anti-spoofing trực tiếp
anti_spoof = AntiSpoofing(conf_threshold=0.5)

# Test với webcam
cap = cv2.VideoCapture(0)

print("Testing anti-spoofing... Press 'q' to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Test liveness trên toàn bộ frame
    is_live, conf, label = anti_spoof.check_liveness(frame)

    print(f"is_live: {is_live}, confidence: {conf:.2f}, label: {label}")

    # Hiển thị kết quả
    text = f"LIVE: {is_live} | {label.upper()} {conf:.2f}"
    color = (0, 255, 0) if is_live else (0, 0, 255)
    cv2.putText(frame, text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    cv2.imshow("Anti-Spoofing Test", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
