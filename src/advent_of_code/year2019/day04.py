from abc import ABC, abstractmethod
from collections import Counter

from advent_of_code.problems import OneLineProblem


class _Problem(OneLineProblem[int], ABC):
    def __init__(self) -> None:
        self.a, self.b = self.line.split("-")

    @abstractmethod
    def sequence_condition(self, s: str) -> bool:
        pass

    def solution(self) -> int:
        return len(
            [
                # filter out numbers that aren't in the given range
                valid_number
                for valid_number in sorted(
                    # filter out numbers that don't pass the given number sequence
                    # condition
                    int(number_str)
                    for number_str in {
                        # reorder all numbers [0, 999999] to be increasing and filter
                        # out duplicates
                        "".join(sorted(str(number)))
                        for number in range(999999)
                    }
                    if self.sequence_condition(number_str)
                )
                if 206938 <= valid_number <= 679128
            ]
        )


class Problem1(_Problem):
    test_solution = None
    my_solution = 1653

    def sequence_condition(self, s: str) -> bool:
        return len(s) > len(set(s))


class Problem2(_Problem):
    test_solution = None
    my_solution = 1133

    def sequence_condition(self, s: str) -> bool:
        return 2 in Counter(s).values()


TEST_INPUT = """

"""
