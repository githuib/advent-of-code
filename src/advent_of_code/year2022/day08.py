from abc import ABC
from math import prod
from typing import TYPE_CHECKING

from advent_of_code.problems import NumGridProblem

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator


class _Problem(NumGridProblem[int], ABC):
    def neighbors(self, x: int, y: int) -> list[Iterator[int]]:
        return [
            (self.grid[x, n] for n in reversed(range(y))),  # west
            (self.grid[x, n] for n in range(y + 1, self.grid.width)),  # east
            (self.grid[n, y] for n in reversed(range(x))),  # north
            (self.grid[n, y] for n in range(x + 1, self.grid.height)),  # south
        ]


class Problem1(_Problem):
    test_solution = 21
    puzzle_solution = 1543

    def solution(self) -> int:
        return sum(
            any(all(t > n for n in trees) for trees in self.neighbors(x, y))
            for (x, y), t in self.grid.items()
        )


def visible_trees(t: int, trees: Iterable[int]) -> int:
    num_visible = 1
    for n in trees:
        if t <= n:
            return num_visible
        num_visible += 1
    return num_visible - 1


class Problem2(_Problem):
    test_solution = 8
    puzzle_solution = 595080

    def solution(self) -> int:
        return max(
            prod(visible_trees(t, trees) for trees in self.neighbors(x, y))
            for (x, y), t in self.grid.items()
        )


TEST_INPUT = """
30373
25512
65332
33549
35390
"""
