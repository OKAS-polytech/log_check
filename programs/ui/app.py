import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES

from core.strategies import NaiveStrategy, BoyerMooreStrategy, KMPSearchStrategy, AhoCorasickStrategy, BitapStrategy
from core.search_runner import SearchRunner
from ui.result_window import ResultWindow

from search_algorithms.boyer_moore import BoyerMooreSearch
from search_algorithms.kmp import KMPSearch
from search_algorithms.aho_corasick_multi import AhoCorasickMulti
from search_algorithms.bitap import BitapSearch
from search_algorithms.naive import NaiveSearch

import csv
import os


class SearchApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.comparisons_per_second = self.measure_comparisons_per_second() # ベンチマーク測定用だよ^^
        self.file_paths = []
        self.search_entries = []
        self.algorithm = tk.StringVar(value="bm")
        self.title("String Search App")
        self.geometry("900x700")
        self.build()
        self.benchmark_coeff = {
            "naive": 1.0,
            "bm": 1.0,
            "kmp": 1.0,
            "ac": 1.0,
            "bitap": 1.0,
        }
        self.after(0, self.benchmark_algorithms)


    def build(self):
        # -------------------------
        # ファイルドロップ領域
        # -------------------------
        drop_frame = ttk.Frame(self, height=60)
        drop_frame.pack(fill="x", padx=10, pady=10)

        drop_frame.pack_propagate(False)  # 高さ固定

        self.drop_label = ttk.Label(
            drop_frame,
            text="ここにファイルをドラッグ＆ドロップ",
            anchor="center",
            relief="ridge",
            padding=20
        )
        self.drop_label.pack(fill="both", expand=True)

        # DnD 設定
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind("<<Drop>>", self.on_drop)


        # アルゴリズム選択
        frame = ttk.LabelFrame(self, text="検索アルゴリズム")
        frame.pack(fill="x", padx=10, pady=5)

        ttk.Radiobutton(frame, text="Naive（総当たり。マジで非推奨。勉強用。）", variable=self.algorithm, value="naive", command=self.update_estimate).pack(anchor="w")
        ttk.Radiobutton(frame, text="Boyer-Moore", variable=self.algorithm, value="bm", command=self.update_estimate).pack(anchor="w")
        ttk.Radiobutton(frame, text="KMP", variable=self.algorithm, value="kmp", command=self.update_estimate).pack(anchor="w")
        ttk.Radiobutton(frame, text="Aho–Corasick", variable=self.algorithm, value="ac", command=self.update_estimate).pack(anchor="w")
        ttk.Radiobutton(frame, text="Bitap（Fuzzy!）", variable=self.algorithm, value="bitap", command=self.update_estimate).pack(anchor="w")

        # Info ボタン（復元）
        ttk.Button(frame, text="Info", command=self.show_algorithm_info).pack(anchor="e", padx=10, pady=5)

        # 許容距離入力
        self.bitap_distance = tk.IntVar(value=2)

        distance_frame = ttk.Frame(self)
        distance_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(distance_frame, text="レーベンシュタイン距離 (何文字まで違ってもいいか、みたいな感じ。Bitap以外は指定しても無意味。):").pack(side="left")
        ttk.Entry(distance_frame, textvariable=self.bitap_distance, width=5).pack(side="left", padx=5)

        # 検索ワード
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
        ttk.Button(self, text="検索実行", command=self.run_search).pack(pady=10)

    # -------------------------
    # Info ボタン（復元）
    # -------------------------
    def show_algorithm_info(self):
        algo = self.algorithm.get()

        # アルゴリズムごとに説明を取得
        if algo == "bm":
            temp = BoyerMooreSearch("dummy")
        elif algo == "kmp":
            temp = KMPSearch("dummy")
        elif algo == "ac":
            temp = AhoCorasickMulti(["dummy"])
        elif algo == "bitap":
            temp = BitapSearch("dummy")
        else:
            temp = NaiveSearch("dummy")

        win = tk.Toplevel(self)
        win.title(f"Algorithm Info - {temp.name}")
        win.geometry("400x250")

        ttk.Label(win, text=temp.name, font=("Arial", 14, "bold")).pack(pady=10)
        ttk.Label(win, text=temp.get_description(), wraplength=360, justify="left").pack(padx=10)

    # -------------------------
    # CSV 読み込み
    # -------------------------
    def load_words_from_csv(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv")]
        )
        if not file_path:
            return

        for entry in self.search_entries:
            entry.destroy()
        self.search_entries.clear()

        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if not row:
                    continue
                word = row[0].strip()
                if word:
                    entry = ttk.Entry(self.word_frame)
                    entry.insert(0, word)
                    entry.pack(fill="x", padx=5, pady=3)
                    self.search_entries.append(entry)

    # -------------------------
    # その他 UI 操作
    # -------------------------
    def on_drop(self, event):
        paths = self.splitlist(event.data)
        self.file_paths = [p.strip("{}") for p in paths]

        total_size = sum(os.path.getsize(p) for p in self.file_paths)
        total_mb = total_size / (1024 * 1024)
        count = len(self.file_paths)

        estimate = self.estimate_worst_time()

        self.drop_label.config(
            text=f"{count} 件のファイルを選択中（計：{total_mb:.2f} MB）{estimate}"
        )


    def add_entry(self):
        e = ttk.Entry(self.word_frame)
        e.pack(fill="x", padx=5, pady=3)
        e.bind("<KeyRelease>", lambda ev: self.update_estimate())
        self.search_entries.append(e)

    # -------------------------
    # 検索実行
    # -------------------------
    def run_search(self):
        if not self.file_paths:
            messagebox.showerror("エラー", "ファイルを選択してください")
            return

        patterns = [e.get().strip() for e in self.search_entries if e.get().strip()]
        if not patterns:
            messagebox.showerror("エラー", "検索ワードを入力してください")
            return

        strategy = {
            "bm": BoyerMooreStrategy,
            "kmp": KMPSearchStrategy,
            "ac": AhoCorasickStrategy,
            "bitap": lambda patterns: BitapStrategy(patterns, max_distance=self.bitap_distance.get()),
            "naive": NaiveStrategy
        }[self.algorithm.get()](patterns)

        runner = SearchRunner(strategy)
        results = {path: runner.run_for_file(path) for path in self.file_paths}

        ResultWindow(self, results)
    
    def benchmark_algorithms(self):
        import time
        import random
        import string

        print("ベンチマーク中...（1〜2秒）")

        # 4kB のテストデータ
        size = 1024 * 4
        test_text = ''.join(random.choices(string.ascii_letters + string.digits, k=size))

        pattern = "benchmarkpattern"

        # Strategy クラスをマッピング
        strategy_map = {
            "naive": NaiveStrategy,
            "bm": BoyerMooreStrategy,
            "kmp": KMPSearchStrategy,
            "ac": AhoCorasickStrategy,
            "bitap": lambda pats: BitapStrategy(pats, max_distance=1)
        }

        results = {}

        for algo, strategy_cls in strategy_map.items():
            # Strategy インスタンス生成
            if algo == "bitap":
                strategy = strategy_cls([pattern])
            else:
                strategy = strategy_cls([pattern])

            start = time.perf_counter()
            strategy.search(test_text)
            end = time.perf_counter()

            elapsed = end - start
            results[algo] = elapsed

        self.benchmark_coeff = results
        print("ベンチマーク完了:", results)


    # -------------------------
    # 時間推定
    # -------------------------
    def estimate_worst_time(self):
        if not self.file_paths:
            return "ファイル未選択"

        total_size = sum(os.path.getsize(p) for p in self.file_paths)
        N_KB = total_size / 1024  # KB換算

        patterns = [e.get().strip() for e in self.search_entries if e.get().strip()]
        if not patterns:
            return ""

        algo = self.algorithm.get()
        num_patterns = len(patterns)

        # 実測係数（1KBあたりの秒数）
        coeff = self.benchmark_coeff.get(algo, 1.0)

        # パターン長補正
        avg_len = sum(len(p) for p in patterns) / num_patterns
        length_factor = max(1.0, avg_len / 16)

        # アルゴリズム別の複数パターン補正
        if algo == "naive":
            pattern_factor = num_patterns * (avg_len / 8)
        elif algo == "bm":
            pattern_factor = num_patterns * (avg_len / 12)
        elif algo == "kmp":
            pattern_factor = num_patterns * (avg_len / 20)
        elif algo == "bitap":
            d = max(1, self.bitap_distance.get())
            pattern_factor = num_patterns * (avg_len / 8) * (d / 2)
        else:  # AC
            pattern_factor = 1.0

        seconds = N_KB * coeff * length_factor * pattern_factor

        if seconds < 1e-3:
            return f"時間の目安：{seconds*1e6:.1f}マイクロ秒"
        elif seconds < 1:
            return f"時間の目安：{seconds*1000:.1f}ミリ秒"
        else:
            return f"時間の目安：{seconds:.2f}秒"

    def update_estimate(self, *args):
        estimate = self.estimate_worst_time()

        # 現在のラベルテキストを取得
        text = self.drop_label.cget("text")

        # ファイル情報部分だけを取り出す
        # → "最悪時間の目安：" 以降を削除
        if "時間の目安" in text:
            file_info = text.split("時間の目安")[0].strip()
        else:
            file_info = text.strip()

        # 新しい 1 行テキストをセット
        self.drop_label.config(
            text=f"{file_info} {estimate}"
        )

    def measure_comparisons_per_second(self):
        import time
        a = "a"
        b = "b"
        count = 10_000_000  # 1千万回

        start = time.perf_counter()
        for _ in range(count):
            _ = (a == b)
        end = time.perf_counter()

        elapsed = end - start
        cps = count / elapsed

        print(f"[Benchmark] {cps:,.0f} comparisons/sec (elapsed {elapsed:.3f}s)")
        return cps




