import csv
from openpyxl import Workbook
import os

class FileExporter:
    @staticmethod
    def export_csv(results, path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["ファイル名", "パターン", "件数", "位置"])

            for file, data in results.items():
                r = data["result"]
                name = os.path.basename(file)
                for p, c in r.counts.items():
                    pos = r.positions.get(p, [])
                    w.writerow([name, p, c, " ".join(map(str, pos))])

    @staticmethod
    def export_excel(results, path):
        wb = Workbook()
        ws = wb.active
        ws.append(["ファイル名", "パターン", "件数", "位置"])

        for file, data in results.items():
            r = data["result"]
            name = os.path.basename(file)
            for p, c in r.counts.items():
                pos = r.positions.get(p, [])
                ws.append([name, p, c, " ".join(map(str, pos))])

        wb.save(path)
