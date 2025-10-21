from abc import ABC

from advent_of_code import log
from advent_of_code.problems import ParsedProblem


def __parse_numbers(s: str) -> set[str]:
    return set(s.split())


class _Problem(ParsedProblem[tuple[set[str], set[str]], int], ABC):
    line_pattern = ": {:numbers} | {:numbers}"

    def __init__(self) -> None:
        self.matching = [len(winning & mine) for winning, mine in self.parsed_input]
        log.debug(self.matching)


class Problem1(_Problem):
    test_solution = 13
    my_solution = 20117

    def solution(self) -> int:
        return sum(2 ** (w - 1) for w in self.matching if w)


class Problem2(_Problem):
    test_solution = 30
    my_solution = 13768818

    def solution(self) -> int:
        n = self.line_count
        cards = [1] * n
        for i, w in enumerate(self.matching, 1):
            for j in range(i, min(i + w, n)):
                cards[j] += cards[i - 1]
        log.debug(cards)
        return sum(cards)


TEST_INPUT = """
Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53
Card 2: 13 32 20 16 61 | 61 30 68 82 17 32 24 19
Card 3:  1 21 53 59 44 | 69 82 63 72 16 21 14  1
Card 4: 41 92 73 84 69 | 59 84 76 51 58  5 54 83
Card 5: 87 83 26 28 32 | 88 30 70 12 93 22 82 36
Card 6: 31 18 13 56 72 | 74 77 10 23 35 67 36 11
"""
