from abc import ABC

from based_utils.data.iterators import repeat_transform
from more_itertools import last

from advent_of_code import log
from advent_of_code.problems import CharGridProblem
from advent_of_code.utils.geo2d import CharGrid2, MutableCharGrid2, manhattan_dist_2


class _Problem(CharGridProblem[int], ABC):
    empty_factor: int

    def __init__(self) -> None:
        log.lazy_debug(self.grid.to_lines)

    def solution(self) -> int:
        def expand(grid: CharGrid2) -> CharGrid2:
            big_grid, offset = MutableCharGrid2(), 0
            for cx in range(grid.width):
                row = {(y, x + offset): v for (x, y), v in grid.items() if x == cx}
                if "#" in row.values():
                    big_grid |= row
                else:
                    offset += self.empty_factor - 1
            return big_grid

        galaxies = last(
            repeat_transform(self.grid, transform=expand, times=2)
        ).points_with_value("#")
        return sum(manhattan_dist_2(p, q) for p in galaxies for q in galaxies if p < q)


class Problem1(_Problem):
    test_solution = 374
    puzzle_solution = 9522407

    empty_factor = 2


class Problem2(_Problem):
    test_solution = 82000210  # 10 = 1030, 100 = 8410
    puzzle_solution = 544723432977

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
