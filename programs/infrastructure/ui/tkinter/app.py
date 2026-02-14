import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES
import csv
import os
import threading

from .result_window import ResultWindow
from .progress_window import ProgressWindow

class SearchApp(TkinterDnD.Tk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.file_paths = []
        self.search_entries = []
        self.algorithm = tk.StringVar(value="bm")
        self.title("String Search App (Refactored)")
        self.geometry("900x750")
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

        self.algo_recommend_labels = {}
        algos = [
            ("naive", "Naive（総当たり。マジで非推奨。勉強用。）"),
            ("bm", "Boyer-Moore"),
            ("kmp", "KMP"),
            ("ac", "Aho–Corasick"),
            ("bitap", "Bitap（Fuzzy!）")
        ]
        for key, text in algos:
            f = ttk.Frame(frame)
            f.pack(anchor="w")
            rb = ttk.Radiobutton(f, text=text, variable=self.algorithm, value=key, command=self.update_estimate)
            rb.pack(side="left")
            l = tk.Label(f, text="", fg="red")
            l.pack(side="left", padx=5)
            self.algo_recommend_labels[key] = l

        ttk.Button(frame, text="Info", command=self.show_algorithm_info).pack(anchor="e", padx=10, pady=5)

        # Bitap Distance
        self.bitap_distance = tk.IntVar(value=2)
        distance_frame = ttk.Frame(self)
        distance_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(distance_frame, text="レーベンシュタイン距離 (Bitapのみ):").pack(side="left")
        ttk.Entry(distance_frame, textvariable=self.bitap_distance, width=5).pack(side="left", padx=5)

        # Search Words
        word_frame_outer = ttk.LabelFrame(self, text="検索ワード")
        word_frame_outer.pack(fill="x", padx=10, pady=10)

        ttk.Button(word_frame_outer, text="検索ワードを CSV から読み込み", command=self.load_words_from_csv).pack(pady=5)

        self.word_canvas = tk.Canvas(word_frame_outer, height=150)
        self.word_canvas.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(word_frame_outer, orient="vertical", command=self.word_canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.word_canvas.configure(yscrollcommand=scrollbar.set)

        self.word_frame = ttk.Frame(self.word_canvas)
        inner = self.word_canvas.create_window((0, 0), window=self.word_frame, anchor="nw")

        def update_scroll(event):
            self.word_canvas.configure(scrollregion=self.word_canvas.bbox("all"))
        self.word_frame.bind("<Configure>", update_scroll)

        def resize(event):
            self.word_canvas.itemconfig(inner, width=event.width)
        self.word_canvas.bind("<Configure>", resize)

        self.add_entry()

        ttk.Button(word_frame_outer, text="検索ワード追加", command=self.add_entry).pack(pady=5)

        # Bottom controls
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill="x", side="bottom", padx=10, pady=10)

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

        self.progress_window = ProgressWindow(self, self.file_paths)
        self.search_button.config(state="disabled")

        def task():
            try:
                results = self.controller.run_search(
                    self.file_paths,
                    self.algorithm.get(),
                    patterns,
                    self.bitap_distance.get(),
                    progress_callback=self.handle_progress
                )
                self.after(0, lambda: self.finish_search(results))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("エラー", f"検索中にエラーが発生しました: {e}"))
                self.after(0, self.reset_ui)

        threading.Thread(target=task, daemon=True).start()

    def handle_progress(self, file_path, global_current, global_total, file_current, file_total):
        self.after(0, lambda: self.progress_window.update_file_progress(file_path, file_current, file_total))
        self.after(0, lambda: self.progress_window.update_overall_progress(global_current, global_total))

    def finish_search(self, results):
        self.reset_ui()
        if hasattr(self, 'progress_window'):
            self.progress_window.destroy()
        ResultWindow(self, results)

    def reset_ui(self):
        self.search_button.config(state="normal")

    def update_estimate(self, *args):
        patterns = [e.get().strip() for e in self.search_entries if e.get().strip()]

        estimate_str = self.controller.estimate_time(
            self.file_paths,
            self.algorithm.get(),
            patterns,
            self.bitap_distance.get()
        )

        total_size = sum(os.path.getsize(p) for p in self.file_paths) if self.file_paths else 0
        total_mb = total_size / (1024 * 1024)
        count = len(self.file_paths)

        file_info = f"{count} 件のファイルを選択中（計：{total_mb:.2f} MB）"
        if not self.file_paths:
            self.drop_label.config(text=f"{file_info} ファイル未選択")
        else:
            self.drop_label.config(text=f"{file_info} {estimate_str}")

        self.update_recommendations(patterns)

    def update_recommendations(self, patterns):
        if not self.file_paths or not patterns:
            for l in self.algo_recommend_labels.values():
                l.config(text="")
            return

        estimates = self.controller.get_all_estimates(self.file_paths, patterns, self.bitap_distance.get())

        best_algo = None
        min_time = float('inf')

        for key, val in estimates.items():
            if val is not None and val < min_time:
                min_time = val
                best_algo = key

        for key, label in self.algo_recommend_labels.items():
            if key == best_algo:
                label.config(text="（推奨！）")
            else:
                label.config(text="")
