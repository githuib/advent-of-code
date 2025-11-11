from abc import ABC
from typing import TYPE_CHECKING

from more_itertools import split_at

from advent_of_code.problems import MultiLineProblem, NoSolutionFoundError
from advent_of_code.utils.geo2d import StringGrid2

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence


class _Problem(MultiLineProblem[int], ABC):
    fix_smudge: bool

    def cols_rows(self) -> Iterator[tuple[list[str], list[str]]]:
        for lines in split_at(self.lines, lambda line: line == ""):
            grid = StringGrid2.from_lines(
                lines, parse_callback=lambda c: str(".#".index(c))
            )
            yield (
                [
                    "".join(v for (x, _), v in grid.items() if x == c)
                    for c in range(grid.width)
                ],
                [
                    "".join(v for (_, y), v in grid.items() if y == r)
                    for r in range(grid.height)
                ],
            )

    def find_reflection(self, lines: Sequence[str]) -> int | None:
        for r in range(1, len(lines)):
            n = min(r, len(lines) - r)
            a = int("".join(reversed(lines[r - n : r])), 2)
            b = int("".join(lines[r : r + n]), 2)
            if (a ^ b).bit_count() == int(self.fix_smudge):
                return r
        return None

    def mirror_value(self, cols: Sequence[str], rows: Sequence[str]) -> int:
        c = self.find_reflection(cols)
        if c is not None:
            return c
        r = self.find_reflection(rows)
        if r is not None:
            return r * 100
        raise NoSolutionFoundError

    def solution(self) -> int:
        return sum(self.mirror_value(cols, rows) for cols, rows in self.cols_rows())


class Problem1(_Problem):
    test_solution = 405
    puzzle_solution = 35232

    fix_smudge = False


class Problem2(_Problem):
    test_solution = 400
    puzzle_solution = 37982

    fix_smudge = True


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
