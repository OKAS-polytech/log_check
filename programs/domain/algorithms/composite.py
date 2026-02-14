from domain.interfaces.search_algorithm import SearchAlgorithm
from domain.models.search_result import SearchResult

class CompositeSearchAlgorithm(SearchAlgorithm):
    def __init__(self, searchers: list[SearchAlgorithm], name="Composite"):
        super().__init__("")
        self.searchers = searchers
        self.name = name

    def search(self, text: str) -> SearchResult:
        counts = {}
        positions = {}
        distances = {}

        for s in self.searchers:
            r = s.search(text)
            counts.update(r.counts)
            positions.update(r.positions)
            distances.update(r.distances)

        return SearchResult(counts, positions, distances)

    def get_description(self) -> str:
        if self.searchers:
            return self.searchers[0].get_description()
        return ""

    def search_chunk(self, text: str, offset: int = 0) -> SearchResult:
        counts = {}
        positions = {}
        distances = {}

        for s in self.searchers:
            r = s.search_chunk(text, offset)
            counts.update(r.counts)
            positions.update(r.positions)
            distances.update(r.distances)

        return SearchResult(counts, positions, distances)
