from core.utils import levenshtein

def myers_bitap(text, pattern, max_distance):
    m = len(pattern)
    if m == 0:
        return []

    # パターンマスク
    mask = {}
    for i, c in enumerate(pattern):
        mask[c] = mask.get(c, 0) | (1 << i)

    VP = (1 << m) - 1
    VN = 0
    curr_dist = m

    matches = []

    for i, c in enumerate(text):
        char_mask = mask.get(c, 0)

        X = char_mask | VN
        D0 = (((X & VP) + VP) ^ VP) | X

        HP = VN | ~(D0 | VP)
        HN = VP & D0

        VP = (HN << 1) | ~(D0 | ((HP << 1) | 1))
        VN = (HP << 1) & D0

        # 編集距離の更新
        if (D0 & (1 << (m - 1))) == 0:
            curr_dist = 0
        else:
            curr_dist += 1

        if curr_dist <= max_distance:
            matches.append((i - m + 1, curr_dist))

    return matches


class BitapSearch:
    def __init__(self, pattern: str, max_distance: int = 2):
        self.pattern = pattern
        self.max_distance = max_distance
        self.name = f"Bitap (d={max_distance})"

    def get_description(self):
        return (
            "Bitap法はあいまい(Fuzzy)検索可能な文字列探索です。"
            "レーベンシュタイン距離（文字列の置換・削除・挿入等の操作につき1加算）を使って、"
            "指定距離以下の近似一致を検出します。^^"
            "レーベンシュタイン距離がわかりにくかったら「何文字まで変わっててもセーフか」みたいな感覚でOK^^"
        )

    def search(self, text: str):
            return self._search_fuzzy(text)

    def _search_fuzzy(self, text: str):
        m = len(self.pattern)
        if m == 0:
            return []

        # パターンマスク
        mask = {}
        for i, c in enumerate(self.pattern):
            mask[c] = mask.get(c, 0) | (1 << i)

        BITMASK = (1 << m) - 1

        # R[d] : 編集距離 d の状態
        R = [BITMASK] * (self.max_distance + 1)

        matches = []

        for i, c in enumerate(text):
            char_mask = mask.get(c, 0)

            # d = 0 の更新（完全一致用）
            prev_rd = R[0]
            R[0] = ((R[0] << 1) | 1) & char_mask
            R[0] &= BITMASK

            # d >= 1 の更新（Myers の正しい fuzzy 遷移）
            prev = prev_rd
            for d in range(1, self.max_distance + 1):
                old_rd = R[d]

                # Myers の fuzzy Bitap 遷移
                sub_or_match = ((R[d] << 1) | 1) & char_mask   # 置換 or 一致
                ins = (prev << 1) | 1                          # 挿入
                delete = prev                                  # 削除

                R[d] = sub_or_match | ins | delete
                R[d] &= BITMASK

                prev = old_rd

            # 一致判定
            if (R[self.max_distance] & (1 << (m - 1))) == 0:
                # 一致位置 i 周辺から window を取る
                start = i - m + 1 - self.max_distance
                end = i + 1
                ws = max(0, start)
                we = min(len(text), end)
                window = text[ws:we]

                best_dist = None
                best_sub = None
                best_pos = None

                # window 内の長さ m の部分文字列を総当たり
                for j in range(0, len(window) - m + 1):
                    sub = window[j:j + m]
                    dist = levenshtein(self.pattern, sub)

                    if best_dist is None or dist < best_dist:
                        best_dist = dist
                        best_sub = sub
                        best_pos = ws + j

                if best_dist is not None and best_dist <= self.max_distance:
                    matches.append((best_pos, best_sub, best_dist))

        return matches
