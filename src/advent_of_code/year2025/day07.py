from abc import ABC

from more_itertools import last

from advent_of_code import log
from advent_of_code.problems import MultiLineProblem
from advent_of_code.utils.geo2d import MutableNumberGrid2


def parse(s: str) -> int:
    return -1 if s == "^" else 1 if s == "S" else 0


class _Problem(MultiLineProblem[int], ABC):
    def __init__(self) -> None:
        self.grid = MutableNumberGrid2.from_lines(self.lines[::2], parse_value=parse)
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
        log.debug(self.grid.to_lines())


class Problem1(_Problem):
    test_solution = 21
    puzzle_solution = 1579

    def solution(self) -> int:
        return sum(
            v > 0 and self.grid.get((x, y + 1), 0) == -1
            for (x, y), v in self.grid.items()
        )


class Problem2(_Problem):
    test_solution = 40
    puzzle_solution = 13418215871354

    def solution(self) -> int:
        return sum(n for n in last(self.grid.rows) if n > -1)


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
