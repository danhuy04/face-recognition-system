import tkinter as tk
from gui.enroll_ui import EnrollUI
from gui.attendance_ui import AttendanceUI
from gui.home_ui import HomeUI
from core.face_matcher import FaceMatcher   

class MainUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Face Attendance System")
        self.geometry("1100x600")
        self.resizable(True, True)
        self.minsize(900, 600)

        self.face_matcher = FaceMatcher() 

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames = {}

        for F in (HomeUI, EnrollUI, AttendanceUI):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame("HomeUI")

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()