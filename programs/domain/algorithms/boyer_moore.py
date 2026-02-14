from domain.interfaces.search_algorithm import SearchAlgorithm
from domain.models.search_result import SearchResult

class BoyerMooreSearch(SearchAlgorithm):
    def __init__(self, pattern: str):
        super().__init__(pattern)
        self.name = "Boyer–Moore"
        self.bad_char = self.build_bad_char_table(pattern)
    
    def get_description(self):
        return ( "Boyer–Mooreアルゴリズムは高速な文字列探索手法で、後方から比較し、Bad-Character/Good-Suffixルールにより大きくスキップします。長いテキストに対して非常に効率的です。^^" )

    def build_bad_char_table(self, pattern):
        table = {}
        for i, c in enumerate(pattern):
            table[c] = i
        return table

    def search(self, text: str) -> SearchResult:
        positions = []
        m = len(self.pattern)
        n = len(text)

        if m == 0:
            return SearchResult({"": 0}, {"": []})

        i = 0
        while i <= n - m:
            j = m - 1
            while j >= 0 and self.pattern[j] == text[i + j]:
                j -= 1
            if j < 0:
                positions.append(i)
                i += m
            else:
                i += max(1, j - self.bad_char.get(text[i + j], -1))

        return SearchResult(
            {self.pattern: len(positions)},
            {self.pattern: positions}
        )
