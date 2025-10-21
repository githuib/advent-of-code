from abc import abstractmethod
from typing import TYPE_CHECKING

from advent_of_code.problems import MultiLineProblem

if TYPE_CHECKING:
    from collections.abc import Iterator


class _Problem(MultiLineProblem[int]):
    def __init__(self):
        self.converted_lines = [
            [ord(c) - (ord("a") - 1 if c.islower() else ord("A") - 27) for c in line]
            for line in self.lines
        ]

    @abstractmethod
    def rucksacks(self) -> Iterator[list[set[int]]]:
        pass

    def solution(self) -> int:
        return sum(i for r in self.rucksacks() for i in set.intersection(*r))


class Problem1(_Problem):
    test_solution = 157
    my_solution = 7878

    def rucksacks(self) -> Iterator[list[set[int]]]:
        def split(nums: list[int]) -> list[set[int]]:
            n = len(nums) // 2
            return [set(nums[:n]), set(nums[n:])]

        for line in self.converted_lines:
            yield split(line)


class Problem2(_Problem):
    test_solution = 70
    my_solution = 2760

    def rucksacks(self) -> Iterator[list[set[int]]]:
        for n in range(0, self.line_count, 3):
            yield [set(line) for line in self.converted_lines[n:n + 3]]


TEST_INPUT = """
vJrwpWtwJgWrhcsFMMfFFhFp
jqHRNqRjqzjGDLGLrsFMfFZSrLrFZsSL
PmmdzqPrVvPwwTWBwg
wMqvLMZHhHMvwLHjbvcjnnSBnvTQFn
ttgJtRGJQctTZtZT
CrZsJsPPZsGzwwsLwLmpwMDw
"""
