from abc import ABC
from collections.abc import Iterable, Iterator
from itertools import groupby

from more_itertools import last

from advent_of_code import log
from advent_of_code.problems import StringGridProblem
from advent_of_code.utils.cycle_detection import detect_cycle
from advent_of_code.utils.data import repeat_transform, rotated_cw
from advent_of_code.utils.geo2d import StringGrid2

Line = list[str]
Lines = Iterable[Line]


def debug_grid(lines: Lines) -> None:
    log.lazy_debug(StringGrid2.from_lines(["".join(line) for line in lines]).to_lines)


class _Problem(StringGridProblem[int], ABC):
    def __init__(self) -> None:
        self.cols: Lines = [
            [v for (x, _), v in self.grid.items() if x == c]
            for c in range(self.grid.width)
        ]
        debug_grid(self.cols)


def reordered(col: Line) -> Iterator[str]:
    for k, g in groupby(col, lambda v: v == "#"):
        if k:
            yield from g
        else:
            yield from sorted(g, reverse=True)


def tilt(cols: Lines) -> Lines:
    return rotated_cw(reordered(col) for col in cols)


def load(rows: Lines) -> int:
    return sum(sum(v == "O" for v in row) * i for i, row in enumerate(rows, 1))


class Problem1(_Problem):
    test_solution = 136
    puzzle_solution = 109596

    def solution(self) -> int:
        tilted = list(tilt(self.cols))
        debug_grid(tilted)
        return load(tilted)


def tilt_cycle(c: Lines) -> Lines:
    return list(last(repeat_transform(c, transform=tilt, times=4)))


class Problem2(_Problem):
    test_solution = 64
    puzzle_solution = 96105

    def solution(self) -> int:
        cycle = detect_cycle(repeat_transform(self.cols, transform=tilt_cycle))
        tilt_sequence = repeat_transform(
            self.cols,
            transform=tilt_cycle,
            times=cycle.start + (1_000_000_000 - cycle.start) % cycle.length,
        )
        result = list(rotated_cw(last(tilt_sequence)))
        debug_grid(result)
        log.debug(cycle)
        return load(result)


TEST_INPUT = """
O....#....
O.OO#....#
.....##...
OO.#O....O
.O.....O#.
O.#..O.#.#
..O..#O..O
.......O..
#....###..
#OO..#....
"""
