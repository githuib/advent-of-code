from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from based_utils.calx import InterpolationBounds, LogarithmicInterpolationBounds
from based_utils.cli import Colored
from based_utils.colors import Color, Colors
from more_itertools import last

from advent_of_code import log
from advent_of_code.problems import MultiLineProblem
from advent_of_code.utils.geo2d import P2, MutableNumGrid2

if TYPE_CHECKING:
    from collections.abc import Iterator


def parse(s: str) -> int:
    return -1 if s == "^" else 1 if s == "S" else 0


# Maximum value v will have with my input
VALUE_MAPPING = LogarithmicInterpolationBounds(1.01, 2205720519616)
HUE_MAPPING = InterpolationBounds(0.8, -0.1)
SHADE_MAPPING = InterpolationBounds(0.3, 0.6)

C_SPLITTER = Colors.blue.dark.saturated(0.6)
C_BACKGROUND = Colors.blue.very_dark


def fmt(_p: P2, v: int, _colored: Colored) -> Colored:
    if v == -1:
        return Colored("^", C_SPLITTER)
    if v == 0:
        return Colored(".", C_BACKGROUND)
    f = VALUE_MAPPING.inverse_interpolate(v)
    hue, shade = HUE_MAPPING.interpolate(f), SHADE_MAPPING.interpolate(f)
    return Colored("|", Color(hue=hue, lightness=shade))


class _Problem(MultiLineProblem[int], ABC):
    def __init__(self) -> None:
        self.grid = MutableNumGrid2.from_lines(self.lines[::2], parse_value=parse)
        log.debug_animated(
            self.manifold, lambda _: self.grid.to_lines(format_value=fmt)
        )

    def manifold(self) -> Iterator[None]:
        for y, row in enumerate(self.grid.rows):
            if y == 0:
                continue
            for x, val in enumerate(row):
                above = self.grid[x, y - 1]
                if above <= 0:
                    continue
                if val == -1:
                    self.grid[x - 1, y] += above
                    self.grid[x + 1, y] += above
                else:
                    self.grid[x, y] += above
            yield

    @abstractmethod
    def values(self) -> Iterator[int]: ...

    def solution(self) -> int:
        return sum(self.values())


class Problem1(_Problem):
    test_solution = 21
    puzzle_solution = 1579

    def values(self) -> Iterator[int]:
        for (x, y), v in self.grid.items():
            if v > 0 and self.grid.get((x, y + 1), 0) == -1:
                yield 1


class Problem2(_Problem):
    test_solution = 40
    puzzle_solution = 13418215871354

    def values(self) -> Iterator[int]:
        for v in last(self.grid.rows):
            if v > 0:
                yield v


TEST_INPUT = """
.......S.......
...............
.......^.......
...............
......^.^......
...............
.....^.^.^.....
...............
....^.^...^....
...............
...^.^...^.^...
...............
..^...^.....^..
...............
.^.^.^.^.^...^.
...............
"""
