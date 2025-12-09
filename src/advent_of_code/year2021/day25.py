from collections.abc import Set
from typing import TYPE_CHECKING

from based_utils.cli import Colored, animated
from based_utils.cli.animation import AnimParams, flashing, moving_forward
from based_utils.colors import Colors
from based_utils.data.iterators import first_duplicate

from advent_of_code import log
from advent_of_code.problems import CharGridProblem, MultiLineProblem
from advent_of_code.utils.geo2d import P2, CharGrid2

if TYPE_CHECKING:
    from collections.abc import Iterator

type SeaCucumbers = tuple[Set[P2], Set[P2]]


def board_str(sea_cucumbers: SeaCucumbers) -> Iterator[str]:
    east, south = sea_cucumbers
    board = CharGrid2(
        dict.fromkeys(east, ">") | dict.fromkeys(south, "v"), default_value="."
    )
    colors = {
        ".": Colors.ocean.shade(0.9),
        ">": Colors.pink.shade(0.6).saturated(0.5),
        "v": Colors.purple.shade(0.4).saturated(0.5),
    }

    def format_value(_p: P2, v: str, _colored: Colored) -> Colored:
        c = colors[v]
        return Colored(v, c, c.darker(1.3))

    return board.to_lines(format_value=format_value)


class Problem1(CharGridProblem[int]):
    test_solution = 58
    puzzle_solution = 389

    def sea_cucumbers(self) -> Iterator[SeaCucumbers]:
        sea_cucumbers = (
            self.grid.points_with_value(">"),
            self.grid.points_with_value("v"),
        )
        width, height = self.grid.width, self.grid.height
        while True:
            prev = east, south = sea_cucumbers
            east = frozenset(
                ((x, y) if ((p := ((x + 1) % width, y)) in east or p in south) else p)
                for (x, y) in east
            )
            south = frozenset(
                ((x, y) if ((p := (x, (y + 1) % height)) in east or p in south) else p)
                for (x, y) in south
            )
            sea_cucumbers = east, south
            yield prev

    def solution(self) -> int:
        n, sea_cucumbers = first_duplicate(
            log.debug_animated_iter(
                self.sea_cucumbers, board_str, params=AnimParams(only_every_nth=10)
            )
        )
        log.lazy_debug(lambda: board_str(sea_cucumbers))
        return n


POSEIDON = r"""
        __  |__
      __L L_|L L__
...[+(____________)
       C_________/

"""


class Problem2(MultiLineProblem[None]):
    def solution(self) -> None:
        """Day 25 didn't have a part 2."""
        fg = Colors.poison.shade(0.9)
        bg = Colors.ocean.shade(0.7).saturated(0.9)
        anim = animated(POSEIDON.splitlines(), moving_forward, flashing(fg=fg, bg=bg))
        log.debug_animated(anim, params=AnimParams(fps=10))


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
