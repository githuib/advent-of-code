from abc import ABC
from collections import defaultdict
from itertools import count
from typing import TYPE_CHECKING

from based_utils.data.iterators import first_duplicate
from more_itertools import nth_or_last

from advent_of_code import log
from advent_of_code.problems import StringGridProblem
from advent_of_code.utils.geo2d import (
    DOWN,
    LEFT,
    LEFT_DOWN,
    LEFT_UP,
    P2,
    RIGHT,
    RIGHT_DOWN,
    RIGHT_UP,
    UP,
    NumberGrid2,
    all_directions,
)

if TYPE_CHECKING:
    from collections.abc import Iterator, Set

DIRECTIONS = [
    (UP, {UP, LEFT_UP, RIGHT_UP}),
    (DOWN, {DOWN, LEFT_DOWN, RIGHT_DOWN}),
    (LEFT, {LEFT, LEFT_UP, LEFT_DOWN}),
    (RIGHT, {RIGHT, RIGHT_UP, RIGHT_DOWN}),
]


def next_pos(x: int, y: int, step: int, occupied: Set[P2]) -> P2 | None:
    for i in range(step, 4 + step):
        (dx, dy), dirs = DIRECTIONS[i % 4]
        if all((x + nx, y + ny) not in occupied for nx, ny in dirs) and any(
            (x + nx, y + ny) in occupied for nx, ny in all_directions
        ):
            return x + dx, y + dy
    return None


class _Problem(StringGridProblem[int], ABC):
    def __init__(self) -> None:
        log.lazy_debug(self.grid.to_lines)

    def dance(self) -> Iterator[frozenset[P2]]:
        occupied = frozenset(p for p, v in self.grid.items() if v == "#")
        elfs: dict[int, P2] = dict(enumerate(occupied, 1))
        for step in count():
            yield occupied
            proposal = defaultdict(list)
            for elf, (x, y) in elfs.items():
                if pos := next_pos(x, y, step, occupied):
                    proposal[pos].append(elf)
            for p, proposing_elfs in proposal.items():
                if len(proposing_elfs) == 1:
                    elfs[proposing_elfs[0]] = p
            occupied = frozenset(elfs.values())


class Problem1(_Problem):
    test_solution = 110
    puzzle_solution = 3788

    def solution(self) -> int:
        elfs = NumberGrid2(dict.fromkeys(nth_or_last(self.dance(), 10), 1))
        log.lazy_debug(elfs.to_lines)
        return elfs.area - len(elfs)


class Problem2(_Problem):
    test_solution = 20
    puzzle_solution = 921

    def solution(self) -> int:
        n, elfs = first_duplicate(self.dance())
        log.lazy_debug(NumberGrid2(dict.fromkeys(elfs, 1)).to_lines)
        return n


TEST_INPUT = """
....#..
..###.#
#...#.#
.#...##
#.###..
##.#.##
.#..#..
"""
