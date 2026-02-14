import os
from docx import Document
from domain.interfaces.file_repository import FileRepository
from typing import Iterator

class LocalFileRepository(FileRepository):
    def read_text(self, path: str) -> str:
        ext = os.path.splitext(path)[1].lower()
        if ext == ".docx":
            return self._read_docx(path)

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    def _read_docx(self, path: str) -> str:
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)

    def get_size(self, path: str) -> int:
        return os.path.getsize(path)

    def read_chunks(self, path: str, chunk_size: int = 1024*1024) -> Iterator[str]:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            while chunk := f.read(chunk_size):
                yield chunk
