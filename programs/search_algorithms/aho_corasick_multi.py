# search_algorithms/aho_corasick_multi.py

from .base import SearchAlgorithm, SearchResult
from collections import deque, defaultdict


class AhoCorasickMulti(SearchAlgorithm):
    def __init__(self, patterns):
        """
        patterns: list[str]
        """
        super().__init__(pattern="")
        self.patterns = patterns
        self.state = 0
        self.name = "Aho–Corasick (Multi Pattern)"
        self.goto = {}
        self.out = defaultdict(list)
        self.fail = {}
        self.build_automaton(patterns)
    
    def get_description(self):
        return ( "Aho–Corasickアルゴリズムは複数パターンを同時に検索できる手法で、Trie構造と失敗遷移（Fail-Link）を用いてテキストを一度走査するだけですべてのパターンを高速に検出できます。^^" )

    def build_automaton(self, patterns):
        self.goto[0] = {}
        new_state = 0

        # 1. GOTO 関数の構築
        for pattern in patterns:
            state = 0
            for char in pattern:
                if char not in self.goto[state]:
                    new_state += 1
                    self.goto[state][char] = new_state
                    self.goto[new_state] = {}
                state = self.goto[state][char]
            self.out[state].append(pattern)

        # 2. FAIL 関数の構築
        queue = deque()

        # 深さ1の fail を 0 に設定
        for char, next_state in self.goto[0].items():
            self.fail[next_state] = 0
            queue.append(next_state)

        # BFS で fail を構築
        while queue:
            r = queue.popleft()
            for char, s in self.goto[r].items():
                queue.append(s)

                state = self.fail[r]
                while state != 0 and char not in self.goto[state]:
                    state = self.fail[state]

                self.fail[s] = self.goto[state].get(char, 0)

                # 出力の継承
                self.out[s].extend(self.out[self.fail[s]])

    def search(self, text: str) -> SearchResult:
        state = 0
        counts = defaultdict(int)
        positions = defaultdict(list)

        for i, char in enumerate(text):
            while state != 0 and char not in self.goto[state]:
                state = self.fail[state]

            state = self.goto[state].get(char, 0)

            for pattern in self.out[state]:
                counts[pattern] += 1
                positions[pattern].append(i - len(pattern) + 1)

        return SearchResult(dict(counts), dict(positions))
    
    def search_chunk(self, text: str, offset: int = 0) -> SearchResult:
        counts = defaultdict(int)
        positions = defaultdict(list) 
        for i, char in enumerate(text): 
            while self.state != 0 and char not in self.goto[self.state]: 
                self.state = self.fail[self.state] 
            self.state = self.goto[self.state].get(char, 0) 
            for pattern in self.out[self.state]: 
                counts[pattern] += 1 
                positions[pattern].append(offset + i - len(pattern) + 1) 
        return SearchResult(dict(counts), dict(positions))