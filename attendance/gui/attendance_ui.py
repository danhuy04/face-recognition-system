import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
from PIL import Image, ImageTk
import cv2
from datetime import datetime, timedelta

from gui.scrollable import create_scrollable_page
from gui.base_ui import BaseFrame
from core.camera import Camera
from database.db_connection import DBConnection
from database.attendance_db import AttendanceDB
from database.session_db import SessionDB
from core.insightface_singleton import InsightFaceSingleton
from core.anti_spoofing import AntiSpoofing


class AttendanceUI(BaseFrame):
    # ================= CONFIG =================
    SIMILARITY_THRESHOLD = 0.45
    COOLDOWN_MAX = 60
    DETECT_INTERVAL = 5

    # =========================================
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.config(bg="#f5f5f5")

        self.current_session_id = None
        self.current_course = "Mặc định"

        # Setup UI
        self.setup_ui()

        # Runtime variables
        self.camera = None
        self.running = False
        self.photo_image = None
        self.frame_count = 0
        self.cooldown_frames = 0
        self.marked_ids = set()

        # InsightFace
        self.app = InsightFaceSingleton.get_instance(
            name="buffalo_l",
            providers=["CPUExecutionProvider"],
            det_size=(480, 480),
            ctx_id=0
        )

        self.matcher = controller.face_matcher
        self.attendance_db = AttendanceDB(DBConnection())
        self.session_db = SessionDB(DBConnection())

        self.anti_spoof = AntiSpoofing()

    # =====================================================
    def create_placeholder_image(self):
        img = Image.new('RGB', (640, 480), color='#34495e')
        return ImageTk.PhotoImage(img)

    # =====================================================
    def setup_ui(self):
        # Create placeholder image for video label (640x480)
        self.placeholder_image = self.create_placeholder_image()

        content = create_scrollable_page(
            parent=self,
            title_text="✅ CHẤM CÔNG NHÂN VIÊN"
        )

        # tk.Label(
        #     content,
        #     text="Khu vực camera & nhận diện",
        #     font=("Arial", 14),
        #     bg="#f5f5f5"
        # ).pack(pady=10)

        session_frame = tk.LabelFrame(
            content,
            text=" Chọn hoặc tạo phiên ",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#2c3e50",
            relief="solid",
            borderwidth=2
        )
        session_frame.pack(fill="x", padx=20, pady=(10, 15))

        # Row 1: Chọn session hiện có
        tk.Label(
            session_frame,
            text="Phiên:",
            font=("Arial", 11),
            bg="white"
        ).grid(row=0, column=0, sticky="e", padx=10, pady=10)

        self.session_combo = ttk.Combobox(
            session_frame,
            state="readonly",
            width=50,
            font=("Arial", 11)
        )
        self.session_combo.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.session_combo.bind("<<ComboboxSelected>>",
                                self.on_session_selected)

        tk.Button(
            session_frame,
            text="Làm mới danh sách",
            command=self.load_sessions
        ).grid(row=0, column=2, padx=10, pady=10)

        # Row 2: Tạo session mới
        tk.Label(
            session_frame,
            text="Tạo mới:",
            font=("Arial", 11),
            bg="white"
        ).grid(row=1, column=0, sticky="e", padx=10, pady=10)

        self.new_course_entry = tk.Entry(
            session_frame,
            width=45,
            font=("Arial", 11)
        )
        self.new_course_entry.grid(
            row=1, column=1, padx=10, pady=10, sticky="ew")
        self.new_course_entry.insert(0, "Nhập tên phòng ban...")

        tk.Button(
            session_frame,
            text="Tạo & Chọn",
            bg="#27ae60",
            fg="white",
            command=self.create_and_select_session
        ).grid(row=1, column=2, padx=10, pady=10)

        session_frame.columnconfigure(1, weight=1)

        # ========= VIDEO + INFO SIDE BY SIDE =========
        main_container = tk.Frame(content, bg="#f5f5f5")
        main_container.pack(fill="both", expand=True)

        # Left: Video
        video_container = tk.Frame(main_container, bg="#f5f5f5")
        video_container.pack(side="left", padx=(0, 15))

        video_frame = tk.Frame(video_container, bg="#2c3e50",
                               relief="solid", borderwidth=2)
        video_frame.pack()

        self.video_label = tk.Label(
            video_frame,
            bg="#34495e",
            image=self.placeholder_image,
            text="📷 Camera sẽ hiển thị ở đây",
            font=("Arial", 12),
            fg="white",
            compound="center"
        )
        self.video_label.pack(padx=2, pady=2)

        # Right: Attendance Info
        info_container = tk.Frame(main_container, bg="#f5f5f5")
        info_container.pack(side="left", fill="both", expand=True)

        # Attendance List
        list_frame = tk.LabelFrame(
            info_container,
            text="  📋 Danh sách chấm công  ",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#2c3e50",
            relief="solid",
            borderwidth=2
        )
        list_frame.pack(fill="both", expand=True, pady=(0, 15))

        # Scrolled text for attendance list
        self.attendance_text = scrolledtext.ScrolledText(
            list_frame,
            font=("Consolas", 10),
            bg="#f8f9fa",
            fg="#2c3e50",
            relief="flat",
            padx=10,
            pady=10,
            state="disabled",
            wrap="word"
        )
        self.attendance_text.pack(fill="both", expand=True, padx=10, pady=10)

        # Statistics
        stats_frame = tk.LabelFrame(
            info_container,
            text="  📊 Thống kê  ",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#2c3e50",
            relief="solid",
            borderwidth=2
        )
        stats_frame.pack(fill="x")

        stats_grid = tk.Frame(stats_frame, bg="white")
        stats_grid.pack(padx=15, pady=15)

        tk.Label(
            stats_grid,
            text="Tổng số:",
            font=("Arial", 10, "bold"),
            bg="white"
        ).grid(row=0, column=0, sticky="w", pady=5)

        self.total_label = tk.Label(
            stats_grid,
            text="0 nhân viên",
            font=("Arial", 10),
            bg="white",
            fg="#27ae60"
        )
        self.total_label.grid(row=0, column=1, sticky="w",
                              padx=(10, 0), pady=5)

        # ========= STATUS =========
        self.status = tk.Label(
            content,
            text="✋ Nhấn 'Bắt đầu' để bắt đầu chấm công",
            font=("Arial", 11),
            fg="white",
            bg="#3498db",
            relief="solid",
            borderwidth=2,
            pady=12
        )
        self.status.pack(fill="x", pady=(15, 15))

        # ========= BUTTONS =========
        btn_frame = tk.Frame(content, bg="#f5f5f5")
        btn_frame.pack(pady=(0, 10))

        self.btn_start = tk.Button(
            btn_frame,
            text="▶ Bắt đầu",
            width=15,
            height=2,
            font=("Arial", 11, "bold"),
            bg="#27ae60",
            fg="white",
            activebackground="#229954",
            cursor="hand2",
            command=self.start
        )
        self.btn_start.pack(side="left", padx=5)

        self.btn_stop = tk.Button(
            btn_frame,
            text="⏸ Dừng",
            width=15,
            height=2,
            font=("Arial", 11, "bold"),
            bg="#e74c3c",
            fg="white",
            activebackground="#c0392b",
            cursor="hand2",
            state="disabled",
            command=self.stop
        )
        self.btn_stop.pack(side="left", padx=5)

        self.btn_back = tk.Button(
            btn_frame,
            text="◀ Quay lại",
            width=15,
            height=2,
            font=("Arial", 11, "bold"),
            bg="#95a5a6",
            fg="white",
            activebackground="#7f8c8d",
            cursor="hand2",
            command=self.back
        )
        self.btn_back.pack(side="left", padx=5)

    # =====================================================
    def add_attendance_log(self, student_id, name, similarity):
        """Add attendance log to the text widget"""
        self.attendance_text.config(state="normal")

        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] ✓ {name} ({student_id}) - {similarity:.2%}\n"

        self.attendance_text.insert("1.0", log_entry)
        self.attendance_text.config(state="disabled")

        # Update total count
        total = len(self.marked_ids)
        self.total_label.config(text=f"{total} nhân viên")

    def load_sessions(self):
        """Tải danh sách session từ DB (ưu tiên session chưa kết thúc)"""
        try:
            sessions = self.session_db.get_recent_sessions(limit=30)

            display_list = []
            self.session_map = {}  # display_text -> session_id

            for s in sessions:
                start_str = datetime.fromisoformat(
                    s["start_time"]).strftime("%d/%m/%Y %H:%M")
                status = " (Đang diễn ra)" if s.get("end_time") is None else ""
                display = f"{s['course']} - {start_str}{status} (ID: {s['id']})"
                display_list.append(display)
                self.session_map[display] = s["id"]

            self.session_combo["values"] = display_list

            if display_list:
                self.session_combo.current(0)
                self.on_session_selected(None)  # tự động chọn cái đầu
            else:
                self.session_combo.set("Chưa có phiên nào")
                self.current_session_id = None
                self.current_course = None

        except Exception as e:
            messagebox.showerror(
                "Lỗi", f"Không tải được danh sách phiên chấm\n{e}")
            self.session_combo.set("Lỗi tải dữ liệu")

    def on_session_selected(self, event):
        selected = self.session_combo.get()
        if selected in self.session_map:
            self.current_session_id = self.session_map[selected]
            self.current_course = selected.split(" - ")[0].strip()
            self.status.config(
                text=f"Đã chọn: {selected}\nNhấn 'Bắt đầu' để chấm công",
                bg="#3498db"
            )

    def create_and_select_session(self):
        course_name = self.new_course_entry.get().strip()
        if not course_name or course_name == "Nhập tên phòng ban...":
            messagebox.showwarning(
                "Cảnh báo", "Vui lòng nhập tên phòng ban")
            self.new_course_entry.focus_set()
            return

        try:
            session_id = self.session_db.create_session(
                course=course_name,
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(hours=2)  # mặc định 2 tiếng
            )
            messagebox.showinfo(
                "Thành công", f"Đã tạo phiên:\n{course_name}\nID: {session_id}")

            self.current_session_id = session_id
            self.current_course = course_name

            # Refresh và chọn session vừa tạo
            self.load_sessions()
            for display in self.session_combo["values"]:
                if f"ID: {session_id}" in display:
                    self.session_combo.set(display)
                    self.on_session_selected(None)
                    break

            self.status.config(
                text=f"Đã tạo & chọn: {course_name} (ID: {session_id})",
                bg="#27ae60"
            )

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không tạo được phiên\n{e}")

    # =====================================================
    def start(self):
        try:
            if self.current_session_id is None:
                messagebox.showwarning(
                    "Cảnh báo", "Vui lòng chọn hoặc tạo phiên trước!")
                return
            self.camera = Camera()
            self.running = True
            self.marked_ids.clear()
            self.cooldown_frames = 0
            self.frame_count = 0

            # Clear attendance log
            self.attendance_text.config(state="normal")
            self.attendance_text.delete("1.0", tk.END)
            self.attendance_text.config(state="disabled")
            self.total_label.config(text="0 nhân viên")

            self.status.config(
                text=f"🎥 Đang chấm công - Phiên: {self.current_course} (Session {self.current_session_id})",
                bg="#27ae60"
            )
            self.btn_start.config(state="disabled")
            self.btn_stop.config(state="normal")

            print(f"\n{'='*60}")
            print(f"🎯 Starting attendance tracking")
            print(f"{'='*60}\n")

            self.update_frame()

        except Exception as e:
            self.status.config(
                text=f"❌ Lỗi camera: {e}",
                bg="#e74c3c"
            )

    # =====================================================
    def update_frame(self):
        if not self.running or self.camera is None:
            return

        frame_bgr = self.camera.read()
        if frame_bgr is None:
            self.after(30, self.update_frame)
            return

        self.frame_count += 1
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        display_frame = frame_bgr.copy()  # frame để vẽ và hiển thị

        # Face detection + embedding (giữ nguyên)
        faces = []
        if self.frame_count % self.DETECT_INTERVAL == 0:
            small = cv2.resize(frame_rgb, None, fx=0.75, fy=0.75)
            faces = self.app.get(small)

        # ========== ANTI-SPOOF: Chạy YOLO detection trên FULL FRAME ==========
        spoof_info = self.anti_spoof.detect_spoof(frame_bgr)
        display_frame = self.anti_spoof.draw_results(frame_bgr, spoof_info)

        has_real = spoof_info['has_real']
        real_boxes = spoof_info['real_boxes']

        # ========== Logic chấm công ==========
        attendance_success = False

        if has_real:
            # Có ít nhất một box "real" → có khả năng là người thật
            for face in faces:
                bbox_scaled = (face.bbox * (1 / 0.75)).astype(int)
                f_left, f_top, f_right, f_bottom = bbox_scaled

                # Kiểm tra overlap với ít nhất một box "real" từ YOLO
                verified = False
                max_real_conf = 0.0
                for rx1, ry1, rx2, ry2, rconf in real_boxes:
                    # Overlap đơn giản (có giao nhau đáng kể)
                    if (f_left < rx2 and f_right > rx1 and
                            f_top < ry2 and f_bottom > ry1):
                        verified = True
                        max_real_conf = max(max_real_conf, rconf)
                        break  # chỉ cần overlap 1 cái là đủ

                if verified and face.normed_embedding is not None:
                    student_id, name, similarity = self.matcher.match(
                        face.normed_embedding)

                    if student_id and similarity >= self.SIMILARITY_THRESHOLD:
                        color = (0, 255, 0)
                        label_text = f"{name} ({similarity:.2f})"

                        if (self.cooldown_frames <= 0 and
                            student_id not in self.marked_ids and
                                self.current_session_id is not None):

                            if self.attendance_db.mark_attendance(
                                session_id=self.current_session_id,
                                student_id=student_id,
                                status="present"
                            ):
                                self.marked_ids.add(student_id)
                                self.cooldown_frames = self.COOLDOWN_MAX
                                self.add_attendance_log(
                                    student_id, name, similarity)

                                self.status.config(
                                    text=f"✅ Chấm công: {name} (Session {self.current_session_id})",
                                    bg="#27ae60"
                                )
                                print(
                                    f"Marked: {name} in session {self.current_session_id}")
                                attendance_success = True
                    else:
                        label_text = "Unknown"
                        color = (0, 165, 255)  # vàng cho unknown

                    # Vẽ box từ face detector
                    cv2.rectangle(display_frame, (f_left, f_top), (f_right, f_bottom),
                                  color, 2)
                    cv2.putText(display_frame, label_text, (f_left, max(f_top - 10, 10)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        # ========== Status tổng ==========
        if attendance_success:
            pass  # đã set ở trên
        elif has_real:
            self.status.config(
                text="✅ Khuôn mặt thật – đang kiểm tra danh tính", bg="#3498db")
        elif len(real_boxes) == 0 and len(faces) > 0:
            self.status.config(
                text="🚨 Có thể là giả mạo hoặc chất lượng thấp", bg="#e74c3c")
        else:
            self.status.config(
                text="Đang chờ phát hiện khuôn mặt...", bg="#7f8c8d")

        # Cooldown countdown
        if self.cooldown_frames > 0:
            self.cooldown_frames -= 1

        # ========== Hiển thị frame (giữ nguyên) ==========
        img = Image.fromarray(cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB))
        img = img.resize((640, 480), Image.Resampling.LANCZOS)
        self.photo_image = ImageTk.PhotoImage(img)
        self.video_label.config(image=self.photo_image, text="")

        self.after(30, self.update_frame)

    # =====================================================
    def stop(self):
        self.running = False
        if self.camera:
            self.camera.release()
            self.camera = None

        self.photo_image = None
        self.video_label.config(
            image=self.placeholder_image,
            text="📷 Camera sẽ hiển thị ở đây"
        )

        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")

        total = len(self.marked_ids)
        session_text = f" (Session {self.current_session_id})" if self.current_session_id else ""
        self.status.config(
            text=f"⏸ Đã dừng. Tổng: {total} nhân viên{session_text}",
            bg="#3498db"
        )

        self.current_session_id = None

        print(f"\n{'='*60}")
        print(
            f"Attendance stopped. Session {self.current_session_id} - Total: {total}")
        print(f"{'='*60}\n")

    def back(self):
        self.stop()
        self.controller.show_frame("HomeUI")
