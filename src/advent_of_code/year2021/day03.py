from abc import ABC, abstractmethod

from advent_of_code.problems import MultiLineProblem
from advent_of_code.utils import bits_to_int


def winning_bit(codes: list[list[bool]], inverse: bool):
    # bit occurring in half or more of all first bits
    return (sum(first for first, *_ in codes) * 2 >= len(codes)) ^ inverse


class _Problem(MultiLineProblem[int], ABC):
    def __init__(self):
        self.codes = [[c == "1" for c in line] for line in self.lines]

    @abstractmethod
    def process_codes_tail_rec(
        self, codes: list[list[bool]], result: list[bool], inverse: bool = False
    ):
        pass

    def solution(self) -> int:
        gamma = bits_to_int(self.process_codes_tail_rec(self.codes, []))
        epsilon = bits_to_int(self.process_codes_tail_rec(self.codes, [], inverse=True))
        return gamma * epsilon


class Problem1(_Problem):
    test_solution = 198
    my_solution = 1071734

    def process_codes_tail_rec(
        self, codes: list[list[bool]], result: list[bool], inverse: bool = False
    ):
        if not codes[0]:
            return result

        return self.process_codes_tail_rec(
            [rest for _, *rest in codes],
            [*result, winning_bit(codes, inverse)],
            inverse,
        )


class Problem2(_Problem):
    test_solution = 230
    my_solution = 6124992

    def process_codes_tail_rec(
        self, codes: list[list[bool]], result: list[bool], inverse: bool = False
    ):
        if len(codes) == 0:
            return result

        if len(codes) == 1:
            return result + codes[0]

        winner = winning_bit(codes, inverse)

        return self.process_codes_tail_rec(
            [rest for first, *rest in codes if first == winner],
            [*result, winner],
            inverse,
        )


TEST_INPUT = """
00100
11110
10110
10111
10101
01111
00111
11100
10000
11001
00010
01010
"""
