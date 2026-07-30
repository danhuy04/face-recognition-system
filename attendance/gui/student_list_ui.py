import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from datetime import datetime

from core.student_manager import StudentManager


class StudentListWindow(tk.Toplevel):

    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.title("📋 Danh sách nhân viên đã đăng ký")
        self.geometry("1200x700")
        self.resizable(True, True)
        self.minsize(1000, 600)

        # Style
        self.bg_main = "#f5f5f5"
        self.bg_header = "#2c3e50"
        self.fg_header = "white"
        self.bg_accent = "#3498db"
        self.config(bg=self.bg_main)

        self.controller = controller
        self.manager = StudentManager(controller=self.controller)
        self.all_students = []

        # ========== HEADER ==========
        header_frame = tk.Frame(self, bg=self.bg_header,
                                relief="solid", borderwidth=2)
        header_frame.pack(fill="x", padx=0, pady=0)

        tk.Label(header_frame, text="📋 DANH SÁCH NHÂN VIÊN",
                 font=("Arial", 18, "bold"), bg=self.bg_header,
                 fg=self.fg_header).pack(pady=15, padx=15)

        # ========== SEARCH & STATS FRAME ==========
        control_frame = tk.Frame(self, bg=self.bg_main)
        control_frame.pack(fill="x", padx=15, pady=10)

        # Search bar
        search_frame = tk.Frame(control_frame, bg=self.bg_main)
        search_frame.pack(side="left", fill="x", expand=True)

        tk.Label(search_frame, text="🔍 Tìm kiếm:", bg=self.bg_main,
                 font=("Arial", 10)).pack(side="left", padx=(0, 5))

        self.search_entry = tk.Entry(search_frame, width=30, font=("Arial", 10),
                                     relief="solid", borderwidth=1)
        self.search_entry.pack(side="left", padx=(0, 10), ipady=5)
        self.search_entry.bind(
            "<KeyRelease>", lambda e: self.filter_students())

        # Statistics
        stats_frame = tk.Frame(control_frame, bg=self.bg_main)
        stats_frame.pack(side="right", padx=(10, 0))

        self.stats_label = tk.Label(stats_frame, text="Tổng: 0 | Avg Quality: 0.00",
                                    bg=self.bg_main, font=("Arial", 9),
                                    fg="#2c3e50")
        self.stats_label.pack(side="right")

        # ========== TREEVIEW ==========
        tree_frame = tk.Frame(self, bg=self.bg_main)
        tree_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        columns = ("Mã NV", "Họ tên", "Số mẫu", "Quality", "Ngày đăng ký")
        self.tree = ttk.Treeview(
            tree_frame, columns=columns, show="headings")

        # Configure columns
        self.tree.heading("Mã NV", text="🆔 Mã NV")
        self.tree.heading("Họ tên", text="👤 Họ tên")
        self.tree.heading("Số mẫu", text="📸 Mẫu")
        self.tree.heading("Quality", text="⭐ Quality")
        self.tree.heading("Ngày đăng ký", text="📅 Ngày đăng ký")

        self.tree.column("Mã NV", width=120, anchor="center")
        self.tree.column("Họ tên", width=250)
        self.tree.column("Số mẫu", width=80, anchor="center")
        self.tree.column("Quality", width=120, anchor="center")
        self.tree.column("Ngày đăng ký", width=150, anchor="center")

        # Styling treeview
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview",
                        font=("Arial", 10),
                        rowheight=25,
                        background="#ffffff",
                        foreground="#2c3e50",
                        fieldbackground="#ffffff",
                        relief="solid",
                        borderwidth=0)
        style.configure("Treeview.Heading",
                        font=("Arial", 11, "bold"),
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

        self.btn_export = tk.Button(
            btn_frame, text="💾 Export CSV", bg="#27ae60", fg="white",
            font=("Arial", 10, "bold"), relief="raised", activebackground="#229954",
            command=self.export_csv, padx=15, pady=8)
        self.btn_export.pack(side="left", padx=5)

        self.btn_refresh = tk.Button(
            btn_frame, text="🔄 Làm mới", bg="#3498db", fg="white",
            font=("Arial", 10, "bold"), relief="raised", activebackground="#2980b9",
            command=self.refresh_list, padx=15, pady=8)
        self.btn_refresh.pack(side="left", padx=5)

        self.btn_delete = tk.Button(
            btn_frame, text="🗑️ Xóa nhân viên", bg="#e74c3c", fg="white",
            font=("Arial", 10, "bold"), relief="raised", activebackground="#c0392b",
            command=self.delete_selected, padx=15, pady=8)
        self.btn_delete.pack(side="left", padx=5)

        self.btn_close = tk.Button(
            btn_frame, text="❌ Đóng", bg="#95a5a6", fg="white",
            font=("Arial", 10, "bold"), relief="raised", activebackground="#7f8c8d",
            command=self.destroy, padx=15, pady=8)
        self.btn_close.pack(side="right", padx=5)

        # Load danh sách lần đầu
        self.refresh_list()

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.all_students = self.manager.get_all_students()

        for i, student in enumerate(self.all_students):
            # Xen kẽ màu background cho dòng
            tag = "oddrow" if i % 2 == 0 else "evenrow"
            self.tree.insert("", "end", tags=(tag,), values=(
                student["id"],
                student["name"],
                student['num_samples'],
                f"{student['quality_score']:.2f}" if student['quality_score'] else "N/A",
                student.get('created_date', 'N/A')
            ))

        # Configure row colors
        self.tree.tag_configure("oddrow", background="#f8f9fa")
        self.tree.tag_configure("evenrow", background="#ffffff")

        # Update statistics
        self.update_stats()

    def update_stats(self):
        """Cập nhật thống kê"""
        if not self.all_students:
            self.stats_label.config(text="Tổng: 0 | Avg Quality: 0.00")
            return

        total = len(self.all_students)
        avg_quality = sum(s.get('quality_score', 0)
                          for s in self.all_students) / total if total > 0 else 0

        self.stats_label.config(
            text=f"📊 Tổng: {total} | Avg Quality: {avg_quality:.2f}"
        )

    def filter_students(self):
        """Lọc danh sách theo từ khóa tìm kiếm"""
        search_text = self.search_entry.get().lower().strip()

        for item in self.tree.get_children():
            self.tree.delete(item)

        filtered = [s for s in self.all_students
                    if search_text in s["id"].lower() or search_text in s["name"].lower()]

        for i, student in enumerate(filtered):
            tag = "oddrow" if i % 2 == 0 else "evenrow"
            self.tree.insert("", "end", tags=(tag,), values=(
                student["id"],
                student["name"],
                student['num_samples'],
                f"{student['quality_score']:.2f}" if student['quality_score'] else "N/A",
                student.get('created_date', 'N/A')
            ))

        self.tree.tag_configure("oddrow", background="#f8f9fa")
        self.tree.tag_configure("evenrow", background="#ffffff")

    def export_csv(self):
        """Export danh sách nhân viên ra CSV"""
        if not self.all_students:
            messagebox.showwarning("Cảnh báo", "Không có dữ liệu để export!")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"danh_sach_nhan_vien_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )

        if not file_path:
            return

        try:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                # Header
                writer.writerow(
                    ['Mã NV', 'Họ tên', 'Số mẫu đăng ký', 'Quality Score', 'Ngày đăng ký'])
                # Data
                for student in self.all_students:
                    writer.writerow([
                        student["id"],
                        student["name"],
                        student['num_samples'],
                        f"{student['quality_score']:.2f}" if student['quality_score'] else "N/A",
                        student.get('created_date', 'N/A')
                    ])

            messagebox.showinfo(
                "Thành công", f"Đã export danh sách ra:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể export:\n{e}")

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                "Cảnh báo", "Vui lòng chọn một nhân viên để xóa!")
            return

        values = self.tree.item(selected[0])["values"]
        student_id = values[0]
        name = values[1]

        if messagebox.askyesno("🗑️ Xác nhận xóa",
                               f"Bạn có chắc muốn xóa nhân viên?\n\n"
                               f"Mã NV: {student_id}\n"
                               f"Họ tên: {name}"):
            if self.manager.delete_student(student_id):
                messagebox.showinfo(
                    "✅ Thành công", f"Đã xóa nhân viên: {name}")
                self.refresh_list()
                # Reload face_matcher nếu có
                if self.controller and hasattr(self.controller, 'face_matcher'):
                    self.controller.face_matcher.reload()
            else:
                messagebox.showerror("❌ Lỗi", "Không thể xóa nhân viên!")
