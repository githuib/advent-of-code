from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from based_utils.cli import Colored
from based_utils.colors import Color
from based_utils.data.iterators import polarized
from more_itertools import first, last

from advent_of_code import log
from advent_of_code.problems import CharacterGridProblem
from advent_of_code.utils.geo2d import P2, MutableNumberGrid2, all_directions

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

type GridItems = Iterable[tuple[P2, int]]
type PolarizedItems = tuple[list[tuple[P2, int]], list[tuple[P2, int]]]


def polarized_values(grid_items: GridItems) -> PolarizedItems:
    return polarized(grid_items, lambda i: i[1] == -1)


class _Problem(CharacterGridProblem[int], ABC):
    def __init__(self) -> None:
        self.num_grid = MutableNumberGrid2(
            (p, 0 if v == "@" else -1) for p, v in self.grid.items()
        )

    def new_value(self, p: P2) -> int:
        _empty, non_empty = polarized_values(self.num_grid.neighbors(p, all_directions))
        v = len(non_empty)
        return v if v >= 4 else -1

    def new_values(self, non_empty: GridItems) -> PolarizedItems:
        new_values = {p: self.new_value(p) for p, _v in non_empty}
        self.num_grid |= new_values
        return polarized_values(new_values.items())

    def _grids(self) -> Iterator[tuple[int, GridItems]]:
        count = 0
        empty, non_empty = polarized_values(self.num_grid.items())
        while len(empty) > 0:
            empty, non_empty = self.new_values(non_empty)
            count += len(empty)
            yield count, empty

    @abstractmethod
    def grids(self) -> Iterator[tuple[int, GridItems]]: ...

    def grid_str(self, args: tuple[int, GridItems]) -> Iterator[str]:
        count, empty = args

        def fmt(p: P2, v: int, _c: Colored) -> Colored:
            if p in [p for p, _v in empty]:
                cx = Color.from_name("pink")
                return Colored("x", cx, cx.contrasting_shade)
            if v == -1:
                return Colored(".", Color.from_name("yellow", lightness=0.4))
            c = Color.from_name("green")
            return Colored(str(v), c.shade(v / 10), c.contrasting_shade)

        yield from self.num_grid.to_lines(format_value=fmt)
        yield ""
        yield f"Counted: {count}"

    def solution(self) -> int:
        count, _empty = last(log.debug_animated_iter(self.grids, self.grid_str))
        return count


class Problem1(_Problem):
    test_solution = 13
    puzzle_solution = 1551

    def grids(self) -> Iterator[tuple[int, GridItems]]:
        yield first(self._grids())


class Problem2(_Problem):
    test_solution = 43
    puzzle_solution = 9784

    def grids(self) -> Iterator[tuple[int, GridItems]]:
        yield from self._grids()


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
