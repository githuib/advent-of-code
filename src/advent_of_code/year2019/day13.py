from enum import IntEnum
from itertools import batched
from typing import TYPE_CHECKING

from based_utils.calx import compare
from more_itertools import last

from advent_of_code import log
from advent_of_code.utils.cli import center
from advent_of_code.utils.geo2d import MutableStringGrid2

from .intcode import IntcodeProblem

if TYPE_CHECKING:
    from collections.abc import Iterator


class Tile(IntEnum):
    EMPTY = 0
    WALL = 1
    BLOCK = 2
    PADDLE = 3
    BALL = 4


class Problem1(IntcodeProblem[int]):
    test_solution = None
    puzzle_solution = 333

    def solution(self) -> int:
        return list(self.computer.run_to_next_output())[2::3].count(Tile.BLOCK)


class Problem2(Problem1):
    test_solution = None
    puzzle_solution = 16539

    def grids(self) -> Iterator[tuple[Iterator[str], int]]:
        self.computer.program[0] = 2
        score, paddle_x = 0, None
        grid = MutableStringGrid2()
        for x, y, value in batched(self.computer.run_to_next_output(), 3, strict=True):
            if (x, y) == (-1, 0):
                score = value
                yield grid.to_lines(), score
                continue
            if value == Tile.PADDLE:
                paddle_x = x
                for i in range(1, 43):
                    grid[i, y] = "^" if abs(i - x) <= 2 else " "
            else:
                grid[x, y] = " .#^@"[value]
            if value == Tile.BALL:
                self.computer.inputs.append(compare(paddle_x or x, x))

    def solution(self) -> int:
        def fmt(item: tuple[Iterator[str], int]) -> Iterator[str]:
            lines, score = item
            yield " "
            yield from lines
            yield center(f"Score: {score:05d}", 44)

        _grid, final_score = last(log.debug_animated_iter(self.grids(), fmt))
        return final_score


TEST_INPUT = """

"""
