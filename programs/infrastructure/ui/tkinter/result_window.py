import tkinter as tk
import ttkbootstrap as tb
import os
from infrastructure.external.file_exporter import FileExporter
from tkinter import filedialog, messagebox

class ResultWindow(tb.Toplevel):
    def __init__(self, master, results):
        super().__init__(master)
        self.results = results
        self.title("RESULT")
        self.geometry("1000x700")
        self.build()

    def build(self):
        btn_frame = tb.Frame(self)
        btn_frame.pack(fill="x")

        tb.Button(btn_frame, text="CSV", command=self.export_csv).pack(side="left")
        tb.Button(btn_frame, text="Excel", command=self.export_excel).pack(side="left")

        container = tb.Frame(self)
        container.pack(fill="both", expand=True)

        self.tree = tb.Treeview(
            container,
            columns=("file", "pattern", "count", "pos", "distance"),
            show="headings"
        )
        self.tree.pack(fill="both", expand=True)

        self.tree.heading("file", text="ファイル名")
        self.tree.heading("pattern", text="パターン")
        self.tree.heading("count", text="件数")
        self.tree.heading("pos", text="位置")
        self.tree.heading("distance", text="距離")

        for file, data in self.results.items():
            r = data["result"]
            name = os.path.basename(file)

            for p, c in r.counts.items():
                pos = r.positions.get(p, [])
                dist = r.distances.get(p, None)

                self.tree.insert(
                    "",
                    "end",
                    values=(name, p, c, pos, dist)
                )

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if path:
            FileExporter.export_csv(self.results, path)
            messagebox.showinfo("完了", "CSV にエクスポートしました", parent=self)

    def export_excel(self):
        path = filedialog.asksaveasfilename(defaultextension=".xlsx")
        if path:
            FileExporter.export_excel(self.results, path)
            messagebox.showinfo("完了", "Excel にエクスポートしました", parent=self)
