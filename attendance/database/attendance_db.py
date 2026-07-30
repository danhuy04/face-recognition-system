from datetime import datetime
from database.session_db import SessionDB

class AttendanceDB:
    def __init__(self, conn):
        self.conn = conn
        self.cursor = self.conn.cursor()
        self.session_db = SessionDB(conn)
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                session_id TEXT,
                student_id TEXT,
                name TEXT,
                time TEXT,
                status TEXT,
                UNIQUE(session_id, student_id)
            )
        """)

        self.conn.commit()

    def mark_attendance(self, session_id: int, student_id: str, status="present") -> bool:
        if not self.session_db._is_session_active(session_id):
            print("⛔ Session chưa bắt đầu hoặc đã kết thúc")
            return False

        now = datetime.now().isoformat()
        try:
            self.cursor.execute("""
                INSERT OR IGNORE INTO attendance 
                (session_id, student_id, time, status)
                VALUES (?, ?, ?, ?)
            """, (session_id, student_id, now, status))
            self.conn.commit()
            return self.cursor.rowcount > 0 or self._attendance_exists(session_id, student_id)
        except Exception as e:
            print(f"DB error mark_attendance: {e}")
            return False

    def _attendance_exists(self, session_id: int, student_id: str) -> bool:
        self.cursor.execute("""
            SELECT 1 FROM attendance 
            WHERE session_id = ? AND student_id = ?
        """, (session_id, student_id))
        return self.cursor.fetchone() is not None
    
    def get_attendance_by_date(self, date_str: str):
        """Lấy điểm danh theo ngày (YYYY-MM-DD)"""
        self.cursor.execute("""
            SELECT 
                a.student_id, 
                a.time, 
                date(a.time) AS date_only,
                a.status,
                a.session_id
            FROM attendance a
            WHERE date(a.time) = ?
            ORDER BY a.time
        """, (date_str,))
        return self.cursor.fetchall()

    def get_all_attendance(self):
        """Lấy toàn bộ lịch sử điểm danh"""
        self.cursor.execute("""
            SELECT 
                a.student_id, 
                a.time, 
                date(a.time) AS date_only,
                a.status,
                a.session_id
            FROM attendance a
            ORDER BY a.time DESC
        """)
        return self.cursor.fetchall()

    def get_attendance_by_session(self, session_id: int):
        """Lấy theo session cụ thể """
        self.cursor.execute("""
            SELECT 
                a.student_id, 
                a.time, 
                date(a.time) AS date_only,
                a.status
            FROM attendance a
            WHERE a.session_id = ?
            ORDER BY a.time
        """, (session_id,))
        return self.cursor.fetchall()

    # Đóng kết nối khi cần 
    def close(self):
        self.conn.close()

