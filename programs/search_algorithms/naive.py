# search_algorithms/naive.py

class NaiveSearch:
    def __init__(self, pattern: str):
        self.pattern = pattern
        self.name = "Naive Search"

    def get_description(self):
        return ("""Naiveアルゴリズムは、先頭文字から順々に力任せに文字列探索するやつです。効率は悪いですが、文字列探索の元祖なんで学習用にはいいかもね。プログラムも単純です^^
m文字のテキストからn文字のパターンを見つける場合、n回の比較（パターンマッチング）をm回ループするのでO(mn)程度の計算量になりますな^^

例： "hello" というテキストから "lo" というパターンを見つける場合↓
1回目 ... "hello"の1文字目と"lo"の1文字目を比較 違うので次へ
2回目 ... "hello"の2文字目と"lo"の1文字目を比較 違うので次へ
3回目 ... "hello"の3文字目と"lo"の1文字目を比較 一致！
　　      "hello"の4文字目と"lo"の2文字目を比較 違うので次へ
4回目 ... "hello"の4文字目と"lo"の1文字目を比較 一致！
　　      "hello"の5文字目と"lo"の2文字目を比較 一致！終了！

上では6回の比較操作で探索が終了しました。理論的には"hello"が5文字で"lo"が2文字なので、O(2*5)=O(10)で最大でも10回程度の比較で探索が終了することがわかりますぜ。
最悪のケースは "AAAAAAAAAAA" のような繰り返し文字が多いテキストで "AAAB" のようなパターンを探索する場合ですね。
                """)

    def search(self, text: str):
        m = len(self.pattern)
        n = len(text)

        positions = []

        for i in range(n - m + 1):
            if text[i:i+m] == self.pattern:
                positions.append(i)

        return positions

    def search_chunk(self, chunk: str, offset: int):
        m = len(self.pattern)
        n = len(chunk)

        positions = []

        for i in range(n - m + 1):
            if chunk[i:i+m] == self.pattern:
                positions.append(i + offset)

        return positions
