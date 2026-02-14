# programs/domain/models/search_result.py

class SearchResult:
    def __init__(self, counts: dict[str, int], positions: dict[str, list[int]], distances: dict[str, list[int]] = None):
        self.counts = counts            # {pattern: count}
        self.positions = positions      # {pattern: [pos1, pos2, ...]}
        self.distances = distances or {} # {pattern: [dist1, dist2, ...]}

    def get_count(self, pattern: str) -> int:
        return self.counts.get(pattern, 0)

    def get_positions(self, pattern: str) -> list[int]:
        return self.positions.get(pattern, [])

    def get_distances(self, pattern: str) -> list[int]:
        return self.distances.get(pattern, [])
