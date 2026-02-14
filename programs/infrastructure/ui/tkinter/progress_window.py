import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb

class ProgressWindow(tb.Toplevel):
    def __init__(self, master, file_paths):
        super().__init__(master)
        self.title("検索進行状況")
        self.geometry("600x400")
        self.file_paths = file_paths
        self.progress_vars = {}
        self.labels = {}
        self.build()

    def build(self):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="検索実行中...", font=("Arial", 12, "bold")).pack(pady=10)

        self.overall_progress = ttk.Progressbar(main_frame, orient="horizontal", mode="determinate")
        self.overall_progress.pack(fill="x", pady=5)
        self.overall_label = ttk.Label(main_frame, text="全体の進捗: 0%")
        self.overall_label.pack()

        # Scrollable area for file list
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill="both", expand=True, pady=10)

        canvas = tk.Canvas(canvas_frame)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.scroll_frame = ttk.Frame(canvas)
        inner = canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        def update_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        self.scroll_frame.bind("<Configure>", update_scroll)

        def resize(event):
            canvas.itemconfig(inner, width=event.width)
        canvas.bind("<Configure>", resize)

        for path in self.file_paths:
            f = ttk.Frame(self.scroll_frame)
            f.pack(fill="x", pady=2)

            name = path.split("/")[-1]
            l = ttk.Label(f, text=f"{name}: 待機中", width=40)
            l.pack(side="left")

            p = ttk.Progressbar(f, orient="horizontal", length=150, mode="determinate")
            p.pack(side="right", padx=5)

            self.progress_vars[path] = p
            self.labels[path] = l

    def update_file_progress(self, path, current, total):
        if path in self.progress_vars:
            progress = (current / total) * 100 if total > 0 else 100
            self.progress_vars[path]["value"] = progress
            name = path.split("/")[-1]
            self.labels[path].config(text=f"{name}: {progress:.1f}%")

    def update_overall_progress(self, current, total):
        progress = (current / total) * 100 if total > 0 else 100
        self.overall_progress["value"] = progress
        self.overall_label.config(text=f"全体の進捗: {progress:.1f}%")
