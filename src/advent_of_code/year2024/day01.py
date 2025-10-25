from abc import ABC, abstractmethod

from advent_of_code.problems import ParsedProblem


class _Problem(ParsedProblem[tuple[int, int], int], ABC):
    line_pattern = "{:d}   {:d}"

    @abstractmethod
    def _compare(self, n1: int, n2: int) -> int:
        return NotImplemented

    def solution(self) -> int:
        return sum(
            self._compare(n1, n2)
            for n1, n2 in zip(
                *(sorted(ns) for ns in zip(*self.parsed_input, strict=True)),
                strict=True,
            )
        )


class Problem1(_Problem):
    test_solution = 11
    my_solution = 1341714

    def _compare(self, n1: int, n2: int) -> int:
        return abs(n1 - n2)


class Problem2(_Problem):
    test_solution = 31
    my_solution = None

    def _compare(self, n1: int, n2: int) -> int:
        return abs(n1 - n2)


TEST_INPUT = """
3   4
4   3
2   5
1   3
3   9
3   3
"""
