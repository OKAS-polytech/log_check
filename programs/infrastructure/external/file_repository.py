import os
from docx import Document
from domain.interfaces.file_repository import FileRepository
from typing import Iterator

class LocalFileRepository(FileRepository):
    def read_text(self, path: str) -> str:
        ext = os.path.splitext(path)[1].lower()
        if ext == ".docx":
            return self._read_docx(path)

        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            # latin-1 maps all 256 bytes to characters, ideal for binary string search
            with open(path, "r", encoding="latin-1") as f:
                return f.read()

    def _read_docx(self, path: str) -> str:
        try:
            doc = Document(path)
            return "\n".join(p.text for p in doc.paragraphs)
        except:
            return self.read_text(path)

    def get_size(self, path: str) -> int:
        return os.path.getsize(path)

    def read_chunks(self, path: str, chunk_size: int = 1024*1024) -> Iterator[str]:
        # Use latin-1 for streaming if it might be binary
        # For simplicity and robustness in binary search, we use latin-1
        # if utf-8 fails or if we want to ensure no bytes are skipped.

        encoding = "utf-8"
        try:
            with open(path, "rb") as f:
                f.read(1024).decode("utf-8")
        except UnicodeDecodeError:
            encoding = "latin-1"

        with open(path, "r", encoding=encoding, errors="ignore") as f:
            while chunk := f.read(chunk_size):
                yield chunk
