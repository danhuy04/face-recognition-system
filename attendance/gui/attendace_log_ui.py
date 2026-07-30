import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
from database.attendance_db import AttendanceDB
from database.db_connection import DBConnection


class AttendanceLogWindow(tk.Toplevel):
    """Cửa sổ xem lịch sử chấm công từ SQLite"""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("📝 Lịch sử chấm công")
        self.geometry("1300x700")
        self.resizable(True, True)
        self.minsize(1000, 600)

        # Style
        self.bg_main = "#f5f5f5"
        self.bg_header = "#2c3e50"
        self.fg_header = "white"
        self.config(bg=self.bg_main)

        self.db = AttendanceDB(DBConnection())
        self.all_logs = []

        # ========== HEADER ==========
        header_frame = tk.Frame(self, bg=self.bg_header,
                                relief="solid", borderwidth=2)
        header_frame.pack(fill="x", padx=0, pady=0)

        tk.Label(header_frame, text="📝 LỊCH SỬ CHẤM CÔNG",
                 font=("Arial", 18, "bold"), bg=self.bg_header,
                 fg=self.fg_header).pack(pady=15, padx=15)

        # ========== FILTER FRAME ==========
        filter_frame = tk.Frame(self, bg=self.bg_main,
                                relief="solid", borderwidth=1)
        filter_frame.pack(fill="x", padx=15, pady=10)

        # Left: Date filter
        left_frame = tk.Frame(filter_frame, bg=self.bg_main)
        left_frame.pack(side="left", padx=10, pady=10)

        tk.Label(left_frame, text="📅 Chọn ngày:", font=("Arial", 10),
                 bg=self.bg_main).pack(side="left", padx=(0, 5))

        self.date_entry = tk.Entry(left_frame, width=15, font=("Arial", 10),
                                   relief="solid", borderwidth=1)
        self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        self.date_entry.pack(side="left", padx=(0, 10), ipady=4)

        # Middle: Filter buttons
        btn_filter_frame = tk.Frame(filter_frame, bg=self.bg_main)
        btn_filter_frame.pack(side="left", padx=10, pady=10)

        tk.Button(btn_filter_frame, text="🔍 Lọc ngày", bg="#3498db", fg="white",
                  font=("Arial", 9, "bold"), relief="raised",
                  activebackground="#2980b9", command=self.load_by_date,
                  padx=10, pady=5).pack(side="left", padx=3)

        tk.Button(btn_filter_frame, text="📋 Xem tất cả", bg="#9b59b6", fg="white",
                  font=("Arial", 9, "bold"), relief="raised",
                  activebackground="#8e44ad", command=self.load_all,
                  padx=10, pady=5).pack(side="left", padx=3)

        # Right: Search box
        right_frame = tk.Frame(filter_frame, bg=self.bg_main)
        right_frame.pack(side="right", padx=10, pady=10)

        tk.Label(right_frame, text="🔎 Tìm Mã NV:", font=("Arial", 10),
                 bg=self.bg_main).pack(side="left", padx=(0, 5))

        self.search_entry = tk.Entry(right_frame, width=20, font=("Arial", 10),
                                     relief="solid", borderwidth=1)
        self.search_entry.pack(side="left", padx=(0, 5), ipady=4)
        self.search_entry.bind(
            "<KeyRelease>", lambda e: self.filter_by_student_id())

        # ========== STATS FRAME ==========
        stats_frame = tk.Frame(self, bg="white", relief="solid", borderwidth=1)
        stats_frame.pack(fill="x", padx=15, pady=(0, 10))

        self.stats_label = tk.Label(stats_frame, text="📊 Thống kê: Tổng: 0 | Hôm nay: 0",
                                    bg="white", font=("Arial", 10),
                                    fg="#2c3e50", justify="left")
        self.stats_label.pack(anchor="w", padx=15, pady=10)

        # ========== TREEVIEW ==========
        tree_frame = tk.Frame(self, bg=self.bg_main)
        tree_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        columns = ("Mã NV", "Thời gian",
                   "Ngày", "Trạng thái", "Session")
        self.tree = ttk.Treeview(
            tree_frame, columns=columns, show="headings")

        self.tree.heading("Mã NV", text="🆔 Mã NV")
        self.tree.heading("Thời gian", text="🕐 Thời gian")
        self.tree.heading("Ngày", text="📅 Ngày")
        self.tree.heading("Trạng thái", text="✅ Trạng thái")
        self.tree.heading("Session", text="📋 Session")

        self.tree.column("Mã NV", width=100, anchor="center")
        self.tree.column("Thời gian", width=100, anchor="center")
        self.tree.column("Ngày", width=120, anchor="center")
        self.tree.column("Trạng thái", width=100, anchor="center")
        self.tree.column("Session", width=150, anchor="center")

        # Styling treeview
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview",
                        font=("Arial", 9),
                        rowheight=24,
                        background="#ffffff",
                        foreground="#2c3e50",
                        fieldbackground="#ffffff",
                        relief="solid",
                        borderwidth=0)
        style.configure("Treeview.Heading",
                        font=("Arial", 10, "bold"),
                        background="#34495e",
                        foreground="white",
                        relief="raised")
        style.map('Treeview', background=[('selected', '#3498db')])

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)  # type: ignore

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # ========== BUTTONS ==========
        btn_frame = tk.Frame(self, bg=self.bg_main)
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))

        tk.Button(btn_frame, text="💾 Export CSV", bg="#27ae60", fg="white",
                  font=("Arial", 10, "bold"), relief="raised", activebackground="#229954",
                  command=self.export_csv, padx=15, pady=8).pack(side="left", padx=5)

        tk.Button(btn_frame, text="🔄 Làm mới", bg="#3498db", fg="white",
                  font=("Arial", 10, "bold"), relief="raised", activebackground="#2980b9",
                  command=self.load_by_date, padx=15, pady=8).pack(side="left", padx=5)

        tk.Button(btn_frame, text="❌ Đóng", bg="#95a5a6", fg="white",
                  font=("Arial", 10, "bold"), relief="raised", activebackground="#7f8c8d",
                  command=self.on_closing, padx=15, pady=8).pack(side="right", padx=5)

        # Load mặc định hôm nay
        self.load_by_date()

        # Đóng DB khi window đóng
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.db.close()
        self.destroy()

    def _insert_log(self, row, index=None):
        """Insert log entry với index (để xen kẽ màu)"""
        tag = "oddrow" if (index or 0) % 2 == 0 else "evenrow"

        student_id = row[0] if len(row) > 0 else ""
        time_display = datetime.fromisoformat(row[1]).strftime(
            "%H:%M:%S") if len(row) > 1 and row[1] else ""
        date_display = row[2] if len(row) > 2 else ""
        status = row[3] if len(row) > 3 else ""
        session = row[4] if len(row) > 4 else ""
        print("Session_id", session)
        self.tree.insert("", "end", tags=(tag,), values=(
            student_id,
            time_display,
            date_display,
            status,
            session
        ))

    def update_stats(self, logs=None):
        """Cập nhật thống kê"""
        if logs is None:
            logs = self.all_logs

        total_all = len(self.db.get_all_attendance())
        today = date.today().strftime("%Y-%m-%d")
        today_logs = len(self.db.get_attendance_by_date(today))

        self.stats_label.config(
            text=f"📊 Thống kê: Tổng cộng: {total_all} | Hôm nay ({today}): {today_logs}"
        )

    def load_by_date(self):
        date_str = self.date_entry.get().strip()
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror(
                "❌ Lỗi", "Định dạng ngày không đúng (YYYY-MM-DD)")
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        logs = self.db.get_attendance_by_date(date_str)
        self.all_logs = logs

        for i, log in enumerate(logs):
            self._insert_log(log, i)

        # Configure row colors
        self.tree.tag_configure("oddrow", background="#f8f9fa")
        self.tree.tag_configure("evenrow", background="#ffffff")

        if not logs:
            self.tree.insert("", "end", tags=("oddrow",), values=(
                "", "", "Chưa có chấm công nào trong ngày này", "", "", ""))

        self.update_stats(logs)

    def load_all(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        logs = self.db.get_all_attendance()
        self.all_logs = logs

        for i, log in enumerate(logs):
            self._insert_log(log, i)

        # Configure row colors
        self.tree.tag_configure("oddrow", background="#f8f9fa")
        self.tree.tag_configure("evenrow", background="#ffffff")

        if not logs:
            self.tree.insert("", "end", tags=("oddrow",), values=(
                "", "", "Chưa có lịch sử chấm công", "", "", ""))

        self.update_stats(logs)

    def filter_by_student_id(self):
        """Lọc danh sách theo Mã SV"""
        search_text = self.search_entry.get().lower().strip()

        for item in self.tree.get_children():
            self.tree.delete(item)

        filtered = [log for log in self.all_logs
                    if search_text in str(log[0]).lower()]

        for i, log in enumerate(filtered):
            self._insert_log(log, i)

        # Configure row colors
        self.tree.tag_configure("oddrow", background="#f8f9fa")
        self.tree.tag_configure("evenrow", background="#ffffff")

    def export_csv(self):
        if not self.all_logs:
            messagebox.showwarning(
                "⚠️ Cảnh báo", "Không có dữ liệu để export!")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"lich_su_cham_cong_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            title="💾 Xuất lịch sử chấm công"
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["Mã NV", "Thời gian",
                                "Ngày", "Trạng thái", "Session"])
                for log in self.all_logs:
                    time_str = datetime.fromisoformat(
                        log[1]).strftime("%H:%M:%S") if log[1] else ""
                    writer.writerow([
                        log[0],
                        time_str,
                        log[2],
                        log[3],
                        log[4] if len(log) > 4 else ""
                    ])
            messagebox.showinfo("✅ Thành công", f"Đã xuất file:\n{file_path}")
        except Exception as e:
            messagebox.showerror("❌ Lỗi", f"Không thể xuất file:\n{e}")
