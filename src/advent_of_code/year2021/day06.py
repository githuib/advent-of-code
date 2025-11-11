from abc import ABC
from collections import Counter

from advent_of_code.problems import OneLineProblem


class _Problem(OneLineProblem[int], ABC):
    steps: int

    def solution(self) -> int:
        intitial_count = Counter(int(x) for x in self.line.split(","))
        fish = [intitial_count.get(i, 0) for i in range(9)]
        for i in range(self.steps):
            fish[(i + 7) % 9] += fish[i % 9]
        return sum(fish)


class Problem1(_Problem):
    test_solution = 5934
    puzzle_solution = 362740

    steps = 80


class Problem2(_Problem):
    test_solution = 26984457539
    puzzle_solution = 1644874076764

    steps = 256


TEST_INPUT = "3,4,3,1,2"
