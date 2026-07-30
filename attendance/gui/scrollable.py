import tkinter as tk
from tkinter import ttk

def create_scrollable_page(
    parent,
    title_text,
    header_bg="#2c3e50",
    content_bg="#f5f5f5"
):

    # ========= HEADER =========
    header = tk.Frame(parent, bg=header_bg, height=80)
    header.pack(fill="x", side="top")
    header.pack_propagate(False)

    tk.Label(
        header,
        text=title_text,
        font=("Arial", 20, "bold"),
        bg=header_bg,
        fg="white"
    ).pack(expand=True)

    # ========= SCROLLABLE CONTAINER =========
    container = tk.Frame(parent)
    container.pack(fill="both", expand=True, padx=20, pady=20)

    canvas = tk.Canvas(container, bg=content_bg, highlightthickness=0)
    scrollbar = ttk.Scrollbar(
        container, orient="vertical", command=canvas.yview)

    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # ========= CONTENT =========
    content = tk.Frame(canvas, bg=content_bg)
    canvas_window = canvas.create_window(
        (0, 0), window=content, anchor="nw")

    # Update scrollregion
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    content.bind("<Configure>", on_frame_configure)

    # Keep content width same as canvas
    def on_canvas_configure(event):
        canvas.itemconfig(canvas_window, width=event.width)

    canvas.bind("<Configure>", on_canvas_configure)

    # Mousewheel
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _bind_mousewheel(event):
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def _unbind_mousewheel(event):
        canvas.unbind_all("<MouseWheel>")

    canvas.bind("<Enter>", _bind_mousewheel)
    canvas.bind("<Leave>", _unbind_mousewheel)

    return content
