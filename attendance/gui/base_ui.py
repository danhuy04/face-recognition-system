import tkinter as tk

class BaseFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white") 
        self.controller = controller
        self.pack(fill="both", expand=True) 

    def show(self):
        self.lift()