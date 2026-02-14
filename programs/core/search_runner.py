import os
import time
from core.file_reader import FileReader

class SearchRunner:
    LARGE_FILE_THRESHOLD = 50 * 1024 * 1024

    def __init__(self, strategy):
        self.strategy = strategy

    def run_for_file(self, path):
        size = os.path.getsize(path)
        start = time.perf_counter()

        if size > self.LARGE_FILE_THRESHOLD:
            result = self.strategy.search_stream(path)
        else:
            text = FileReader.read_any(path)
            result = self.strategy.search(text)

        end = time.perf_counter()

        return {
            "result": result,
            "time": (end - start) * 1000,
            "size": size
        }
