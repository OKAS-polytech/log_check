from domain.interfaces.search_algorithm import SearchAlgorithm
from domain.models.search_result import SearchResult
from domain.utils import levenshtein

class BitapSearch(SearchAlgorithm):
    def __init__(self, pattern: str, max_distance: int = 2):
        super().__init__(pattern)
        self.max_distance = max_distance
        self.name = f"Bitap (d={max_distance})"

    def get_description(self):
        return (
            "Bitap法はあいまい(Fuzzy)検索可能な文字列探索です。"
            "レーベンシュタイン距離（文字列の置換・削除・挿入等の操作につき1加算）を使って、"
            "指定距離以下の近似一致を検出します。^^"
            "レーベンシュタイン距離がわかりにくかったら「何文字まで変わっててもセーフか」みたいな感覚でOK^^"
        )

    def search(self, text: str) -> SearchResult:
        m = len(self.pattern)
        if m == 0:
            return SearchResult({"": 0}, {"": []})

        mask = {}
        for i, c in enumerate(self.pattern):
            mask[c] = mask.get(c, 0) | (1 << i)

        BITMASK = (1 << m) - 1
        R = [0] * (self.max_distance + 1)
        matches = []

        for i, c in enumerate(text):
            char_mask = mask.get(c, 0)
            old_r0 = R[0]
            R[0] = ((R[0] << 1) | 1) & char_mask
            R[0] &= BITMASK

            prev = old_r0
            for d in range(1, self.max_distance + 1):
                old_rd = R[d]
                sub_or_match = ((R[d] << 1) | 1) & char_mask
                ins = (prev << 1) | 1
                delete = prev

                R[d] = (sub_or_match | ins | delete) & BITMASK
                prev = old_rd

            if (R[self.max_distance] & (1 << (m - 1))) != 0:
                start = i - m + 1 - self.max_distance
                end = i + 1
                ws = max(0, start)
                we = min(len(text), end)
                window = text[ws:we]

                best_dist = None
                best_pos = None

                for j in range(0, len(window) - m + 1):
                    sub = window[j:j + m]
                    dist = levenshtein(self.pattern, sub)

                    if best_dist is None or dist < best_dist:
                        best_dist = dist
                        best_pos = ws + j

                if best_dist is not None and best_dist <= self.max_distance:
                    matches.append((best_pos, best_dist))

        unique_matches = []
        seen_pos = set()
        for pos, dist in matches:
            if pos not in seen_pos:
                unique_matches.append((pos, dist))
                seen_pos.add(pos)

        counts = {self.pattern: len(unique_matches)}
        positions = {self.pattern: [pos for pos, dist in unique_matches]}
        distances = {self.pattern: [dist for pos, dist in unique_matches]}

        return SearchResult(counts, positions, distances)

    def search_chunk(self, text: str, offset: int = 0) -> SearchResult:
        raise NotImplementedError("Bitapはストリーム非対応.")
