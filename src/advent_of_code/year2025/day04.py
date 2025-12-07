from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from based_utils.cli import Colored
from based_utils.colors import Color
from based_utils.data.iterators import polarized

from advent_of_code import log
from advent_of_code.problems import CharacterGridProblem
from advent_of_code.utils.geo2d import P2, Crop, MutableNumberGrid2, all_directions

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

type Rolls = list[tuple[P2, int]]


def remove_rolls(grid_items: Iterable[tuple[P2, int]]) -> tuple[Rolls, Rolls]:
    return polarized(grid_items, lambda i: i[1] == -1)


class _Problem(CharacterGridProblem[int], ABC):
    def __init__(self) -> None:
        self.num_grid = MutableNumberGrid2(
            (p, 0 if v == "@" else -1) for p, v in self.grid.items()
        )

    def availability(self, p: P2) -> int:
        _removed, blocked = remove_rolls(self.num_grid.neighbors(p, all_directions))
        v = len(blocked)
        return v if v >= 4 else -1

    def _removed(self) -> Iterator[Rolls]:
        removed, blocked = remove_rolls(self.num_grid.items())
        while removed:
            availabilities = {p: self.availability(p) for p, _v in blocked}
            self.num_grid |= availabilities
            removed, blocked = remove_rolls(availabilities.items())
            yield removed

    @abstractmethod
    def removed(self) -> Iterator[Rolls]: ...

    def grid_str(self, removed: Rolls) -> Iterator[str]:
        def fmt(p: P2, v: int, _c: Colored) -> Colored:
            if p in [p for p, _v in removed]:
                cx = Color.from_name("pink")
                return Colored("x", cx, cx.contrasting_shade)
            if v == -1:
                return Colored(".", Color.from_name("yellow", lightness=0.4))
            c = Color.from_name("green")
            return Colored(str(v), c.shade(v / 10), c.contrasting_shade)

        yield from self.num_grid.to_lines(format_value=fmt, crop=Crop(bottom=2))
        yield ""
        yield f"Removed: {len(list(removed))}"

    def solution(self) -> int:
        return sum(len(r) for r in log.debug_animated_iter(self.removed, self.grid_str))


class Problem1(_Problem):
    test_solution = 13
    puzzle_solution = 1551

    def removed(self) -> Iterator[Rolls]:
        yield next(self._removed())


class Problem2(_Problem):
    test_solution = 43
    puzzle_solution = 9784

    def removed(self) -> Iterator[Rolls]:
        yield from self._removed()

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
