from abc import ABC
from typing import TYPE_CHECKING

from more_itertools import split_at

from aoc.geo2d import Grid2
from aoc.problems import MultiLineProblem, NoSolutionFoundError

if TYPE_CHECKING:
    from collections.abc import Iterator


class _Problem(MultiLineProblem[int], ABC):
    def cols_rows(self) -> Iterator[tuple[list[str], list[str]]]:
        for lines in split_at(self.lines, lambda line: line == ""):
            grid = Grid2.from_lines(lines).converted(lambda c: str(".#".index(c)))
            yield (
                ["".join(v for (x, _), v in grid.items() if x == c) for c in range(grid.width)],
                ["".join(v for (_, y), v in grid.items() if y == r) for r in range(grid.height)],
            )


def find_reflection(lines: list[str], fix_smudge: bool) -> int | None:
    for r in range(1, len(lines)):
        n = min(r, len(lines) - r)
        a = int("".join(reversed(lines[r-n:r])), 2)
        b = int("".join(lines[r:r+n]), 2)
        if (a ^ b).bit_count() == int(fix_smudge):
            return r
    return None


def mirror_value(cols: list[str], rows: list[str], fix_smudge: bool) -> int:
    c = find_reflection(cols, fix_smudge)
    if c is not None:
        return c
    r = find_reflection(rows, fix_smudge)
    if r is not None:
        return r * 100
    raise NoSolutionFoundError


class Problem1(_Problem):
    test_solution = 405
    my_solution = 35232

    def solution(self) -> int:
        return sum(mirror_value(cols, rows, fix_smudge=False) for cols, rows in self.cols_rows())


class Problem2(_Problem):
    test_solution = 400
    my_solution = 37982

    def solution(self) -> int:
        return sum(mirror_value(cols, rows, fix_smudge=True) for cols, rows in self.cols_rows())


TEST_INPUT = """
#.##..##.
..#.##.#.
##......#
##......#
..#.##.#.
..##..##.
#.#.##.#.

#...##..#
#....#..#
..##..###
#####.##.
#####.##.
..##..###
#....#..#
"""
