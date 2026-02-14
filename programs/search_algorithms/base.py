# search_algorithms/base.py
# 文字列探索アルゴリズムの抽象クラス

from abc import ABC, abstractmethod

class SearchResult:
    def __init__(self, counts: dict[str, int], positions: dict[str, list[int]], distances=None):
        self.counts = counts            # {pattern: count}
        self.positions = positions      # {pattern: [pos1, pos2, ...]}
        self.distances = distances or {}

    def get(self, pattern: str) -> int:
        return self.counts.get(pattern, 0)

    def get_positions(self, pattern: str) -> list[int]:
        return self.positions.get(pattern, [])

class SearchAlgorithm(ABC):
    def __init__(self, pattern):
        self.pattern = pattern
        self.name = "Unknown Algorithm"

    @abstractmethod
    def search(self, text) -> SearchResult:
        pass

    @abstractmethod
    def get_description(self) -> str:
        """アルゴリズムの説明文を返す"""
        pass

    def search_chunk(self, text: str, offset: int = 0) -> SearchResult:
        """
        デフォルトは search() を呼ぶだけ（BM/KMP 用）
        """
        r = self.search(text)
        # 位置に offset を足す
        new_positions = {
            p: [pos + offset for pos in pos_list]
            for p, pos_list in r.positions.items()
        }
        return SearchResult(r.counts, new_positions)

