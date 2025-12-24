from collections.abc import Set
from typing import TYPE_CHECKING

from based_utils.iterators import first_duplicate
from ternimator import AnimParams, animate, animated_lines
from ternimator.animations import flashing, moving_forward

from advent_of_code import C, log
from advent_of_code.problems import CharGridProblem, MultiLineProblem
from advent_of_code.utils import lowlighted
from advent_of_code.utils.geo2d import P2, CharGrid2

if TYPE_CHECKING:
    from collections.abc import Iterator

    from kleur import ColorStr

type SeaCucumbers = tuple[Set[P2], Set[P2]]

COLORS = {
    ".": C.ocean.bright,
    ">": C.pink.slightly_bright.saturated(0.5),
    "v": C.purple.slightly_dark.saturated(0.75),
}


def board_str(sea_cucumbers: SeaCucumbers) -> Iterator[str]:
    east, south = sea_cucumbers
    d = dict.fromkeys(east, ">") | dict.fromkeys(south, "v")
    board = CharGrid2(d, default_value=".")

    def format_value(_p: P2, v: str, _colored: ColorStr) -> ColorStr:
        c = COLORS[v]
        return lowlighted(c)(v)

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
        params = AnimParams(format_item=board_str, only_every_nth=10)
        it = log.debug_animated_iter(self.sea_cucumbers(), params)
        n, sea_cucumbers = first_duplicate(it)
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
        fg, bg = C.poison.very_bright, C.ocean
        anim = animated_lines(POSEIDON, moving_forward(), flashing(fg=fg, bg=bg))
        animate(anim, AnimParams(fps=10, loop=True))


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
