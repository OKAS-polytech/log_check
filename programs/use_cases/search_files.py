import time
from domain.interfaces.file_repository import FileRepository
from domain.interfaces.search_algorithm import SearchAlgorithm
from domain.models.search_result import SearchResult

class SearchFilesUseCase:
    LARGE_FILE_THRESHOLD = 50 * 1024 * 1024

    def __init__(self, file_repo: FileRepository):
        self.file_repo = file_repo

    def execute(self, file_path: str, algorithm: SearchAlgorithm, progress_callback=None):
        size = self.file_repo.get_size(file_path)
        start = time.perf_counter()

        if size > self.LARGE_FILE_THRESHOLD:
            result = self._search_stream(file_path, algorithm, progress_callback=progress_callback)
        else:
            if progress_callback:
                progress_callback(0, size)
            text = self.file_repo.read_text(file_path)
            result = algorithm.search(text)
            if progress_callback:
                progress_callback(size, size)

        end = time.perf_counter()

        return {
            "result": result,
            "time": (end - start) * 1000,
            "size": size
        }

    def _search_stream(self, path, algorithm, chunk_size=1024*1024, progress_callback=None):
        size = self.file_repo.get_size(path)
        offset = 0
        counts = {}
        positions = {}
        distances = {}

        if progress_callback:
            progress_callback(0, size)

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
            if progress_callback:
                progress_callback(offset, size)

        return SearchResult(counts, positions, distances)
