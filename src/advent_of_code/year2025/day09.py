from abc import ABC

from advent_of_code.problems import MultiLineProblem


class _Problem(MultiLineProblem[int], ABC):
    def __init__(self) -> None:
        pass


class Problem1(_Problem):
    test_solution = None
    puzzle_solution = None

    def solution(self) -> int:
        return 0


class Problem2(_Problem):
    test_solution = None
    puzzle_solution = None

    def solution(self) -> int:
        return 0


TEST_INPUT = """
7,1
11,1
11,7
9,7
9,5
2,5
2,3
7,3
"""
