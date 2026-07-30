# 🎓 Face Recognition Attendance System

Hệ thống nhận diện khuôn mặt tự động để điểm danh sinh viên với tính năng chống giả mạo (liveness detection).

[![Python](https://img.shields.io/badge/Python-3.10-blue?style=flat-square&logo=python)](https://www.python.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange?style=flat-square&logo=tensorflow)](https://www.tensorflow.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

---

## 📋 Mục lục

- [Tính năng chính](#-tính-năng-chính)
- [Yêu cầu hệ thống](#-yêu-cầu-hệ-thống)
- [Cài đặt](#-cài-đặt)
- [Sử dụng](#-sử-dụng)
- [Cấu trúc thư mục](#-cấu-trúc-thư-mục)
- [Công nghệ sử dụng](#-công-nghệ-sử-dụng)
- [Xử lý vấn đề](#-xử-lý-vấn-đề)
- [Tham khảo](#-tham-khảo)

---

## ✨ Tính năng chính

### 📷 Điểm danh sinh viên

- ✅ Nhận diện khuôn mặt real-time
- ✅ Lưu lịch sử điểm danh đầy đủ (thời gian, ngày, trạng thái)
- ✅ Quản lý buổi học (session)
- ✅ Interface thân thiện với tiếng Việt

### 👤 Đăng ký sinh viên

- ✅ Thu thập 15 mẫu khuôn mặt từ nhiều góc độ
- ✅ Kiểm tra chất lượng ảnh (ánh sáng, khoảng cách, clarity)
- ✅ Cảnh báo real-time về chất lượng
- ✅ Progress bar theo dõi tiến độ

### 🚨 Chống giả mạo (Liveness Detection)

- ✅ Phát hiện khuôn mặt giả mạo (ảnh, video)
- ✅ Model YOLO được train riêng
- ✅ Test liveness trên frame toàn bộ (confidence cao)
- ✅ Ngăn chặn ngoại trang không hợp lệ

### 📊 Quản lý dữ liệu

- ✅ Danh sách sinh viên đã đăng ký
- ✅ Tìm kiếm, lọc theo Mã SV hoặc Họ tên
- ✅ Thống kê quality score
- ✅ Xóa sinh viên
- ✅ **Export CSV** (danh sách, lịch sử điểm danh)

### 🎯 Tối ưu hiệu năng

- ✅ Giảm tần suất detection (DETECT_INTERVAL = 5)
- ✅ Giảm tần suất anti-spoofing (ANTISPOOF_INTERVAL = 3)
- ✅ Giảm resolution (det_size: 640×640 → 480×480)
- ✅ FPS ước tính: **6-8 FPS** (từ 0.7 FPS cũ)

---

## 💻 Yêu cầu hệ thống

| Yêu cầu    | Chi tiết                                  |
| ---------- | ----------------------------------------- |
| **OS**     | Windows 10/11, Linux, macOS               |
| **Python** | 3.10+                                     |
| **RAM**    | 4GB+ (8GB+ recommended)                   |
| **CPU**    | Intel i5 hoặc tương đương                 |
| **GPU**    | CUDA 11.8+ (optional, nâng cao hiệu năng) |
| **Camera** | Webcam với resolution ≥ 720p              |

---

## 🚀 Cài đặt

### 1. Clone dự án

```bash
git clone https://github.com/danhuy04/face-recognition-system.git
cd face-recognition-system
```

### 2. Tạo virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Cài đặt dependencies

```bash
# Cài pip packages
pip install -r requirement.txt

# Cài insightface (nếu chưa có) (https://github.com/Gourieff/Assets/tree/main/Insightface)
pip install insightface-0.7.3-cp310-cp310-win_amd64.whl
```

### 4. Cấu hình cơ sở dữ liệu

```bash
cd attendance
# Database sẽ tự tạo khi chạy lần đầu
```

### 5. Chạy ứng dụng

```bash
python -m main
```

---

## 📖 Sử dụng

### 🏠 Giao diện chính

```
┌─────────────────────────────────┐
│  🎓 Face Recognition System    │
├─────────────────────────────────┤
│  ✅ Điểm danh sinh viên        │
│  📋 Đăng ký sinh viên          │
│  📊 Xem lịch sử                │
│  👥 Danh sách sinh viên        │
│  🔧 Cài đặt                    │
└─────────────────────────────────┘
```

### ✅ Quy trình Điểm danh

1. **Chọn hoặc tạo buổi học**
   - Chọn từ dropdown hoặc tạo mới
   - Tên môn học (vd: "Toán A1")

2. **Bắt đầu điểm danh**
   - Nhấn "▶ Bắt đầu"
   - Camera sẽ hoạt động
   - Khuôn mặt sẽ được phát hiện và match

3. **Kết thúc**
   - Nhấn "⏸ Dừng"
   - Xem lịch sử điểm danh

### 👤 Quy trình Đăng ký

1. **Nhập thông tin**
   - Mã SV: "20200001"
   - Họ tên: "Nguyễn Văn A"

2. **Thu thập mẫu**
   - Nhìn vào camera
   - Giữ khoảng cách 50-70cm
   - Xoay nhẹ đầu khi được yêu cầu
   - Thu thập 15 mẫu từ nhiều góc độ

3. **Hoàn thành**
   - ✅ Khi đủ 15 mẫu → tự động lưu
   - Có thể tiếp tục đăng ký sinh viên khác

---

## 📁 Cấu trúc thư mục

```
face-recognition-system/
├── attendance/
│   ├── main.py                    # Entry point
│   ├── core/
│   │   ├── insightface_singleton.py
│   │   ├── anti_spoofing.py      # Liveness detection
│   │   ├── face_matcher.py       # Matching embeddings
│   │   ├── camera.py            # Xử lý camera
│   │   ├── enroll_manager.py    # Đăng ký
│   │   └── student_manager.py   # Quản lý sinh viên
│   ├── gui/
│   │   ├── main_ui.py           # Giao diện chính
│   │   ├── attendance_ui.py     # Điểm danh
│   │   ├── enroll_ui.py         # Đăng ký
│   │   ├── student_list_ui.py   # Danh sách
│   │   ├── attendace_log_ui.py  # Lịch sử
│   │   └── scrollable.py        # Helper UI
│   └── database/
│       ├── db_connection.py
│       ├── models.py
│       ├── attendace_db.py
│       └── session_db.py
│
├── anti-spoofing/
│   ├── main.py
│   ├── models/
│   │   ├── best.pt             # YOLO model (real/fake detection)
│   │   └── yolov8n.pt
│   └── Dataset/
│
├── requirement.txt
├── README.md
└── insightface-0.7.3-cp310-cp310-win_amd64.whl
```

---

## 🔧 Công nghệ sử dụng

| Công nghệ       | Mục đích                               |
| --------------- | -------------------------------------- |
| **InsightFace** | Nhận diện khuôn mặt, extract embedding |
| **YOLO v8**     | Anti-spoofing (real/fake detection)    |
| **OpenCV**      | Xử lý video, draw bbox                 |
| **Tkinter**     | Giao diện người dùng                   |
| **SQLite**      | Lưu trữ dữ liệu                        |
| **NumPy**       | Xử lý ma trận embedding                |

---

## ⚙️ Xử lý vấn đề

### 🐢 Vấn đề: Camera lag / Detect chậm

**Nguyên nhân:** InsightFace & YOLO quá nặng, CPU đạt đến giới hạn

**Giải pháp:**

| Tùy chọn                        | Hiệu ứng    | Khó độ |
| ------------------------------- | ----------- | ------ |
| Tăng DETECT_INTERVAL (5 → 8)    | -20% FPS ↑  | Dễ     |
| Giảm ANTISPOOF_INTERVAL (3 → 5) | -10% FPS ↑  | Dễ     |
| Giảm det_size (480 → 320)       | +30% FPS ↑  | Dễ     |
| Bật GPU (CUDA)                  | +200% FPS ↑ | Khó    |
| Sử dụng model lightweight       | +50% FPS ↑  | Khó    |

**Cách áp dụng (trong `attendance_ui.py`):**

```python
# Tăng tần suất detect
DETECT_INTERVAL = 8  # Thay vì 5

# Giảm resolution
det_size=(320, 320)  # Thay vì (480, 480)
```

### 🚨 Vấn đề: Luôn phát hiện là giả mạo

**Nguyên nhân:**

- Model anti-spoofing chưa được train tốt
- Confidence threshold quá cao
- Test liveness trên face_crop (resolution thấp)

**Giải pháp được áp dụng:**
✅ Test liveness trên **frame toàn bộ** (confidence cao hơn)
✅ Hạ confidence threshold: 0.8 → 0.5
✅ Chỉ check liveness nếu frame "live" thì mới match

---

## 🎯 Hiệu năng hiện tại

| Thước đo   | Cũ         | Mới      | Cải thiện |
| ---------- | ---------- | -------- | --------- |
| FPS        | 0.7-2.2    | 6-8      | ↑ 270%    |
| Detection  | 300-1200ms | 50-200ms | ↑ 85%     |
| Anti-spoof | 60-120ms   | 20-40ms  | ↑ 75%     |

---

## 📋 Tính năng sắp tới

- [ ] Bật GPU support (CUDA)
- [ ] Model anti-spoofing được train tốt hơn
- [ ] Facial expression detection
- [ ] Multi-face detection (điểm danh cùng lúc)
- [ ] Report thống kê chi tiết (bao cơm, etc.)
- [ ] Mobile app (Flask API)
- [ ] Dark mode UI

---

## 🤝 Đóng góp

Nếu bạn muốn đóng góp, vui lòng:

1. Fork repository
2. Tạo branch mới (`git checkout -b feature/AmazingFeature`)
3. Commit thay đổi (`git commit -m 'Add AmazingFeature'`)
4. Push lên branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

---

## 📝 License

Dự án này được cấp phép theo MIT License - xem file [LICENSE](LICENSE) để chi tiết.

---

## 🙏 Cảm ơn

- InsightFace Team cho model nhận diện
- Ultralytics cho YOLOv8
- OpenCV community
- Python community

---


