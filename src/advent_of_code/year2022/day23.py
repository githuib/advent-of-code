from abc import ABC
from collections import defaultdict
from itertools import count
from typing import TYPE_CHECKING

from more_itertools import nth_or_last

from advent_of_code import log
from advent_of_code.geo2d import P2, Dir2, Grid2
from advent_of_code.problems import GridProblem
from advent_of_code.utils import first_duplicate

if TYPE_CHECKING:
    from collections.abc import Iterator

DIRECTIONS = [
    (Dir2.up, {Dir2.up, Dir2.left_up, Dir2.right_up}),
    (Dir2.down, {Dir2.down, Dir2.left_down, Dir2.right_down}),
    (Dir2.left, {Dir2.left, Dir2.left_up, Dir2.left_down}),
    (Dir2.right, {Dir2.right, Dir2.right_up, Dir2.right_down}),
]


def next_pos(x: int, y: int, step: int, occupied: set[P2]) -> P2 | None:
    for i in range(step, 4 + step):
        (dx, dy), dirs = DIRECTIONS[i % 4]
        if all(
            (x + nx, y + ny) not in occupied for nx, ny in dirs
        ) and any(
            (x + nx, y + ny) in occupied for nx, ny in Dir2.all_neighbors
        ):
            return x + dx, y + dy
    return None


class _Problem(GridProblem[int], ABC):
    def dance(self) -> Iterator[set[P2]]:
        occupied = {p for p, v in self.grid.items() if v == "#"}
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
            occupied = set(elfs.values())


class Problem1(_Problem):
    test_solution = 110
    my_solution = 3788

    def solution(self) -> int:
        log.debug(self.grid)
        log.debug(" ")
        elfs = Grid2(nth_or_last(self.dance(), 10), default=1)
        log.debug(elfs)
        return elfs.area - len(elfs)


class Problem2(_Problem):
    test_solution = 20
    my_solution = 921

    def solution(self) -> int:
        log.debug(self.grid)
        log.debug(" ")
        n, elfs = first_duplicate(self.dance())
        log.debug(Grid2(elfs, default=1))
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
