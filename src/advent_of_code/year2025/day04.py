from abc import ABC
from typing import TYPE_CHECKING

from based_utils.cli import Colored
from based_utils.colors import Color
from more_itertools import last

from advent_of_code import log
from advent_of_code.problems import CharacterGridProblem
from advent_of_code.utils.geo2d import (
    P2,
    MutableNumberGrid2,
    NumberGrid2,
    all_directions,
)

if TYPE_CHECKING:
    from collections.abc import Iterator, Set


class _Problem(CharacterGridProblem[int], ABC):
    def __init__(self) -> None:
        self.num_grid = MutableNumberGrid2(
            (p, 0 if v == "@" else -1) for p, v in self.grid.items()
        )

    def step(self) -> Set[P2]:
        ps = set()
        g: dict[P2, int] = {}
        for p, v in self.num_grid.items():
            if v == -1:
                continue
            n = sum(n > -1 for _p, n in self.num_grid.neighbors(p, all_directions))
            if n < 4:
                ps.add(p)
                n = -1
            g[p] = n
        for p, v in g.items():
            self.num_grid[p] = v
        return ps


def grid_str(args: tuple[int, NumberGrid2, Set[P2]]) -> Iterator[str]:
    count, grid, ps = args

    def fmt(p: P2, v: int, _c: Colored) -> Colored:
        if p in ps:
            cx = Color.from_name("pink")
            return Colored("x", cx, cx.contrasting_shade)
        if v == -1:
            return Colored(".", Color.from_name("blue", lightness=0.25))
        c = Color.from_name("green")
        return Colored(str(v), c.shade(v / 10), c.contrasting_shade)

    yield from grid.to_lines(format_value=fmt)
    yield ""
    yield f"Counted: {count}"


class Problem1(_Problem):
    test_solution = 13
    puzzle_solution = 1551

    def solution(self) -> int:
        ps = self.step()
        n = len(ps)
        log.lazy_debug(lambda: grid_str((n, self.num_grid, ps)))
        return n


class Problem2(_Problem):
    test_solution = 43
    puzzle_solution = 9784

    def grids(self) -> Iterator[tuple[int, NumberGrid2, Set[P2]]]:
        count = 0
        ps: Set[P2] | None = None
        while ps is None or len(ps) > 0:
            ps = self.step()
            count += len(ps)
            yield count, self.num_grid, ps

    def solution(self) -> int:
        it = log.debug_animated_iter(self.grids, grid_str)
        count, _grid, _ps = last(it)
        return count


TEST_INPUT = """
..@@.@@@@.
@@@.@.@.@@
@@@@@.@.@@
@.@@@@..@.
@@.@@@@.@@
.@@@@@@@.@
.@.@.@.@@@
@.@@@.@@@@
.@@@@@@@@.
@.@.@@@.@.
"""
