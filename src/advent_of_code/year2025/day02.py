from abc import ABC

from advent_of_code.problems import OneLineProblem


def invalid(lo: str, hi: str, d: int) -> set[int]:
    n_lo, n_hi = len(lo), len(hi)
    lo_even, hi_even = n_lo % d == 0, n_hi % d == 0
    if not (lo_even or hi_even):
        return set()

    i_lo = int(lo) if lo_even else 10 ** (n_hi - 1)
    i_hi = int(hi) if hi_even else 10**n_lo - 1
    lo, hi = str(i_lo), str(i_hi)
    n_half = len(lo) // d
    i_lo_half, i_hi_half = int(lo[:n_half]), int(hi[:n_half])
    return {
        j
        for i in range(i_lo_half, i_hi_half + 1)
        if i_lo <= (j := int(str(i) * d)) <= i_hi
    }


class _Problem(OneLineProblem[int], ABC):
    def __init__(self) -> None:
        self.ranges = [s.split("-") for s in self.line.split(",")]

    def numbers(self, n: int) -> set[int]:
        nrs = (invalid(lo, hi, d) for lo, hi in self.ranges for d in range(2, n + 1))
        return set.union(*nrs)


class Problem1(_Problem):
    test_solution = 1227775554
    puzzle_solution = 41294979841

    def solution(self) -> int:
        return sum(self.numbers(2))


class Problem2(_Problem):
    test_solution = 4174379265
    puzzle_solution = 66500947346

    def solution(self) -> int:
        return sum(self.numbers(max(len(hi) for lo, hi in self.ranges)))


TEST_INPUT = """
11-22,95-115,998-1012,1188511880-1188511890,222220-222224,1698522-1698528,446443-446449,38593856-38593862,565653-565659,824824821-824824827,2121212118-2121212124
"""
