from collections.abc import Set
from typing import TYPE_CHECKING, Self

from based_utils.colors import Color

from advent_of_code import log
from advent_of_code.problems import MultiLineProblem, StringGridProblem
from advent_of_code.utils.cli import Colored
from advent_of_code.utils.data import first_duplicate
from advent_of_code.utils.geo2d import P2, StringGrid2

if TYPE_CHECKING:
    from collections.abc import Iterator

SeaCucumbers = tuple[Set[P2], Set[P2]]


def board_str(sea_cucumbers: SeaCucumbers) -> Iterator[str]:
    east, south = sea_cucumbers
    board = StringGrid2(
        dict.fromkeys(east, ">") | dict.fromkeys(south, "v"), default_value="."
    )
    colors = {
        ".": Color.from_name("ocean", lightness=0.9),
        ">": Color.from_name("pink", lightness=0.4, saturation=0.5),
        "v": Color.from_name("purple", lightness=0.22, saturation=0.5),
    }

    def format_value(_p: P2, v: str, _colored: Colored) -> Colored:
        c = colors[v]
        return Colored(v, c, c.with_changed(lightness=0.9))

    return board.to_lines(format_value=format_value)


class Problem1(StringGridProblem[int]):
    test_solution = 58
    puzzle_solution = 389

    def __init__(self) -> None:
        self.width = self.grid.width
        self.height = self.grid.height
        self.sea_cucumbers = (
            self.grid.points_with_value(">"),
            self.grid.points_with_value("v"),
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
        s = """
                                               .
                    __  |__                    .
                  __L L_|L L__                 .
            ...[+(____________)                .
                   C_________/                 .
                                               ."""
        sub = Color.from_name("poison", lightness=0.9)
        ocean = Color.from_name("ocean", lightness=0.7, saturation=0.9)
        log.info(Colored(s, sub, ocean).formatted)


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
