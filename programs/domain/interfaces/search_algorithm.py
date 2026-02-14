from abc import ABC, abstractmethod
from domain.models.search_result import SearchResult

class SearchAlgorithm(ABC):
    def __init__(self, pattern: str = ""):
        self.pattern = pattern
        self.name = "Unknown Algorithm"

    @abstractmethod
    def search(self, text: str) -> SearchResult:
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Returns the description of the algorithm."""
        pass

    def search_chunk(self, text: str, offset: int = 0) -> SearchResult:
        """Default implementation for chunk-based searching."""
        r = self.search(text)
        new_positions = {
            p: [pos + offset for pos in pos_list]
            for p, pos_list in r.positions.items()
        }
        return SearchResult(r.counts, new_positions, getattr(r, 'distances', {}))
