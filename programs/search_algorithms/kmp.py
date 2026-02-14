# search_algorithms/kmp.py

from .base import SearchAlgorithm, SearchResult

class KMPSearch(SearchAlgorithm):
    def __init__(self, pattern):
        super().__init__(pattern)
        self.name = "Knuth–Morris–Pratt (KMP)"
        self.lps = self.build_lps(pattern)
    
    def get_description(self):
        return ( "KMPアルゴリズムは部分一致テーブル（LPS）を使い、無駄な比較を避けながら線形時間で検索を行います。パターンが繰り返し構造を持つ場合に特に効率的です。^^" )

    def build_lps(self, pattern):
        lps = [0] * len(pattern)
        length = 0
        i = 1

        while i < len(pattern):
            if pattern[i] == pattern[length]:
                length += 1
                lps[i] = length
                i += 1
            else:
                if length != 0:
                    length = lps[length - 1]
                else:
                    lps[i] = 0
                    i += 1
        return lps

    def search(self, text: str) -> SearchResult:
        positions = []
        i = j = 0
        n = len(text)
        m = len(self.pattern)

        while i < n:
            if self.pattern[j] == text[i]:
                i += 1
                j += 1
            if j == m:
                positions.append(i - j)
                j = self.lps[j - 1]
            elif i < n and self.pattern[j] != text[i]:
                if j != 0:
                    j = self.lps[j - 1]
                else:
                    i += 1

        return SearchResult(
            {self.pattern: len(positions)},
            {self.pattern: positions}
        )
