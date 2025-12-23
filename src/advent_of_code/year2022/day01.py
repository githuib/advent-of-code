from abc import ABC
from operator import not_

from based_utils.data import try_convert
from more_itertools import split_at

from advent_of_code.problems import MultiLineProblem


class _Problem(MultiLineProblem[int], ABC):
    def __init__(self) -> None:
        self.calorie_totals = [
            sum(try_convert(int, c, default=0) for c in elf_calories)
            for elf_calories in split_at(self.lines, not_)
        ]


class Problem1(_Problem):
    test_solution = 24000
    puzzle_solution = 72017

    def solution(self) -> int:
        return max(self.calorie_totals)


class Problem2(_Problem):
    test_solution = 45000
    puzzle_solution = 212520

    def solution(self) -> int:
        return sum(sorted(self.calorie_totals)[-3:])


TEST_INPUT = """
1000
2000
3000

4000

5000
6000

7000
8000
9000

10000
"""
