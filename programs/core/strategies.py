from search_algorithms.boyer_moore import BoyerMooreSearch
from search_algorithms.kmp import KMPSearch
from search_algorithms.aho_corasick_multi import AhoCorasickMulti
from search_algorithms.base import SearchResult
from core.utils import levenshtein
from search_algorithms.bitap import BitapSearch
from search_algorithms.naive import NaiveSearch

class BaseStrategy:
    def __init__(self, patterns):
        self.patterns = patterns

    def search(self, text: str) -> SearchResult:
        raise NotImplementedError

    def search_stream(self, path: str, chunk_size=1024*1024) -> SearchResult:
        raise NotImplementedError

class NaiveStrategy(BaseStrategy):
    def __init__(self, patterns):
        super().__init__(patterns)
        self.searchers = [NaiveSearch(p) for p in patterns]

    def search(self, text):
        counts = {}
        positions = {}

        for s in self.searchers:
            pos = s.search(text)
            counts[s.pattern] = len(pos)
            positions[s.pattern] = pos

        return SearchResult(counts, positions)

    def search_stream(self, path, chunk_size=1024*1024):
        counts = {p: 0 for p in self.patterns}
        positions = {p: [] for p in self.patterns}

        offset = 0

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break

                for s in self.searchers:
                    pos = s.search_chunk(chunk, offset)
                    counts[s.pattern] += len(pos)
                    positions[s.pattern].extend(pos)

                offset += len(chunk)

        return SearchResult(counts, positions)

class BitapStrategy(BaseStrategy):
    def __init__(self, patterns, max_distance=2):
        super().__init__(patterns)
        self.max_distance = max_distance
        self.searchers = [BitapSearch(p, max_distance) for p in patterns]

    def search(self, text):
        counts = {}
        positions = {}
        distances = {}

        for s in self.searchers:
            matches = s.search(text)

            counts[s.pattern] = len(matches)
            positions[s.pattern] = [pos for pos, _, _ in matches]
            distances[s.pattern] = [dist for _, _, dist in matches]

        return SearchResult(counts, positions, distances=distances)

    def search_stream(self, path, chunk_size=1024*1024):
        raise NotImplementedError("Bitapはストリーム非対応.")

class BoyerMooreStrategy(BaseStrategy):
    def __init__(self, patterns):
        super().__init__(patterns)
        self.searchers = [BoyerMooreSearch(p) for p in patterns]

    def search(self, text):
        counts = {}
        positions = {}
        for s in self.searchers:
            r = s.search(text)
            counts[s.pattern] = r.get(s.pattern)
            positions[s.pattern] = r.get_positions(s.pattern)
        return SearchResult(counts, positions)

    def search_stream(self, path, chunk_size=1024*1024):
        counts = {p: 0 for p in self.patterns}
        positions = {p: [] for p in self.patterns}
        offset = 0

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            while chunk := f.read(chunk_size):
                for s in self.searchers:
                    r = s.search_chunk(chunk, offset)
                    for p, c in r.counts.items():
                        counts[p] += c
                    for p, pos in r.positions.items():
                        positions[p].extend(pos)
                offset += len(chunk)

        return SearchResult(counts, positions)


class KMPSearchStrategy(BoyerMooreStrategy):
    def __init__(self, patterns):
        super().__init__(patterns)
        self.searchers = [KMPSearch(p) for p in patterns]


class AhoCorasickStrategy(BaseStrategy):
    def __init__(self, patterns):
        super().__init__(patterns)
        self.searcher = AhoCorasickMulti(patterns)

    def search(self, text):
        return self.searcher.search(text)

    def search_stream(self, path, chunk_size=1024*1024):
        counts = {p: 0 for p in self.patterns}
        positions = {p: [] for p in self.patterns}
        offset = 0

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            while chunk := f.read(chunk_size):
                r = self.searcher.search_chunk(chunk, offset)
                for p, c in r.counts.items():
                    counts[p] += c
                for p, pos in r.positions.items():
                    positions[p].extend(pos)
                offset += len(chunk)

        return SearchResult(counts, positions)
