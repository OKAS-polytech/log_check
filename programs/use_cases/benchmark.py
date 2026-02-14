import time
import random
import string
from domain.interfaces.search_algorithm import SearchAlgorithm

class BenchmarkUseCase:
    def execute(self, algorithms: dict[str, SearchAlgorithm]):
        size = 1024 * 4
        test_text = ''.join(random.choices(string.ascii_letters + string.digits, k=size))

        results = {}

        for key, algo in algorithms.items():
            start = time.perf_counter()
            algo.search(test_text)
            end = time.perf_counter()

            elapsed = end - start
            results[key] = elapsed

        return results
