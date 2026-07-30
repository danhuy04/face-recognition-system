import cv2
import time
from core.anti_spoofing import AntiSpoofing
from core.insightface_singleton import InsightFaceSingleton

# Khởi tạo
print("Loading models...")
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

print("\nProfiling performance... Press 'q' to quit\n")

times = {
    "read": [],
    "antispoof": [],
    "detect": [],
    "total": []
}

while True:
    t_total = time.time()
    
    # Read frame
    t_read = time.time()
    ret, frame_bgr = cap.read()
    if not ret:
        break
    times["read"].append(time.time() - t_read)
    
    frame_count += 1
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    
    # Anti-spoofing on full frame
    t_antispoof = time.time()
    is_live, conf, label = anti_spoof.check_liveness(frame_bgr)
    times["antispoof"].append(time.time() - t_antispoof)
    
    # Detection
    t_detect = time.time()
    if frame_count % DETECT_INTERVAL == 0:
        faces = app.get(frame_rgb)
    times["detect"].append(time.time() - t_detect)
    
    times["total"].append(time.time() - t_total)
    
    # Print stats mỗi 30 frames
    if frame_count % 30 == 0:
        print(f"\n--- Frame {frame_count} ---")
        print(f"Read:        {times['read'][-1]*1000:.2f}ms")
        print(f"AntiSpoof:   {times['antispoof'][-1]*1000:.2f}ms")
        print(f"Detect:      {times['detect'][-1]*1000:.2f}ms")
        print(f"Total:       {times['total'][-1]*1000:.2f}ms")
        print(f"FPS:         {1/times['total'][-1]:.1f}")
        
        if frame_count == 30:
            print(f"\nAverage (first 30 frames):")
            print(f"Read:        {sum(times['read'])/len(times['read'])*1000:.2f}ms")
            print(f"AntiSpoof:   {sum(times['antispoof'])/len(times['antispoof'])*1000:.2f}ms")
            print(f"Detect:      {sum(times['detect'])/len(times['detect'])*1000:.2f}ms")
            print(f"Total:       {sum(times['total'])/len(times['total'])*1000:.2f}ms")
            print(f"FPS:         {1/(sum(times['total'])/len(times['total'])):.1f}")
    
    # Display
    text = f"Live:{is_live} | FPS:{1/times['total'][-1]:.1f}"
    cv2.putText(frame_bgr, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
    cv2.imshow("Performance Profile", frame_bgr)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

print("\n\n=== FINAL SUMMARY ===")
print(f"Total frames: {frame_count}")
print(f"Avg FPS: {1/(sum(times['total'])/len(times['total'])):.1f}")
