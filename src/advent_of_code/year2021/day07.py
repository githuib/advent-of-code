from abc import ABC
from functools import cache

from advent_of_code.problems import OneLineProblem


class _Problem(OneLineProblem[int], ABC):
    false: bool

    def solution(self) -> int:
        positions = [int(x) for x in self.line.split(",")]

        @cache
        def gas_op_die_lollie(x: int) -> int:
            return x * (x + 1) // 2 if self.false else x

        return min(
            sum(gas_op_die_lollie(abs(p - q)) for p in positions)
            for q in range(max(positions) + 1)
        )


class Problem1(_Problem):
    test_solution = 37
    puzzle_solution = 349812

    false = False


class Problem2(_Problem):
    test_solution = 168
    puzzle_solution = 99763899

    false = True


TEST_INPUT = "16,1,2,0,4,2,7,1,2,14"
