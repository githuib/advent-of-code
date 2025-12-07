from abc import ABC

from advent_of_code import log
from advent_of_code.problems import NumGridProblem


def joltage(n: list[int], left: int) -> int:
    if left == 0:
        d = max(n)
        log.debug(f"{n} -> {d}")
        return d

    d = max(n[:-left])
    log.debug(f"{n} -> {d}")
    return d * 10**left + joltage(n[n.index(d) + 1 :], left - 1)


class _Problem(NumGridProblem[int], ABC):
    number_size: int

    def joltage(self, n: list[int]) -> int:
        j = joltage(n, self.number_size - 1)
        log.debug(f"⚡️Joltage: {j}")
        return j

    def solution(self) -> int:
        return sum(self.joltage(row) for row in self.grid.rows)


class Problem1(_Problem):
    test_solution = 357
    puzzle_solution = 17142

    number_size = 2


class Problem2(_Problem):
    test_solution = 3121910778619
    puzzle_solution = 169935154100102

    number_size = 12


TEST_INPUT = """
987654321111111
811111111111119
234234234234278
818181911112111
"""
