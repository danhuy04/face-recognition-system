import tkinter as tk
from gui.attendace_log_ui import AttendanceLogWindow
from gui.base_ui import BaseFrame
from gui.student_list_ui import StudentListWindow

class HomeUI(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.config(bg="#f5f5f5")
        
        # ========= HEADER =========
        header = tk.Frame(self, bg="#2c3e50", height=80)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="🏠 HỆ THỐNG CHẤM CÔNG FACE ID",
            font=("Arial", 22, "bold"),
            bg="#2c3e50",
            fg="white"
        ).pack(expand=True)

        # ========= FOOTER =========
        tk.Label(
            self,
            text="© 2026 Face Attendance System. Ver 1.0",
            font=("Arial", 9),
            bg="#f5f5f5",
            fg="#95a5a6"
        ).pack(side="bottom", pady=15, fill="x")

        # ========= CENTERED CONTAINER =========
        center_frame = tk.Frame(self, bg="#f5f5f5")
        center_frame.pack(expand=True, fill="both", padx=50, pady=20)
        
        # Căn giữa nội dung bên trong center_frame
        center_frame.grid_columnconfigure(0, weight=1)
        center_frame.grid_rowconfigure(0, weight=1) # Top spacer
        center_frame.grid_rowconfigure(2, weight=1) # Bottom spacer
        
        # Menu Grid Container
        menu_container = tk.Frame(center_frame, bg="#f5f5f5")
        menu_container.grid(row=1, column=0) 
        
        menu_container.columnconfigure(0, weight=1)
        menu_container.columnconfigure(1, weight=1)

        # === Row 1: Main Actions ===
        self.create_menu_button(
            menu_container,
            text="👤 ĐĂNG KÝ NHÂN VIÊN",
            desc="Thêm dữ liệu khuôn mặt mới",
            bg_color="#2ecc71", # Green
            command=lambda: controller.show_frame("EnrollUI"),
            row=0, col=0
        )

        self.create_menu_button(
            menu_container,
            text="✅ CHẤM CÔNG",
            desc="Chấm công realtime bằng camera",
            bg_color="#3498db", # Blue
            command=lambda: controller.show_frame("AttendanceUI"),
            row=0, col=1
        )

        # === Row 2: Management ===
        self.create_menu_button(
            menu_container,
            text="📋 DANH SÁCH NHÂN VIÊN",
            desc="Xem và quản lý thông tin NV",
            bg_color="#9b59b6", # Purple
            command=self.open_student_list,
            row=1, col=0
        )

        self.create_menu_button(
            menu_container,
            text="📊 LỊCH SỬ CHẤM CÔNG",
            desc="Xem báo cáo ra/vào",
            bg_color="#f1c40f", # Yellow/Orange
            text_color="#2c3e50", 
            command=self.open_attendance_log,
            row=1, col=1
        )

        # === Row 3: Exit ===
        btn_exit = tk.Button(
            menu_container,
            text="❌ THOÁT HỆ THỐNG",
            font=("Arial", 12, "bold"),
            bg="#e74c3c",
            fg="white",
            relief="raised",
            cursor="hand2",
            height=2,
            command=controller.quit
        )
        btn_exit.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(20, 0), padx=15)

    def create_menu_button(self, parent, text, desc, bg_color, command, row, col, text_color="white"):
        wrapper = tk.Frame(parent, bg="#f5f5f5")
        wrapper.grid(row=row, column=col, padx=15, pady=15)
        
        frame = tk.Frame(
            wrapper,
            bg=bg_color,
            relief="raised",
            borderwidth=2,
            cursor="hand2",
            width=350,   
            height=150   
        )
        frame.pack()
        frame.pack_propagate(False) # Giữ kích thước cố định
        
        # Sự kiện click
        frame.bind("<Button-1>", lambda e: command())
        
        # Inner content container
        inner = tk.Frame(frame, bg=bg_color)
        inner.place(relx=0.5, rely=0.5, anchor="center")
        
        title = tk.Label(
            inner,
            text=text,
            font=("Arial", 14, "bold"),
            bg=bg_color,
            fg=text_color
        )
        title.pack(pady=(0, 10))
        
        subtitle = tk.Label(
            inner,
            text=desc,
            font=("Arial", 11),
            bg=bg_color,
            fg=text_color
        )
        subtitle.pack()
        
        # Propagate click events
        inner.bind("<Button-1>", lambda e: command())
        title.bind("<Button-1>", lambda e: command())
        subtitle.bind("<Button-1>", lambda e: command())

    def open_student_list(self):
        StudentListWindow(self,controller=self.controller)

    def open_attendance_log(self):
        AttendanceLogWindow(self)