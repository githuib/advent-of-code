from abc import ABC
from enum import IntEnum
from itertools import pairwise
from typing import TYPE_CHECKING

from parse import parse  # type: ignore[import-untyped]
from yachalk import chalk

from advent_of_code import log
from advent_of_code.problems import MultiLineProblem
from advent_of_code.utils.data import smart_range
from advent_of_code.utils.geo2d import P2, Grid2

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator


class Material(IntEnum):
    AIR = 0
    ROCK = 1
    SAND = 2
    SOURCE = 3


START = 500, 0


class _Problem(MultiLineProblem[int], ABC):
    def __init__(self) -> None:
        self.map = Grid2.from_points(self.points, Material.ROCK)
        self.map[START] = Material.SOURCE

    @property
    def points(self) -> Iterator[P2]:
        for line in self.lines:
            for (x1, y1), (x2, y2) in pairwise(
                parse("{:d},{:d}", x) for x in line.split(" -> ")
            ):
                for x in smart_range(x1, x2, inclusive=True):
                    for y in smart_range(y1, y2, inclusive=True):
                        yield x, y

    def next_pos(self, x: int, y: int) -> P2:
        for dx in 0, -1, 1:
            if (np := (x + dx, y + 1)) not in self.map:
                return np
        return START

    def go(self, keep_going: Callable[[int, int], bool]) -> None:
        x, y = START
        while keep_going(x, y):
            if (np := self.next_pos(x, y)) == START:
                self.map[x, y] = Material.SAND
            x, y = np

    def map_str(self) -> Iterator[str]:
        sx, _ = START
        return self.map.to_lines(
            lambda _, v: {
                Material.AIR: chalk.hex("111").bg_hex("111")("."),
                Material.ROCK: chalk.hex("654").bg_hex("654")("#"),
                Material.SAND: chalk.hex("fdb").bg_hex("fdb")("o"),
                Material.SOURCE: chalk.hex("0af").bg_hex("0af")("+"),
                None: chalk.hex("0af").bg_hex("faf")("+"),
            }[v],
            min_x=sx - 18,
            max_x=sx + 81,
        )


class Problem1(_Problem):
    test_solution = 24
    my_solution = 964

    def __init__(self) -> None:
        super().__init__()
        self.p_min, self.p_max = self.map.span

    def solution(self) -> int:
        (min_x, _), (max_x, max_y) = self.p_min, self.p_max
        self.go(lambda x, y: min_x <= x <= max_x and y < max_y)
        log.debug(self.map_str)
        return sum(m == Material.SAND for m in self.map.values())


class Problem2(_Problem):
    test_solution = 93
    my_solution = 32041

    def solution(self) -> int:
        y = max(y for (_, y) in self.map) + 2
        sx, _ = START
        for x in range(-y, y + 1):
            self.map[sx + x, y] = Material.ROCK
        self.go(lambda _x, _y: self.map[START] == Material.SOURCE)
        log.debug(self.map_str)
        return sum(m == Material.SAND for m in self.map.values())


TEST_INPUT = """
498,4 -> 498,6 -> 496,6
503,4 -> 502,4 -> 502,9 -> 494,9
"""
