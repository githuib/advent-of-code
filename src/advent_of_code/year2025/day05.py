from abc import ABC

from based_utils.iterators import polarized, split_items

from advent_of_code.problems import MultiLineProblem

type Range = tuple[int, int]
type Ranges = list[Range]


def parse_range(s: str) -> Range:
    lo, hi = s.split("-")
    return int(lo), int(hi) + 1


class _Problem(MultiLineProblem[int], ABC):
    def __init__(self) -> None:
        ranges, ids = split_items(self.lines, delimiter="")
        self.ranges = sorted(parse_range(r) for r in ranges)
        self.ids = [int(i) for i in ids]


class Problem1(_Problem):
    test_solution = 3
    puzzle_solution = 726

    def solution(self) -> int:
        return sum(any(lo <= i <= hi for lo, hi in self.ranges) for i in self.ids)


def reduced(ranges: Ranges) -> Ranges:
    if not ranges:
        return []

    (lo, hi), rest = ranges[0], ranges[1:]
    if not rest:
        return [(lo, hi)]

    left, right = polarized(rest, lambda r: r[0] <= hi)
    far_right = reduced(right)
    if not left:
        return [(lo, hi), *far_right]

    return reduced([(lo, max(hi, *[h for _, h in left])), *far_right])


class Problem2(_Problem):
    test_solution = 14
    puzzle_solution = 354226555270043

    def solution(self) -> int:
        return sum(hi - lo for lo, hi in reduced(self.ranges))


TEST_INPUT = """
3-5
10-14
16-20
12-18

1
5
8
11
17
32
"""
