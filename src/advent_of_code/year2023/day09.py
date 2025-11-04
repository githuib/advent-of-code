from itertools import pairwise
from typing import TYPE_CHECKING

from advent_of_code import log
from advent_of_code.problems import MultiLineProblem
from advent_of_code.utils.data import Unique

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence


class Problem1(MultiLineProblem[int]):
    test_solution = 114
    my_solution = 1772145754

    def __init__(self) -> None:
        self.sequences = [[int(i) for i in line.split()] for line in self.lines]

    def solution(self) -> int:
        def diffs(seq: Sequence[int]) -> Iterator[int]:
            while any(seq):
                yield seq[-1]
                seq = [b - a for a, b in pairwise(seq)]

        log.debug({Unique(sum(diffs(seq))): list(diffs(seq)) for seq in self.sequences})
        return sum(sum(diffs(seq)) for seq in self.sequences)


class Problem2(Problem1):
    test_solution = 2
    my_solution = 867

    def __init__(self) -> None:
        super().__init__()
        self.sequences = [list(reversed(seq)) for seq in self.sequences]


TEST_INPUT = """
0 3 6 9 12 15
1 3 6 10 15 21
10 13 16 21 30 45
"""
