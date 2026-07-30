from dataclasses import dataclass
from typing import Optional

@dataclass
class Session:
    id: Optional[int]
    course: str
    start_time: str
    end_time: Optional[str] = None


@dataclass
class Attendance:
    session_id: int
    student_id: str
    time: str
    status: str = "Present"
