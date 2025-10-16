from abc import ABC

from more_itertools import last

from aoc import log
from aoc.geo2d import Grid2, manhattan_dist_2
from aoc.problems import GridProblem
from aoc.utils import repeat_transform


class _Problem(GridProblem[int], ABC):
    empty_factor: int

    def __init__(self):
        log.debug(self.grid)

    def solution(self) -> int:
        def expand(grid: Grid2[str]) -> Grid2[str]:
            big_grid, offset = Grid2[str](), 0
            for cx in range(grid.width):
                row = {(y, x + offset): v for (x, y), v in grid.items() if x == cx}
                if "#" in row.values():
                    big_grid |= row
                else:
                    offset += self.empty_factor - 1
            return big_grid
        galaxies = last(repeat_transform(self.grid, expand, times=2)).points_with_value("#")
        return sum(manhattan_dist_2(p, q) for p in galaxies for q in galaxies if p < q)


class Problem1(_Problem):
    test_solution = 374
    my_solution = 9522407

    empty_factor = 2


class Problem2(_Problem):
    test_solution = 82000210  # 10 = 1030, 100 = 8410
    my_solution = 544723432977

    empty_factor = 1_000_000


TEST_INPUT = """
...#......
.......#..
#.........
..........
......#...
.#........
.........#
..........
.......#..
#...#.....
"""
