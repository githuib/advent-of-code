from abc import ABC, abstractmethod

from advent_of_code import log
from advent_of_code.problems import MultiLineProblem


class _Problem(MultiLineProblem[int], ABC):
    def __init__(self) -> None:
        self.rotations: list[tuple[str, int]] = [(s[0], int(s[1:])) for s in self.lines]
        self.dial = 50
        self.counter = 0

    @abstractmethod
    def step(self, direction: str, n: int) -> int: ...

    def solution(self) -> int:
        for d, n in self.rotations:
            self.dial = self.step(d, self.dial + (n if d == "R" else -n))
            log.debug(f"{d} {n:02d} -> Dial {self.dial:02d}, count {self.counter}")
        return self.counter


class Problem1(_Problem):
    test_solution = 3
    puzzle_solution = 1129

    def step(self, _direction: str, n: int) -> int:
        d = n % 100
        if d == 0:
            self.counter += 1
        return d


class Problem2(_Problem):
    test_solution = 6
    puzzle_solution = 6638

    def step(self, direction: str, n: int) -> int:
        beyond = n if direction == "R" else -n if self.dial == 0 else 100 - n
        if beyond >= 0:
            self.counter += beyond // 100
        return n % 100


TEST_INPUT = """
L68
L30
R48
L5
R60
L55
L1
L99
R14
L82
"""
