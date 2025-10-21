from abc import ABC
from dataclasses import dataclass, field
from math import lcm
from typing import TYPE_CHECKING, NamedTuple

from yachalk import chalk

from advent_of_code import AOC, log
from advent_of_code.geo2d import P2, Dir2, manhattan_dist_2
from advent_of_code.problems import GridProblem
from advent_of_code.search import AStarState

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

@dataclass
class Constants:
    start: P2
    end: P2
    blizzards: list[set[P2]]
    ground: set[P2] = field(init=False)
    num_valleys: int = field(init=False)

    def __post_init__(self) -> None:
        ex, ey = self.end
        self.ground = {self.start} | {(x, y) for x in range(1, ex + 1) for y in range(1, ey)} | {self.end}
        self.num_valleys = len(self.blizzards)

    def reverse_direction(self) -> None:
        self.start, self.end = self.end, self.start


class Variables(NamedTuple):
    pos: P2 = (1, 0)
    cycle: int = 1


class ValleyState(AStarState[Constants, Variables]):
    @property
    def is_finished(self) -> bool:
        return self.v.pos == self.c.end

    @property
    def next_states(self) -> Iterable[ValleyState]:
        def neighbors() -> Iterator[P2]:
            x, y = self.v.pos
            for dx, dy in Dir2.direct_neighbors:
                yield x + dx, y + dy
            yield x, y
        blizzards = self.c.blizzards[self.v.cycle % self.c.num_valleys]
        return [
            self.move(pos=p, cycle=self.v.cycle + 1)
            for p in neighbors()
            if p in self.c.ground and p not in blizzards
        ]

    @property
    def heuristic(self) -> int:
        return manhattan_dist_2(self.v.pos, self.c.end)

    def __repr__(self):
        return f"{self.v.pos} - {self.v.cycle}"


class _Problem(GridProblem[int], ABC):
    def __init__(self):
        w, h = self.grid.width - 2, self.grid.height - 2
        self.constants = Constants((1, 0), (w, h + 1), list(self.blizzard_states(w, h)))
        self.path = ValleyState.find_path(Variables(), self.constants)
        if AOC.debugging:
            log.debug(self.grid.to_str(lambda p, _: (
                chalk.hex("034").bg_hex("bdf")(self.grid[p]) if (
                    p in [s.v.pos for s in self.path.states]
                ) else chalk.hex("222").bg_hex("888")(self.grid[p])
            )))

    def blizzard_states(self, w: int, h: int) -> Iterator[set[P2]]:
        blizzards = [self.grid.points_with_value(c) for c in "^v<>"]
        for _ in range(lcm(w, h)):
            yield {p for pts in blizzards for p in pts}
            blizzards = [{
                ((x + dx - 1) % w + 1, (y + dy - 1) % h + 1)
                for (x, y) in pts
            } for pts, (dx, dy) in zip(blizzards, Dir2.direct_neighbors, strict=False)]


class Problem1(_Problem):
    test_solution = 18
    my_solution = 242

    def solution(self) -> int:
        return self.path.length


class Problem2(_Problem):
    test_solution = 54
    my_solution = 720

    def solution(self) -> int:
        first = self.path.end_state
        self.constants.reverse_direction()
        second = first.find_path_from_current_state().end_state
        self.constants.reverse_direction()
        return second.find_path_from_current_state().length


TEST_INPUT = """
#.######
#>>.<^<#
#.<..<<#
#>v.><>#
#<^v^^>#
######.#
"""
