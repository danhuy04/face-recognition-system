import os
import cv2
from ultralytics import YOLO


class AntiSpoofing:
    """
    Class xử lý anti-spoofing bằng YOLO (detection-based).
    - Dùng chung cho enrollment & attendance.
    - Trả về danh sách detections để linh hoạt xử lý.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AntiSpoofing, cls).__new__(cls)
        return cls._instance

    def __init__(self,
                 model_path=None,
                 conf_threshold=0.85,  # có thể điều chỉnh 0.75-0.85
                 classes=["fake", "real"]):

        if hasattr(self, "_initialized") and self._initialized:
            return
        self._initialized = True

        self.conf_threshold = conf_threshold
        self.classes = classes

        # Resolve model path (giữ nguyên logic cũ của bạn)
        if model_path is None:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
            model_path = os.path.join(PROJECT_ROOT, "anti-spoofing", "models", "best.pt")

        model_path = os.path.abspath(model_path)
        self.model_path = model_path

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Không tìm thấy model tại: {model_path}")

        self.model = YOLO(model_path)
        print("[AntiSpoofing] Model loaded:", model_path)

    def detect_spoof(self, img_bgr):
        """
        Chạy YOLO detection trên full frame.
        Trả về danh sách detections + tóm tắt.

        Returns:
            dict {
                'detections': list of dicts [{'bbox': (x1,y1,x2,y2), 'conf': float, 'label': str, 'class_id': int}],
                'has_real': bool,
                'max_real_conf': float,
                'real_boxes': list of (x1,y1,x2,y2,conf),
                'fake_boxes': list of (x1,y1,x2,y2,conf)
            }
        """
        results = self.model(img_bgr, stream=True, verbose=False)

        detections = []
        real_boxes = []
        fake_boxes = []
        max_real_conf = 0.0

        for r in results:
            boxes = r.boxes
            for box in boxes:
                conf = float(box.conf[0])
                if conf < self.conf_threshold:
                    continue

                cls_id = int(box.cls[0])
                label = self.classes[cls_id]
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                det = {
                    'bbox': (x1, y1, x2, y2),
                    'conf': conf,
                    'label': label,
                    'class_id': cls_id
                }
                detections.append(det)

                if label == "real":
                    real_boxes.append((x1, y1, x2, y2, conf))
                    max_real_conf = max(max_real_conf, conf)
                else:
                    fake_boxes.append((x1, y1, x2, y2, conf))

        has_real = len(real_boxes) > 0

        return {
            'detections': detections,
            'has_real': has_real,
            'max_real_conf': max_real_conf,
            'real_boxes': real_boxes,
            'fake_boxes': fake_boxes
        }

    def draw_results(self, img_bgr, detections_info, thickness=2, text_scale=0.7):
        """
        Vẽ tất cả detections lên ảnh (real xanh, fake đỏ).
        Trả về ảnh đã vẽ.

        Args:
            img_bgr: ảnh gốc
            detections_info: dict từ detect_spoof()
            thickness, text_scale: điều chỉnh visual

        Returns:
            img_bgr đã vẽ
        """
        img = img_bgr.copy()

        for det in detections_info['detections']:
            x1, y1, x2, y2 = det['bbox']
            conf = det['conf']
            label = det['label']

            color = (0, 255, 0) if label == "real" else (0, 0, 255)
            cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)

            text = f"{label.upper()} {conf:.2f}"
            cv2.putText(img, text, (x1, max(y1 - 10, 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, text_scale, color, max(thickness-1, 1))

        return img