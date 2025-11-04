from abc import abstractmethod

from advent_of_code.problems import ParsedProblem


class _Problem(ParsedProblem[tuple[int, int, int, int], int]):
    line_pattern = "{:d}-{:d},{:d}-{:d}"

    @abstractmethod
    def has_overlaps(self, s1: set[int], s2: set[int]) -> bool:
        pass

    def solution(self) -> int:
        return sum(
            self.has_overlaps(set(range(l1, h1 + 1)), set(range(l2, h2 + 1)))
            for l1, h1, l2, h2 in self.parsed_input
        )


class Problem1(_Problem):
    test_solution = 2
    my_solution = 515

    def has_overlaps(self, s1: set[int], s2: set[int]) -> bool:
        return s1.issubset(s2) or s2.issubset(s1)


class Problem2(_Problem):
    test_solution = 4
    my_solution = 883

    def has_overlaps(self, s1: set[int], s2: set[int]) -> bool:
        return len(s1 & s2) > 0


TEST_INPUT = """
2-4,6-8
2-3,4-5
5-7,7-9
2-8,3-7
6-6,4-6
2-6,4-8
"""
