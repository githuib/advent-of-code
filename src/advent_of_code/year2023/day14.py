from abc import ABC
from collections.abc import Iterable
from itertools import groupby

from more_itertools import last

from advent_of_code import log
from advent_of_code.cycle_detection import detect_cycle
from advent_of_code.problems import GridProblem
from advent_of_code.utils import repeat_transform

Lines = Iterable[tuple[str, ...]]


class _Problem(GridProblem[int], ABC):
    def cols(self) -> Lines:
        for c in range(self.grid.width):
            yield tuple(v for (x, _), v in self.grid.items() if x == c)


def tilt(cols: Lines) -> Lines:
    return zip(
        *(
            [
                p
                for part in (
                    g if k else sorted(g)
                    for k, g in groupby(reversed(col), lambda v: v == "#")
                )
                for p in part
            ]
            for col in cols
        ),
        strict=False,
    )


def load(rows: Lines) -> int:
    return sum(sum(v == "O" for v in row) * i for i, row in enumerate(rows, 1))


class Problem1(_Problem):
    test_solution = 136
    my_solution = 109596

    def solution(self) -> int:
        log.debug(self.grid)
        return load(tilt(self.cols()))


def tilt_cycle(c: Lines) -> Lines:
    return last(repeat_transform(c, transform=tilt, times=4))


class Problem2(_Problem):
    test_solution = 64
    my_solution = 96105

    def solution(self) -> int:
        cycle = detect_cycle(
            repeat_transform(self.cols(), transform=lambda c: list(tilt_cycle(c)))
        )
        log.debug(cycle)
        return load(
            reversed(
                list(
                    zip(
                        *last(
                            repeat_transform(
                                self.cols(),
                                transform=tilt_cycle,
                                times=cycle.start
                                + (1_000_000_000 - cycle.start) % cycle.length,
                            )
                        ),
                        strict=False,
                    )
                )
            )
        )


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
