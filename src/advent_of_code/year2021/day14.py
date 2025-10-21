from abc import ABC
from collections import Counter
from itertools import pairwise

from advent_of_code.problems import MultiLineProblem


class _Problem(MultiLineProblem[int], ABC):
    def _solution(self, steps: int) -> int:
        template = self.lines[0]
        rules: dict[str, str] = dict([line.split(" -> ") for line in self.lines[2:]])
        pair_count = Counter(a + b for a, b in pairwise(template))
        polymer_count = Counter(template)

        for _ in range(steps):
            new_pair_count: Counter[str] = Counter()

            for s, count in pair_count.items():
                a, b = s[0], s[1]
                x = rules[a + b]
                polymer_count[x] += count
                new_pair_count[a + x] += count
                new_pair_count[x + b] += count

            pair_count = new_pair_count

        counts = polymer_count.values()
        return max(counts) - min(counts)


class Problem1(_Problem):
    def solution(self) -> int:
        return self._solution(10)


class Problem2(_Problem):
    def solution(self) -> int:
        return self._solution(40)


TEST_INPUT = """
NNCB

CH -> B
HH -> N
CB -> H
NH -> C
HB -> C
HC -> B
HN -> C
NN -> C
BH -> H
NC -> B
NB -> B
BN -> B
BB -> N
BC -> B
CC -> N
CN -> C
"""
