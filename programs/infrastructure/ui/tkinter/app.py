import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES
import csv
import os
import threading

from .result_window import ResultWindow

class SearchApp(TkinterDnD.Tk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.file_paths = []
        self.search_entries = []
        self.algorithm = tk.StringVar(value="bm")
        self.title("String Search App (Refactored)")
        self.geometry("900x800")
        self.build()
        self.after(0, self.run_benchmark)

    def run_benchmark(self):
        print("ベンチマーク中...（1〜2秒）")
        results = self.controller.run_benchmark()
        print("ベンチマーク完了:", results)
        self.update_estimate()

    def build(self):
        # File Drop Area
        drop_frame = ttk.Frame(self, height=60)
        drop_frame.pack(fill="x", padx=10, pady=10)
        drop_frame.pack_propagate(False)

        self.drop_label = ttk.Label(
            drop_frame,
            text="ここにファイルをドラッグ＆ドロップ",
            anchor="center",
            relief="ridge",
            padding=20
        )
        self.drop_label.pack(fill="both", expand=True)
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind("<<Drop>>", self.on_drop)

        # Algorithm Selection
        frame = ttk.LabelFrame(self, text="検索アルゴリズム")
        frame.pack(fill="x", padx=10, pady=5)

        ttk.Radiobutton(frame, text="Naive（総当たり。マジで非推奨。勉強用。）", variable=self.algorithm, value="naive", command=self.update_estimate).pack(anchor="w")
        ttk.Radiobutton(frame, text="Boyer-Moore", variable=self.algorithm, value="bm", command=self.update_estimate).pack(anchor="w")
        ttk.Radiobutton(frame, text="KMP", variable=self.algorithm, value="kmp", command=self.update_estimate).pack(anchor="w")
        ttk.Radiobutton(frame, text="Aho–Corasick", variable=self.algorithm, value="ac", command=self.update_estimate).pack(anchor="w")
        ttk.Radiobutton(frame, text="Bitap（Fuzzy!）", variable=self.algorithm, value="bitap", command=self.update_estimate).pack(anchor="w")

        ttk.Button(frame, text="Info", command=self.show_algorithm_info).pack(anchor="e", padx=10, pady=5)

        # Bitap Distance
        self.bitap_distance = tk.IntVar(value=2)
        distance_frame = ttk.Frame(self)
        distance_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(distance_frame, text="レーベンシュタイン距離 (Bitapのみ):").pack(side="left")
        ttk.Entry(distance_frame, textvariable=self.bitap_distance, width=5).pack(side="left", padx=5)

        # Search Words
        word_frame_outer = ttk.LabelFrame(self, text="検索ワード")
        word_frame_outer.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Button(self, text="検索ワードを CSV から読み込み", command=self.load_words_from_csv).pack(pady=5)

        canvas = tk.Canvas(word_frame_outer)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(word_frame_outer, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.word_frame = ttk.Frame(canvas)
        inner = canvas.create_window((0, 0), window=self.word_frame, anchor="nw")

        def update_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        self.word_frame.bind("<Configure>", update_scroll)

        def resize(event):
            canvas.itemconfig(inner, width=event.width)
        canvas.bind("<Configure>", resize)

        self.add_entry()

        ttk.Button(self, text="検索ワード追加", command=self.add_entry).pack(pady=5)

        # Bottom controls
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill="x", side="bottom", padx=10, pady=10)

        self.progress_bar = ttk.Progressbar(bottom_frame, orient="horizontal", length=100, mode="determinate")
        # Hidden initially by not packing yet or packing with 0 height

        self.search_button = ttk.Button(bottom_frame, text="検索実行", command=self.run_search)
        self.search_button.pack(pady=5)

    def show_algorithm_info(self):
        algo_key = self.algorithm.get()
        name, desc = self.controller.get_algorithm_info(algo_key)

        win = tk.Toplevel(self)
        win.title(f"Algorithm Info - {name}")
        win.geometry("400x250")

        ttk.Label(win, text=name, font=("Arial", 14, "bold")).pack(pady=10)
        ttk.Label(win, text=desc, wraplength=360, justify="left").pack(padx=10)

    def load_words_from_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return

        for entry in self.search_entries:
            entry.destroy()
        self.search_entries.clear()

        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if not row: continue
                word = row[0].strip()
                if word:
                    self.add_entry(word)

    def on_drop(self, event):
        paths = self.splitlist(event.data)
        self.file_paths = [p.strip("{}") for p in paths]
        self.update_estimate()

    def add_entry(self, word=""):
        e = ttk.Entry(self.word_frame)
        if word:
            e.insert(0, word)
        e.pack(fill="x", padx=5, pady=3)
        e.bind("<KeyRelease>", lambda ev: self.update_estimate())
        self.search_entries.append(e)

    def run_search(self):
        if not self.file_paths:
            messagebox.showerror("エラー", "ファイルを選択してください")
            return

        patterns = [e.get().strip() for e in self.search_entries if e.get().strip()]
        if not patterns:
            messagebox.showerror("エラー", "検索ワードを入力してください")
            return

        self.progress_bar.pack(fill="x", side="top", pady=5)
        self.progress_bar["value"] = 0
        self.search_button.config(state="disabled")

        def task():
            try:
                results = self.controller.run_search(
                    self.file_paths,
                    self.algorithm.get(),
                    patterns,
                    self.bitap_distance.get(),
                    progress_callback=self.update_progress
                )
                self.after(0, lambda: self.finish_search(results))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("エラー", f"検索中にエラーが発生しました: {e}"))
                self.after(0, self.reset_ui)

        threading.Thread(target=task, daemon=True).start()

    def update_progress(self, current, total):
        progress = (current / total) * 100
        self.after(0, lambda: self.progress_bar.configure(value=progress))

    def finish_search(self, results):
        self.reset_ui()
        ResultWindow(self, results)

    def reset_ui(self):
        self.progress_bar.pack_forget()
        self.search_button.config(state="normal")

    def update_estimate(self, *args):
        if not self.file_paths:
            file_info = "0 件のファイルを選択中（計：0.00 MB）"
            self.drop_label.config(text=f"{file_info} ファイル未選択")
            return

        patterns = [e.get().strip() for e in self.search_entries if e.get().strip()]
        estimate = self.controller.estimate_time(
            self.file_paths,
            self.algorithm.get(),
            patterns,
            self.bitap_distance.get()
        )

        total_size = sum(os.path.getsize(p) for p in self.file_paths)
        total_mb = total_size / (1024 * 1024)
        count = len(self.file_paths)

        file_info = f"{count} 件のファイルを選択中（計：{total_mb:.2f} MB）"
        self.drop_label.config(text=f"{file_info} {estimate}")
