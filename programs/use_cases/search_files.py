import time
from domain.interfaces.file_repository import FileRepository
from domain.interfaces.search_algorithm import SearchAlgorithm
from domain.models.search_result import SearchResult

class SearchFilesUseCase:
    LARGE_FILE_THRESHOLD = 50 * 1024 * 1024

    def __init__(self, file_repo: FileRepository):
        self.file_repo = file_repo

    def execute(self, file_path: str, algorithm: SearchAlgorithm):
        size = self.file_repo.get_size(file_path)
        start = time.perf_counter()

        if size > self.LARGE_FILE_THRESHOLD:
            result = self._search_stream(file_path, algorithm)
        else:
            text = self.file_repo.read_text(file_path)
            result = algorithm.search(text)

        end = time.perf_counter()

        return {
            "result": result,
            "time": (end - start) * 1000,
            "size": size
        }

    def _search_stream(self, path, algorithm, chunk_size=1024*1024):
        offset = 0
        counts = {}
        positions = {}
        distances = {}

        for chunk in self.file_repo.read_chunks(path, chunk_size):
            r = algorithm.search_chunk(chunk, offset)

            for p, c in r.counts.items():
                counts[p] = counts.get(p, 0) + c
            for p, pos in r.positions.items():
                if p not in positions: positions[p] = []
                positions[p].extend(pos)
            for p, dist in r.distances.items():
                if p not in distances: distances[p] = []
                distances[p].extend(dist)

            offset += len(chunk)

        return SearchResult(counts, positions, distances)
