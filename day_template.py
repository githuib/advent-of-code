from abc import ABC

from advent_of_code.problems import MultiLineProblem


class _Problem(MultiLineProblem[int], ABC):
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

"""
