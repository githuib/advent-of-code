from abc import ABC, abstractmethod

from advent_of_code import log
from advent_of_code.problems import MultiLineProblem


class _Problem(MultiLineProblem[int], ABC):
    def __init__(self) -> None:
        self.rotations = [(line[0] == "L", int(line[1:])) for line in self.lines]
        self.dial = 50

    @abstractmethod
    def count_clicks(self, new_dial: int) -> int: ...

    def solution(self) -> int:
        clicks = 0
        for go_left, n in self.rotations:
            new_dial = self.dial + (-n if go_left else n)
            counted = self.count_clicks(new_dial)
            clicks += counted
            self.dial = new_dial % 100

            s = f"👈 {n:<3}" if go_left else f"{n:>3} 👉"
            log.debug(f"Dial {s} = {self.dial:>2}  Clicks +{counted:<2} = {clicks}")
        return clicks


class Problem1(_Problem):
    test_solution = 3
    puzzle_solution = 1129

    def count_clicks(self, new_dial: int) -> int:
        return 1 if new_dial % 100 == 0 else 0


class Problem2(_Problem):
    test_solution = 6
    puzzle_solution = 6638

    def count_clicks(self, new_dial: int) -> int:
        b = new_dial
        if new_dial < self.dial:
            b += 99 if self.dial == 0 else -1
        return abs(b // 100)


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
