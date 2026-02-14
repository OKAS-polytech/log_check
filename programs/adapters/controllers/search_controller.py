from use_cases.search_files import SearchFilesUseCase
from use_cases.benchmark import BenchmarkUseCase
from use_cases.estimation import EstimationUseCase
from domain.algorithms.naive import NaiveSearch
from domain.algorithms.boyer_moore import BoyerMooreSearch
from domain.algorithms.kmp import KMPSearch
from domain.algorithms.aho_corasick import AhoCorasickSearch
from domain.algorithms.bitap import BitapSearch
from domain.algorithms.composite import CompositeSearchAlgorithm

class SearchController:
    def __init__(self, search_use_case: SearchFilesUseCase, benchmark_use_case: BenchmarkUseCase, estimation_use_case: EstimationUseCase):
        self.search_use_case = search_use_case
        self.benchmark_use_case = benchmark_use_case
        self.estimation_use_case = estimation_use_case
        self.benchmark_coeffs = {}

    def run_benchmark(self):
        algos = {
            "naive": NaiveSearch("benchmarkpattern"),
            "bm": BoyerMooreSearch("benchmarkpattern"),
            "kmp": KMPSearch("benchmarkpattern"),
            "ac": AhoCorasickSearch(["benchmarkpattern"]),
            "bitap": BitapSearch("benchmarkpattern", max_distance=1)
        }
        self.benchmark_coeffs = self.benchmark_use_case.execute(algos)
        return self.benchmark_coeffs

    def estimate_time(self, file_paths, algorithm_key, patterns, bitap_distance):
        return self.estimation_use_case.execute(file_paths, algorithm_key, patterns, self.benchmark_coeffs, bitap_distance)

    def run_search(self, file_paths, algorithm_key, patterns, bitap_distance, progress_callback=None):
        algorithm = self._get_algorithm(algorithm_key, patterns, bitap_distance)
        results = {}

        # Calculate total size for progress reporting
        total_size = sum(self.search_use_case.file_repo.get_size(path) for path in file_paths)
        processed_size = 0

        for path in file_paths:
            file_size = self.search_use_case.file_repo.get_size(path)

            def make_wrapped_callback(base_offset):
                return lambda current, total: progress_callback(base_offset + current, total_size) if progress_callback else None

            results[path] = self.search_use_case.execute(
                path,
                algorithm,
                progress_callback=make_wrapped_callback(processed_size)
            )
            processed_size += file_size

        return results

    def get_algorithm_info(self, algorithm_key):
        # Dummy algorithm instance to get info
        algo = self._get_algorithm(algorithm_key, ["dummy"], 2)
        return algo.name, algo.get_description()

    def _get_algorithm(self, algorithm_key, patterns, bitap_distance):
        if algorithm_key == "ac":
            return AhoCorasickSearch(patterns)

        if algorithm_key == "bitap":
            searchers = [BitapSearch(p, bitap_distance) for p in patterns]
            return CompositeSearchAlgorithm(searchers, "Bitap (Multi)")

        if algorithm_key == "naive":
            searchers = [NaiveSearch(p) for p in patterns]
            return CompositeSearchAlgorithm(searchers, "Naive (Multi)")

        if algorithm_key == "bm":
            searchers = [BoyerMooreSearch(p) for p in patterns]
            return CompositeSearchAlgorithm(searchers, "Boyer-Moore (Multi)")

        if algorithm_key == "kmp":
            searchers = [KMPSearch(p) for p in patterns]
            return CompositeSearchAlgorithm(searchers, "KMP (Multi)")

        raise ValueError(f"Unknown algorithm: {algorithm_key}")
