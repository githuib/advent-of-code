from collections.abc import Set
from contextlib import suppress
from typing import TYPE_CHECKING

from based_utils.cli import Colored, Lines, animated
from based_utils.cli.animation import AnimationParams, moving_forward
from based_utils.colors import Color
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
        ".": Color.from_name("ocean", lightness=0.9),
        ">": Color.from_name("pink", lightness=0.6, saturation=0.5),
        "v": Color.from_name("purple", lightness=0.4, saturation=0.5),
    }

    def format_value(_p: P2, v: str, _colored: Colored) -> Colored:
        c = colors[v]
        return Colored(v, c, c.with_changed(lightness=0.75))

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
                self.sea_cucumbers, board_str, params=AnimationParams(only_every_nth=10)
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
SUB_COLOR = Color.from_name("poison", lightness=0.9)
OCEAN_COLOR = Color.from_name("ocean", lightness=0.7, saturation=0.9)


class Problem2(MultiLineProblem[None]):
    def solution(self) -> None:
        """Day 25 didn't have a part 2."""

        def fmt(lines: Lines) -> Iterator[str]:
            for line in lines:
                yield Colored(line, SUB_COLOR, OCEAN_COLOR).formatted

        with suppress(KeyboardInterrupt):
            log.debug_animated(
                animated(POSEIDON.splitlines(), moving_forward),
                format_item=fmt,
                params=AnimationParams(fps=10),
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
