from collections.abc import Set
from typing import TYPE_CHECKING, Self

from yachalk import chalk

from advent_of_code import log
from advent_of_code.problems import GridProblem, MultiLineProblem
from advent_of_code.utils.data import first_duplicate
from advent_of_code.utils.geo2d import P2, Grid2

if TYPE_CHECKING:
    from collections.abc import Iterator

SeaCucumbers = tuple[Set[P2], Set[P2]]


def board_str(sea_cucumbers: SeaCucumbers) -> Iterator[str]:
    east, south = sea_cucumbers
    board = Grid2[str](dict.fromkeys(east, ">") | dict.fromkeys(south, "v"))
    return board.to_lines(
        lambda _, v: {
            None: chalk.hex("0af").bg_hex("0af")("."),
            ">": chalk.hex("888").bg_hex("888")(">"),
            "v": chalk.hex("666").bg_hex("666")("v"),
        }[v]
    )


class Problem1(GridProblem[int]):
    test_solution = 58
    my_solution = 389

    def __init__(self) -> None:
        self.width = self.grid.width
        self.height = self.grid.height
        self.sea_cucumbers = (
            self.grid.points_with_values(">"),
            self.grid.points_with_values("v"),
        )

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> SeaCucumbers:
        prev = east, south = self.sea_cucumbers
        east = frozenset(
            ((x, y) if ((p := ((x + 1) % self.width, y)) in east or p in south) else p)
            for (x, y) in east
        )
        south = frozenset(
            ((x, y) if ((p := (x, (y + 1) % self.height)) in east or p in south) else p)
            for (x, y) in south
        )
        self.sea_cucumbers = east, south
        return prev

    def solution(self) -> int:
        log.lazy_debug(lambda: board_str(self.sea_cucumbers))
        n, sea_cucumbers = first_duplicate(self)
        log.lazy_debug(lambda: board_str(sea_cucumbers))
        return n


class Problem2(MultiLineProblem[None]):
    def solution(self) -> None:
        """Day 25 didn't have a part 2."""
        log.info(
            chalk.bg_hex("0df").hex("df0")("""
                                               .
                    __  |__                    .
                  __L L_|L L__                 .
            ...[+(____________)                .
                   C_________/                 .
                                               .""")
        )


TEST_INPUT = """
v...>>.vv>
.vv>>.vv..
>>.>v>...v
>>v>>.>.v.
v>v.vv.v..
>.>>..v...
.vv..>.>v.
v.v..>>v.v
....v..v.>
"""
