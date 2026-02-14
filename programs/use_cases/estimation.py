import os

class EstimationUseCase:
    def execute(self, file_paths: list[str], algorithm_key: str, patterns: list[str], benchmark_coeffs: dict, bitap_distance: int = 0):
        seconds = self.get_seconds(file_paths, algorithm_key, patterns, benchmark_coeffs, bitap_distance)
        if seconds is None:
            if not file_paths: return "ファイル未選択"
            return ""

        if seconds < 1e-3:
            return f"時間の目安：{seconds*1e6:.1f}マイクロ秒"
        elif seconds < 1:
            return f"時間の目安：{seconds*1000:.1f}ミリ秒"
        else:
            return f"時間の目安：{seconds:.2f}秒"

    def get_seconds(self, file_paths, algorithm_key, patterns, benchmark_coeffs, bitap_distance=0):
        if not file_paths or not patterns:
            return None

        total_size = sum(os.path.getsize(p) for p in file_paths)
        N_KB = total_size / 1024

        num_patterns = len(patterns)
        coeff = benchmark_coeffs.get(algorithm_key, 1.0)

        avg_len = sum(len(p) for p in patterns) / num_patterns
        length_factor = max(1.0, avg_len / 16)

        if algorithm_key == "naive":
            pattern_factor = num_patterns * (avg_len / 8)
        elif algorithm_key == "bm":
            pattern_factor = num_patterns * (avg_len / 12)
        elif algorithm_key == "kmp":
            pattern_factor = num_patterns * (avg_len / 20)
        elif algorithm_key == "bitap":
            d = max(1, bitap_distance)
            pattern_factor = num_patterns * (avg_len / 8) * (d / 2)
        else:  # AC
            pattern_factor = 1.0

        return N_KB * coeff * length_factor * pattern_factor
