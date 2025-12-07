from abc import ABC, abstractmethod
from math import log10
from typing import TYPE_CHECKING

from based_utils.cli import Colored
from based_utils.colors import Color
from more_itertools import last
from more_itertools.recipes import consume

from advent_of_code import log
from advent_of_code.problems import MultiLineProblem
from advent_of_code.utils.geo2d import P2, MutableNumGrid2

if TYPE_CHECKING:
    from collections.abc import Iterator


def parse(s: str) -> int:
    return -1 if s == "^" else 1 if s == "S" else 0


def format_value(_p: P2, v: int, _colored: Colored) -> Colored:
    if v == -1:
        return Colored("^", Color.from_name("indigo", lightness=0.4))
    if v == 0:
        return Colored(".", Color.from_name("blue", lightness=0.2))
    return Colored("|", Color.from_name("pink", lightness=0.2 + log10(v) / 20))


class _Problem(MultiLineProblem[int], ABC):
    def __init__(self) -> None:
        self.grid = MutableNumGrid2.from_lines(self.lines[::2], parse_value=parse)
        consume(
            log.debug_animated_iter(
                self.manifold, lambda _: self.grid.to_lines(format_value=format_value)
            )
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
