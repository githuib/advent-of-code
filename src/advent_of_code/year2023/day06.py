import re
from abc import ABC
from math import ceil, prod, sqrt

from advent_of_code import log
from advent_of_code.problems import MultiLineProblem
from advent_of_code.utils import compose_number


def ways_to_win(time: int, dist: int) -> int:
    # squirt = sqrt(time ** 2 - dist * 4)
    # x_max = (time + squirt) / 2
    # x_min = (time - squirt) / 2
    # x_min, x_max = solve_quadratic(-1, time, -dist)
    # return ceil(x_max) - floor(x_min) - 1
    o = time % 2
    return ceil((sqrt(time**2 - dist * 4) - o) / 2) * 2 + o - 1


class _Problem(MultiLineProblem[int], ABC):
    def __init__(self):
        self.parsed = [
            [int(s) for s in re.findall(r"\d+", line)] for line in self.lines
        ]
        log.debug(self.parsed)


class Problem1(_Problem):
    test_solution = 288
    my_solution = 3316275

    def solution(self) -> int:
        return prod(ways_to_win(t, d) for t, d in zip(*self.parsed, strict=False))


class Problem2(_Problem):
    test_solution = 71503
    my_solution = 27102791

    def solution(self) -> int:
        return ways_to_win(*[compose_number(line) for line in self.parsed])


TEST_INPUT = """
Time:      7  15   30
Distance:  9  40  200
"""
