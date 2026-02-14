import tkinter as tk
import ttkbootstrap as tb
from core.exporter import ResultExporter
import os

class ResultWindow(tb.Toplevel):
    def __init__(self, master, results):
        super().__init__(master)
        self.results = results
        self.title("RESULT")
        self.geometry("1000x700")
        self.build()

    def build(self):
        btn = tb.Frame(self)
        btn.pack(fill="x")

        tb.Button(btn, text="CSV", command=lambda: ResultExporter.export_csv(self.results, self)).pack(side="left")
        tb.Button(btn, text="Excel", command=lambda: ResultExporter.export_excel(self.results, self)).pack(side="left")

        container = tb.Frame(self)
        container.pack(fill="both", expand=True)

        # 距離(distance) 列を追加
        self.tree = tb.Treeview(
            container,
            columns=("file", "pattern", "count", "pos", "distance"),
            show="headings"
        )
        self.tree.pack(fill="both", expand=True)

        # ヘッダ
        self.tree.heading("file", text="ファイル名")
        self.tree.heading("pattern", text="パターン")
        self.tree.heading("count", text="件数")
        self.tree.heading("pos", text="位置")
        self.tree.heading("distance", text="距離")

        # データ挿入
        for file, data in self.results.items():
            r = data["result"]
            name = os.path.basename(file)

            for p, c in r.counts.items():
                pos = r.positions.get(p, [])

                # Bitap の場合のみ距離が存在する
                dist = r.distances.get(p, None) if hasattr(r, "distances") else None

                # Treeview に 5 列分の値を渡す
                self.tree.insert(
                    "",
                    "end",
                    values=(name, p, c, pos, dist)
                )
