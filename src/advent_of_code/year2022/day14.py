from abc import ABC, abstractmethod
from itertools import pairwise
from typing import TYPE_CHECKING

from kleur import GREY, ColorStr
from parse import parse  # type: ignore[import-untyped]
from ternimator import AnimParams

from advent_of_code import C, log
from advent_of_code.problems import MultiLineProblem
from advent_of_code.utils import lowlighted
from advent_of_code.utils.geo2d import P2, MutableCharGrid2

if TYPE_CHECKING:
    from collections.abc import Iterator

MC = [
    (".", GREY.very_dark),  # air
    ("#", C.pink.slightly_dark),  # rock
    ("o", C.brown.saturated(0.33).very_bright),  # sand
    ("+", C.blue),  # source
]
MATERIAL_COLORS = {m: lowlighted(c)(m) for m, c in MC}
START = START_X, START_Y = 500, 0


def format_value(_p: P2, v: str, _colored: ColorStr) -> ColorStr:
    return MATERIAL_COLORS[v]


class _Problem(MultiLineProblem[int], ABC):
    def __init__(self) -> None:
        self.map = MutableCharGrid2(dict.fromkeys(self.points, "#"), allow_resize=True)
        self.map[START] = "+"

    @property
    def points(self) -> Iterator[P2]:
        for line in self.lines:
            for (x1, y1), (x2, y2) in pairwise(
                parse("{:d},{:d}", x) for x in line.split(" -> ")
            ):
                (x_lo, x_hi), (y_lo, y_hi) = sorted((x1, x2)), sorted((y1, y2))
                for x in range(x_lo, x_hi + 1):
                    for y in range(y_lo, y_hi + 1):
                        yield x, y

    def next_pos(self, x: int, y: int) -> P2:
        for dx in 0, -1, 1:
            np = x + dx, y + 1
            if np not in self.map:
                return np
        return START

    @abstractmethod
    def keep_going(self, x: int, y: int) -> bool: ...

    def go(self) -> Iterator[Iterator[str]]:
        x, y = START
        rocks = self.map.points_with_value("#")
        keep_x = [x, *sorted(x for x, _ in rocks)]
        keep_y = [y, *sorted(y for _, y in rocks)]
        while self.keep_going(x, y):
            np = self.next_pos(x, y)
            if np == START:
                self.map[x, y] = "o"
                yield self.map.to_lines(
                    format_value=format_value, keep_x=keep_x, keep_y=keep_y
                )
            x, y = np


class Problem1(_Problem):
    test_solution = 24
    puzzle_solution = 964

    def keep_going(self, x: int, y: int) -> bool:
        (min_x, _), (max_x, max_y) = self.map.span
        return min_x <= x <= max_x and y < max_y

    def solution(self) -> int:
        maps = self.go()
        log.debug_animated(maps, AnimParams(fps=60, only_every_nth=20))
        return sum(m == "o" for m in self.map.values())


class Problem2(_Problem):
    test_solution = 93
    puzzle_solution = 32041

    def keep_going(self, _x: int, _y: int) -> bool:
        return self.map[START] == "+"

    def solution(self) -> int:
        _, (_, y_max) = self.map.span
        y_max += 2
        sx, _ = START
        for x in range(-y_max, y_max + 1):
            self.map[sx + x, y_max] = "#"

        maps = self.go()
        log.debug_animated(maps, AnimParams(fps=60, only_every_nth=500))
        return sum(m == "o" for m in self.map.values())


TEST_INPUT = """
498,4 -> 498,6 -> 496,6
503,4 -> 502,4 -> 502,9 -> 494,9
"""
