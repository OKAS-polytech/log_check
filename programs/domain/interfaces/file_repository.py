from abc import ABC, abstractmethod
from typing import Iterator

class FileRepository(ABC):
    @abstractmethod
    def read_text(self, path: str) -> str:
        pass

    @abstractmethod
    def get_size(self, path: str) -> int:
        pass

    @abstractmethod
    def read_chunks(self, path: str, chunk_size: int = 1024*1024) -> Iterator[str]:
        pass
