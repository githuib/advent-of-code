import re
from abc import abstractmethod

from advent_of_code.problems import MultiLineProblem


class _Problem(MultiLineProblem[int]):
    _pattern: re.Pattern

    @abstractmethod
    def _parse(self, s: str) -> str:
        pass

    def solution(self) -> int:
        return sum(
            int(self._parse(matches[0]) + self._parse(matches[-1]))
            for line in self.lines
            if (matches := self._pattern.findall(line))
        )


class Problem1(_Problem):
    test_solution = 142
    my_solution = 53080

    _pattern = re.compile(r"[1-9]")

    def _parse(self, s: str) -> str:
        return s


TEST_INPUT = """
1abc2
pqr3stu8vwx
a1b2c3d4e5f
treb7uchet
"""

DIGIT_NAMES = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
DIGITS = {s: str(i) for i, s in enumerate(DIGIT_NAMES, 1)}


class Problem2(_Problem):
    test_solution = 281
    my_solution = 53268

    _pattern = re.compile(rf"(?=([1-9]|{'|'.join(DIGIT_NAMES)}))")

    def _parse(self, s: str) -> str:
        return DIGITS.get(s, s)


TEST_INPUT_2 = """
two1nine
eightwothree
abcone2threexyz
xtwone3four
4nineeightseven2
zoneight234
7pqrstsixteen
"""
