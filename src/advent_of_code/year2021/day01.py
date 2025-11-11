from abc import ABC

from advent_of_code.problems import MultiLineProblem


class _Problem(MultiLineProblem[int], ABC):
    window_size: int

    def solution(self) -> int:
        depths = [int(line) for line in self.lines]
        return sum(
            sum(depths[i + 1 : i + self.window_size + 1])
            > sum(depths[i : i + self.window_size])
            for i in range(len(depths) - 1)
        )


class Problem1(_Problem):
    test_solution = 7
    puzzle_solution = 1832

    window_size = 1


class Problem2(_Problem):
    test_solution = 5
    puzzle_solution = 1858

    window_size = 3


TEST_INPUT = """
199
200
208
210
200
207
240
269
260
263
"""
