import os
import pickle
import shutil
from tkinter import messagebox


class StudentManager:
    def __init__(self, db_path="database/embeddings.pkl", controller=None):
        self.db_path = db_path
        self.students = self._load_students()
        self.controller = controller

    def _load_students(self):
        """Hàm nội bộ load dữ liệu, có thể gọi lại khi cần"""
        if not os.path.exists(self.db_path):
            return []
        try:
            with open(self.db_path, "rb") as f:
                data = pickle.load(f)
            return data
        except Exception as e:
            print(f"Lỗi đọc embeddings.pkl: {e}")
            return []

    def reload(self):
        """Reload dữ liệu từ file"""
        self.students = self._load_students()
        return self.students

    def get_all_students(self):
        return self.students

    def get_student_by_id(self, student_id):
        for student in self.students:
            if student["id"] == student_id:
                return student
        return None

    def delete_student(self, student_id: str) -> bool:
        if not self.students:
            return False

        # Backup file cũ
        backup_path = self.db_path + ".backup"
        try:
            if os.path.exists(self.db_path):
                shutil.copy2(self.db_path, backup_path)
        except Exception as e:
            print(f"Không backup được: {e}")

        # Lọc bỏ nhân viên
        original_count = len(self.students)
        self.students = [s for s in self.students  if str(s["id"]) != str(student_id)]

        if len(self.students) == original_count:
            print("❌ Không tìm thấy nhân viên để xóa")
            return False
        
        # Ghi đè file
        try:
            with open(self.db_path, "wb") as f:
                pickle.dump(self.students, f, protocol=pickle.HIGHEST_PROTOCOL)
            self.reload()

            try:
                if self.controller and hasattr(self.controller, 'face_matcher'):
                    self.controller.face_matcher.reload()
                    print(f"Đã reload FaceMatcher sau khi xóa {student_id}")
            except Exception as e:
                print(
                    f"Không reload được FaceMatcher: {e} (sẽ reload khi restart)")

            return True

        except Exception as e:
            print(f"Lỗi ghi file khi xóa {student_id}: {e}")
            # Phục hồi từ backup nếu có
            if os.path.exists(backup_path):
                try:
                    shutil.copy2(backup_path, self.db_path)
                    print("Đã khôi phục từ backup")
                except:
                    pass
            return False
