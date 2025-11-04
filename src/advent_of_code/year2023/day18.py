from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from advent_of_code.geo2d import DOWN, LEFT, P2, RIGHT, UP, grid_area
from advent_of_code.problems import MultiLineProblem

if TYPE_CHECKING:
    from collections.abc import Iterator

DIRS = [RIGHT, DOWN, LEFT, UP]


class _Problem(MultiLineProblem[int], ABC):
    @abstractmethod
    def parsed(self) -> Iterator[tuple[P2, int]]:
        pass

    def loop(self) -> Iterator[P2]:
        x, y = 0, 0
        for (dx, dy), dist in self.parsed():
            x += dx * dist
            y += dy * dist
            yield x, y

    def solution(self) -> int:
        return grid_area(self.loop())


class Problem1(_Problem):
    test_solution = 62
    my_solution = 62365

    def parsed(self) -> Iterator[tuple[P2, int]]:
        dirs = dict(zip("RDLU", DIRS, strict=False))
        for line in self.lines:
            d_str, dist_str, _ = line.split()
            yield dirs[d_str], int(dist_str)


class Problem2(_Problem):
    test_solution = 952408144115
    my_solution = 159485361249806

    def parsed(self) -> Iterator[tuple[P2, int]]:
        for line in self.lines:
            yield DIRS[int(line[-2])], int(line[-7:-2], 16)


TEST_INPUT = """
R 6 (#70c710)
D 5 (#0dc571)
L 2 (#5713f0)
D 2 (#d2c081)
R 2 (#59c680)
D 2 (#411b91)
L 5 (#8ceee2)
U 2 (#caa173)
L 1 (#1b58a2)
U 2 (#caa171)
R 2 (#7807d2)
U 3 (#a77fa3)
L 2 (#015232)
U 2 (#7a21e3)
"""
