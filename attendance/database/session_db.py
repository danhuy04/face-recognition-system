import sqlite3
from datetime import datetime, timedelta
import os


class SessionDB:
    def __init__(self, conn):
        self.conn = conn
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                status TEXT DEFAULT 'present'
            )
        """)
        self.conn.commit()

    def create_session(
        self,
        course: str,
        start_time: datetime | None = None,
        end_time: datetime | None = None
    ) -> int:
        if start_time is None:
            start_time = datetime.now()

        self.cursor.execute("""
            INSERT INTO sessions (course, start_time, end_time)
            VALUES (?, ?, ?)
        """, (
            course,
            start_time.isoformat(),
            end_time.isoformat() if end_time else None
        ))
        self.conn.commit()
        return self.cursor.lastrowid

    def _is_session_active(self, session_id: int) -> bool:
        self.cursor.execute("""
            SELECT start_time, end_time, status
            FROM sessions
            WHERE id = ?
        """, (int(session_id),))

        row = self.cursor.fetchone()
        print("DEBUG row:", dict(row))

        if not row:
            return False

        status = row["status"]
        if status != "present":
            print("DEBUG inactive status:", status)
            return False

        start = datetime.fromisoformat(row["start_time"])
        now = datetime.now()

        if row["end_time"]:
            end = datetime.fromisoformat(row["end_time"])
            return start <= now <= end

        return now >= start


    def close_session(self, session_id: int) -> bool:
        self.cursor.execute("""
            UPDATE sessions
            SET end_time = ?, status = 'closed'
            WHERE id = ?
        """, (datetime.now().isoformat(), session_id))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def session_exists(self, session_id: int) -> bool:
        self.cursor.execute(
            "SELECT 1 FROM sessions WHERE id = ?",
            (session_id,)
        )
        return self.cursor.fetchone() is not None

    def get_session(self, session_id: int) -> dict | None:
        self.cursor.execute("""
            SELECT id, course, start_time, end_time, status
            FROM sessions
            WHERE id = ?
        """, (session_id,))
        row = self.cursor.fetchone()
        if not row:
            return None

        return {
            "id": row[0],
            "course": row[1],
            "start_time": row[2],
            "end_time": row[3],
            "status": row[4]
        }

    def get_active_session(self) -> dict | None:
        self.cursor.execute("""
            SELECT id, course, start_time
            FROM sessions
            WHERE status = 'active'
            ORDER BY start_time DESC
            LIMIT 1
        """)
        row = self.cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "course": row[1],
                "start_time": row[2]
            }
        return None
    
    def get_recent_sessions(self, limit=30):
        """Lấy các session gần đây, ưu tiên chưa kết thúc"""
        self.cursor.execute("""
            SELECT id, course, start_time, end_time 
            FROM sessions 
            ORDER BY 
                CASE WHEN end_time IS NULL THEN 0 ELSE 1 END,  
                start_time DESC 
            LIMIT ?
        """, (limit,))
        return [
            {
                "id": row[0],
                "course": row[1],
                "start_time": row[2],
                "end_time": row[3]
            }
            for row in self.cursor.fetchall()
        ]
