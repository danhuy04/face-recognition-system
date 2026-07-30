import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2

from gui.scrollable import create_scrollable_page
from gui.base_ui import BaseFrame
from core.camera import Camera
from core.enroll_manager import EnrollManager
from core.insightface_singleton import InsightFaceSingleton
from core.anti_spoofing import AntiSpoofing


class EnrollUI(BaseFrame):
    # ================= CONFIG =================
    MAX_SAMPLES = 15
    SAMPLE_COOLDOWN = 4
    DETECT_INTERVAL = 2
    MIN_FACE_SIZE = 120
    MIN_CONFIDENCE = 0.65

    # =========================================
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.config(bg="#f5f5f5")  # Light gray background

        # Create main container with scrollbar support
        self.setup_ui()

        # Runtime variables
        self.camera = None
        self.running = False
        self.photo_image = None
        self.frame_count = 0
        self.sample_cooldown = 0
        self.last_sample_count = 0

        # EnrollManager
        self.enroll_mgr = EnrollManager(max_samples=self.MAX_SAMPLES)

        # InsightFace
        self.app = InsightFaceSingleton.get_instance(
            name="buffalo_l",
            providers=["CPUExecutionProvider"],
            det_size=(480, 480),
            ctx_id=0
        )

        self.anti_spoof = AntiSpoofing()

    # =====================================================
    def create_placeholder_image(self):
        """Create a placeholder image for the video label"""
        img = Image.new('RGB', (640, 480), color='#34495e')
        return ImageTk.PhotoImage(img)

    # =====================================================
    def setup_ui(self):
        # Create placeholder image for video label (640x480)
        self.placeholder_image = self.create_placeholder_image()

        content = create_scrollable_page(
            parent=self,
            title_text="📋 ĐĂNG KÝ NHÂN VIÊN"
        )

        # tk.Label(
        #     content,
        #     text="Thông tin sinh viên",
        #     font=("Arial", 14),
        #     bg="#f5f5f5"
        # ).pack(pady=10)

        # ========= FORM =========
        form_frame = tk.LabelFrame(
            content,
            text="  Thông tin nhân viên  ",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#2c3e50",
            relief="solid",
            borderwidth=2
        )
        form_frame.pack(fill="x", pady=(0, 15))

        # Form inputs
        form_grid = tk.Frame(form_frame, bg="white")
        form_grid.pack(padx=20, pady=15)

        tk.Label(form_grid, text="Mã NV:", bg="white", font=("Arial", 10)).grid(
            row=0, column=0, sticky="e", padx=(0, 10), pady=8
        )
        tk.Label(form_grid, text="Họ tên:", bg="white", font=("Arial", 10)).grid(
            row=1, column=0, sticky="e", padx=(0, 10), pady=8
        )

        self.entry_id = tk.Entry(form_grid, width=35, font=("Arial", 10))
        self.entry_name = tk.Entry(form_grid, width=35, font=("Arial", 10))
        self.entry_id.grid(row=0, column=1, pady=8)
        self.entry_name.grid(row=1, column=1, pady=8)

        # ========= VIDEO + INSTRUCTIONS SIDE BY SIDE =========
        video_instruction_frame = tk.Frame(content, bg="#f5f5f5")
        video_instruction_frame.pack(fill="both", expand=True, pady=(0, 15))

        # Left: Video
        video_container = tk.Frame(video_instruction_frame, bg="#f5f5f5")
        video_container.pack(side="left", padx=(0, 10))

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

        # Right: Instructions
        instruction_container = tk.Frame(video_instruction_frame, bg="#f5f5f5")
        instruction_container.pack(side="left", fill="both", expand=True)

        instruction_frame = tk.LabelFrame(
            instruction_container,
            text="  📖 Hướng dẫn  ",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#2c3e50",
            relief="solid",
            borderwidth=2
        )
        instruction_frame.pack(fill="both", expand=True)

        instructions = [
            ("1️⃣", "Nhìn thẳng vào camera"),
            ("2️⃣", "Giữ khoảng cách 50-70cm"),
            ("3️⃣", "Đảm bảo ánh sáng đủ sáng"),
            ("4️⃣", "Xoay nhẹ đầu khi được yêu cầu"),
            ("5️⃣", "Giữ khuôn mặt trong khung xanh"),
        ]

        for icon, text in instructions:
            inst_row = tk.Frame(instruction_frame, bg="white")
            inst_row.pack(fill="x", padx=15, pady=5)

            tk.Label(
                inst_row,
                text=icon,
                font=("Arial", 14),
                bg="white"
            ).pack(side="left", padx=(0, 10))

            tk.Label(
                inst_row,
                text=text,
                font=("Arial", 10),
                bg="white",
                anchor="w",
                wraplength=350,  # Allow text to wrap if needed
                justify="left"
            ).pack(side="left", fill="x", expand=True)

        # ========= QUALITY INDICATORS =========
        quality_frame = tk.Frame(
            content, bg="white", relief="solid", borderwidth=1)
        quality_frame.pack(fill="x", pady=(0, 10))

        tk.Label(
            quality_frame,
            text="Chất lượng:",
            font=("Arial", 9, "bold"),
            bg="white"
        ).pack(side="left", padx=10)

        self.quality_labels = {}
        indicators = [
            ("face", "👤 Khuôn mặt"),
            ("distance", "📏 Khoảng cách"),
            ("confidence", "✨ Độ rõ"),
            ("diversity", "🔄 Đa dạng"),
        ]

        for key, text in indicators:
            label = tk.Label(
                quality_frame,
                text=text,
                font=("Arial", 9),
                bg="#95a5a6",
                fg="white",
                relief="raised",
                padx=10,
                pady=5
            )
            label.pack(side="left", padx=5, pady=8)
            self.quality_labels[key] = label

        # ========= PROGRESS BAR =========
        progress_frame = tk.Frame(
            content, bg="white", relief="solid", borderwidth=1)
        progress_frame.pack(fill="x", pady=(0, 10))

        tk.Label(
            progress_frame,
            text="Tiến độ thu thập:",
            font=("Arial", 10, "bold"),
            bg="white"
        ).pack(anchor="w", padx=15, pady=(10, 5))

        self.progress = ttk.Progressbar(
            progress_frame,
            mode="determinate",
            length=400,
            maximum=self.MAX_SAMPLES
        )
        self.progress.pack(fill="x", padx=15, pady=(0, 5))

        self.progress_label = tk.Label(
            progress_frame,
            text=f"0/{self.MAX_SAMPLES} mẫu (0%)",
            font=("Arial", 9),
            bg="white",
            fg="#7f8c8d"
        )
        self.progress_label.pack(anchor="w", padx=15, pady=(0, 10))

        # ========= STATUS =========
        self.status = tk.Label(
            content,
            text="✋ Nhập thông tin và nhấn 'Bắt đầu' để tiếp tục",
            font=("Arial", 11),
            fg="white",
            bg="#3498db",
            relief="solid",
            borderwidth=2,
            pady=12
        )
        self.status.pack(fill="x", pady=(0, 15))

        # ========= BUTTONS =========
        self.btn_frame = tk.Frame(content, bg="#f5f5f5")
        self.btn_frame.pack(pady=(0, 10))

        self.btn_start = tk.Button(
            self.btn_frame,
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

        self.btn_back = tk.Button(
            self.btn_frame,
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
    def update_quality_indicator(self, key, status):
        """Cập nhật chỉ báo chất lượng"""
        colors = {
            "good": "#27ae60",
            "warning": "#f39c12",
            "bad": "#e74c3c",
            "inactive": "#95a5a6"
        }

        if key in self.quality_labels:
            self.quality_labels[key].config(bg=colors.get(status, "#95a5a6"))

    # =====================================================
    def start(self):
        self.student_id = self.entry_id.get().strip()
        self.name = self.entry_name.get().strip()

        if not self.student_id or not self.name:
            self.status.config(
                text="⚠️ Vui lòng nhập đầy đủ Mã NV và Họ tên!",
                bg="#e74c3c"
            )
            return

        self.entry_id.config(state="disabled")
        self.entry_name.config(state="disabled")
        self.btn_start.config(state="disabled")

        try:
            self.camera = Camera()
            self.running = True
            self.frame_count = 0
            self.sample_cooldown = 0
            self.last_sample_count = 0

            self.progress["value"] = 0
            self.progress_label.config(text=f"0/{self.MAX_SAMPLES} mẫu (0%)")

            print(f"\n{'='*60}")
            print(f"🎯 Starting enrollment: {self.name} ({self.student_id})")
            print(f"{'='*60}\n")

            self.status.config(
                text="🎥 Đang khởi động camera...",
                bg="#3498db"
            )
            self.update_frame()

        except Exception as e:
            self.status.config(text=f"❌ Lỗi camera: {e}", bg="#e74c3c")
            self.btn_start.config(state="normal")
            self.entry_id.config(state="normal")
            self.entry_name.config(state="normal")

    # =====================================================
    def update_frame(self):
        if not self.running or self.camera is None:
            return

        frame_bgr = self.camera.read()
        if frame_bgr is None:
            self.after(40, self.update_frame)
            return

        self.frame_count += 1
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        display_frame = frame_bgr.copy()  # dùng để vẽ và hiển thị

        faces = []
        if self.frame_count % self.DETECT_INTERVAL == 0:
            faces = self.app.get(frame_rgb)

        status_text = None
        status_color = "#3498db"

        # Reset indicators
        for key in self.quality_labels:
            self.update_quality_indicator(key, "inactive")

        # ========== ANTI-SPOOF: Chạy YOLO detection trên FULL FRAME ==========
        spoof_info = self.anti_spoof.detect_spoof(frame_bgr)
        display_frame = self.anti_spoof.draw_results(frame_bgr, spoof_info)
        has_real = spoof_info['has_real']

        # ========== Xử lý khuôn mặt detect được ==========
        if faces:
            face = faces[0]  # giả sử chỉ xử lý 1 mặt trong đăng ký
            l, t, r, b = face.bbox.astype(int)
            w, h = r - l, b - t

            # Kiểm tra overlap với box "real" từ YOLO
            verified_real = False
            max_real_conf = 0.0
            for rx1, ry1, rx2, ry2, rconf in spoof_info['real_boxes']:
                # Overlap đơn giản (có giao nhau đáng kể)
                if (l < rx2 and r > rx1 and t < ry2 and b > ry1):
                    verified_real = True
                    max_real_conf = max(max_real_conf, rconf)
                    break

            if not verified_real or not has_real:
                # Không có box real overlap → coi như spoof hoặc không xác thực
                status_text = "🚨 Phát hiện khả năng giả mạo hoặc không rõ ràng"
                status_color = "#e74c3c"
                self.update_quality_indicator("face", "bad")
                cv2.rectangle(display_frame, (l, t), (r, b), (0, 0, 255), 3)
                cv2.putText(display_frame, "SPOOF?", (l, t - 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            else:
                # Có xác thực real → tiếp tục check chất lượng
                self.update_quality_indicator("face", "good")

                is_distance_ok = False
                is_confidence_ok = False

                # Distance check
                if w < self.MIN_FACE_SIZE or h < self.MIN_FACE_SIZE:
                    self.update_quality_indicator("distance", "bad")
                    status_text = "📏 Đưa khuôn mặt lại GẦN camera hơn"
                    status_color = "#e67e22"
                    cv2.rectangle(display_frame, (l, t), (r, b), (0, 165, 255), 3)
                elif w > 400 or h > 400:
                    self.update_quality_indicator("distance", "bad")
                    status_text = "📏 Lùi ra XA camera một chút"
                    status_color = "#e67e22"
                    cv2.rectangle(display_frame, (l, t), (r, b), (0, 165, 255), 3)
                else:
                    self.update_quality_indicator("distance", "good")
                    is_distance_ok = True

                # Confidence check (từ face detector)
                if face.det_score < self.MIN_CONFIDENCE:
                    self.update_quality_indicator("confidence", "bad")
                    status_text = f"✨ Ánh sáng chưa đủ ({face.det_score*100:.0f}%)"
                    status_color = "#e67e22"
                    cv2.rectangle(display_frame, (l, t), (r, b), (0, 0, 255), 3)
                else:
                    self.update_quality_indicator("confidence", "good")
                    is_confidence_ok = True

                # Chỉ thu thập sample khi tất cả OK
                if is_distance_ok and is_confidence_ok:
                    cv2.rectangle(display_frame, (l, t), (r, b), (0, 255, 0), 3)
                    cv2.putText(display_frame, f"REAL {max_real_conf:.2f}", (l, t - 25),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

                    if self.sample_cooldown <= 0:
                        ok = self.enroll_mgr.add_frame(frame_rgb)

                        if ok:
                            count = len(self.enroll_mgr.samples)
                            self.sample_cooldown = self.SAMPLE_COOLDOWN

                            self.progress["value"] = count
                            percentage = int((count / self.MAX_SAMPLES) * 100)
                            self.progress_label.config(
                                text=f"{count}/{self.MAX_SAMPLES} mẫu ({percentage}%)",
                                fg="#27ae60"
                            )

                            status_text = f"✅ Thu thập mẫu {count}/{self.MAX_SAMPLES}"
                            status_color = "#27ae60"
                            self.update_quality_indicator("diversity", "good")

                            if self.enroll_mgr.is_complete():
                                print("\n🎉 Enrollment completed!")
                                success = self.enroll_mgr.save(self.student_id, self.name)
                                if success:
                                    self.show_success_screen()
                                    if hasattr(self.controller, 'face_matcher'):
                                        self.controller.face_matcher.reload()
                                        print("Đã reload FaceMatcher")
                                    else:
                                        print("Warning: Controller chưa có face_matcher")
                                else:
                                    self.status.config(text="❌ Lỗi khi lưu dữ liệu!", bg="#e74c3c")
                                return
                        else:
                            self.update_quality_indicator("diversity", "warning")
                            status_text = "🔄 Xoay nhẹ đầu sang trái/phải/lên/xuống"
                            status_color = "#f39c12"
                    else:
                        status_text = f"⏱ Giữ yên ({self.sample_cooldown} frames)..."
                        status_color = "#3498db"
                        self.update_quality_indicator("diversity", "warning")

                cv2.putText(display_frame,
                            f"{face.det_score*100:.0f}%",
                            (l, t - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 255, 0) if is_confidence_ok else (0, 0, 255),
                            2)

        else:
            status_text = "👤 Không phát hiện khuôn mặt"
            status_color = "#e74c3c"
            self.update_quality_indicator("face", "bad")

        if self.sample_cooldown > 0:
            self.sample_cooldown -= 1

        if status_text:
            self.status.config(text=status_text, bg=status_color)

        # Display frame
        img = Image.fromarray(cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB))
        img = img.resize((640, 480), Image.Resampling.LANCZOS)
        self.photo_image = ImageTk.PhotoImage(img)
        self.video_label.config(image=self.photo_image, text="")

        self.after(40, self.update_frame)

    # =====================================================
    def show_success_screen(self):
        self.stop()

        self.video_label.config(image="", bg="#2ecc71",
                                text="✅", font=("Arial", 80), fg="white")

        self.btn_start.pack_forget()
        self.btn_back.pack_forget()

        self.status.config(
            text="🎉 ĐĂNG KÝ THÀNH CÔNG!",
            font=("Arial", 16, "bold"),
            bg="#27ae60"
        )

        self.progress_label.config(
            text=f"✓ Hoàn thành {self.MAX_SAMPLES}/{self.MAX_SAMPLES} mẫu",
            fg="#27ae60",
            font=("Arial", 10, "bold")
        )

        for label in self.quality_labels.values():
            label.pack_forget()

        # Success buttons
        self.btn_continue = tk.Button(
            self.btn_frame,
            text="➕ Tiếp tục đăng ký",
            font=("Arial", 11, "bold"),
            bg="#27ae60",
            fg="white",
            width=18,
            height=2,
            cursor="hand2",
            command=self.reset_form
        )
        self.btn_continue.pack(side="left", padx=5)

        self.btn_home = tk.Button(
            self.btn_frame,
            text="🏠 Về trang chủ",
            font=("Arial", 11, "bold"),
            bg="#3498db",
            fg="white",
            width=18,
            height=2,
            cursor="hand2",
            command=self.back
        )
        self.btn_home.pack(side="left", padx=5)

    # =====================================================
    def reset_form(self):
        if hasattr(self, "btn_continue"):
            self.btn_continue.destroy()
        if hasattr(self, "btn_home"):
            self.btn_home.destroy()

        self.video_label.config(
            image=self.placeholder_image,
            bg="#34495e",
            text="📷 Camera sẽ hiển thị ở đây",
            font=("Arial", 12)
        )

        self.entry_id.delete(0, tk.END)
        self.entry_name.delete(0, tk.END)
        self.entry_id.config(state="normal")
        self.entry_name.config(state="normal")

        self.status.config(
            text="✋ Nhập thông tin và nhấn 'Bắt đầu' để tiếp tục",
            bg="#3498db",
            font=("Arial", 11)
        )

        self.progress["value"] = 0
        self.progress_label.config(
            text=f"0/{self.MAX_SAMPLES} mẫu (0%)",
            fg="#7f8c8d",
            font=("Arial", 9)
        )

        self.btn_start.pack(side="left", padx=5)
        self.btn_back.pack(side="left", padx=5)
        self.btn_start.config(state="normal")

        for label in self.quality_labels.values():
            label.pack(side="left", padx=5, pady=8)
            label.config(bg="#95a5a6")

        self.enroll_mgr.reset()
        self.sample_cooldown = 0
        self.frame_count = 0
        self.last_sample_count = 0

    # =====================================================
    def stop(self):
        self.running = False
        if self.camera:
            self.camera.release()
            self.camera = None
        self.photo_image = None
        self.sample_cooldown = 0
        self.frame_count = 0

    def back(self):
        self.stop()
        self.controller.show_frame("HomeUI")
