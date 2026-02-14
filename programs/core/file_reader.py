import os
from docx import Document

class FileReader:
    @staticmethod
    def read_docx(path: str) -> str:
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)

    @staticmethod
    def read_any(path: str) -> str:
        ext = os.path.splitext(path)[1].lower()
        try:
            if ext == ".docx":
                return FileReader.read_docx(path)

            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

        except Exception as e:
            raise RuntimeError(f"{path} の読み込みに失敗しました: {e}")
