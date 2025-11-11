from abc import ABC

from .intcode import IntcodeProblem


class _Problem(IntcodeProblem[int], ABC):
    pass


class Problem1(_Problem):
    test_solution = 27
    puzzle_solution = 126

    def solution(self) -> int:
        return 0


class Problem2(_Problem):
    test_solution = 250020
    puzzle_solution = None

    def solution(self) -> int:
        return 0


TEST_INPUT = ""
