import csv
from openpyxl import Workbook
from tkinter import filedialog, messagebox
import os

class ResultExporter:
    @staticmethod
    def export_csv(results, parent):
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if not path:
            return

        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["ファイル名", "パターン", "件数", "位置"])

            for file, data in results.items():
                r = data["result"]
                name = os.path.basename(file)
                for p, c in r.counts.items():
                    pos = r.positions[p]
                    w.writerow([name, p, c, " ".join(map(str, pos))])

        messagebox.showinfo("完了", "CSV にエクスポートしました", parent=parent)

    @staticmethod
    def export_excel(results, parent):
        path = filedialog.asksaveasfilename(defaultextension=".xlsx")
        if not path:
            return

        wb = Workbook()
        ws = wb.active
        ws.append(["ファイル名", "パターン", "件数", "位置"])

        for file, data in results.items():
            r = data["result"]
            name = os.path.basename(file)
            for p, c in r.counts.items():
                pos = r.positions[p]
                ws.append([name, p, c, " ".join(map(str, pos))])

        wb.save(path)
        messagebox.showinfo("完了", "Excel にエクスポートしました", parent=parent)
