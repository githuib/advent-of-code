from abc import ABC
from dataclasses import dataclass
from functools import cached_property
from math import lcm
from typing import TYPE_CHECKING, Literal, NamedTuple

from based_utils.algo import AStarState
from yachalk import chalk

from advent_of_code import log
from advent_of_code.problems import StringGridProblem
from advent_of_code.utils.geo2d import DOWN, LEFT, P2, RIGHT, UP, manhattan_dist_2

if TYPE_CHECKING:
    from collections.abc import Iterator

DirectionTile = Literal["^", "v", "<", ">"]

DIRECTION_TILES: list[DirectionTile] = ["^", "v", "<", ">"]
TILES = [*DIRECTION_TILES, "."]
DIRECTIONS: dict[DirectionTile, P2] = {"^": UP, "v": DOWN, "<": LEFT, ">": RIGHT}


@dataclass
class Constants:
    start: P2
    end: P2
    ground: frozenset[P2]
    blizzards: list[set[P2]]

    @cached_property
    def num_valleys(self) -> int:
        return len(self.blizzards)

    def reverse_direction(self) -> None:
        self.start, self.end = self.end, self.start


class Variables(NamedTuple):
    pos: P2 = 1, 0
    cycle: int = 1


class ValleyState(AStarState[Constants, Variables]):
    @property
    def is_end_state(self) -> bool:
        return self.v.pos == self.c.end

    @property
    def next_states(self) -> Iterator[ValleyState]:
        def neighbors() -> Iterator[P2]:
            x, y = self.v.pos
            for dx, dy in DIRECTIONS.values():
                yield x + dx, y + dy
            yield x, y

        blizzards = self.c.blizzards[self.v.cycle % self.c.num_valleys]
        for pos in neighbors():
            if pos in self.c.ground and pos not in blizzards:
                yield self.move(Variables(pos, self.v.cycle + 1))

    @property
    def heuristic(self) -> int:
        return manhattan_dist_2(self.v.pos, self.c.end)

    def __repr__(self) -> str:
        return f"{self.v.pos} - {self.v.cycle}"


class _Problem(StringGridProblem[int], ABC):
    def __init__(self) -> None:
        self.grouped_tiles = {t: self.grid.points_with_value(t) for t in TILES}
        self.ground = frozenset.union(*self.grouped_tiles.values())
        self.size = w, h = self.grid.width - 2, self.grid.height - 2
        start, end = (1, 0), (w, h + 1)
        blizzards = list(self.blizzard_states())
        self.constants = Constants(start, end, self.ground, blizzards)
        self.path = ValleyState.find_path(Variables(), self.constants)

        def grid_str() -> Iterator[str]:
            positions = [s.v.pos for s in self.path.states]

            def format_value(p: P2, v: str) -> str:
                return (
                    chalk.hex("034").bg_hex("bdf")(v)
                    if (p in positions)
                    else chalk.hex("222").bg_hex("888")(v)
                )

            return self.grid.to_lines(format_value=format_value)

        log.lazy_debug(grid_str)

    def new_blizzards(self, t: DirectionTile, bs: frozenset[P2]) -> frozenset[P2]:
        dx, dy = DIRECTIONS[t]
        w, h = self.size
        return frozenset(((x + dx - 1) % w + 1, (y + dy - 1) % h + 1) for (x, y) in bs)

    def blizzard_states(self) -> Iterator[set[P2]]:
        blizzards = {t: self.grouped_tiles[t] for t in DIRECTION_TILES}
        for _ in range(lcm(*self.size)):
            yield {p for pts in blizzards.values() for p in pts}
            blizzards = {t: self.new_blizzards(t, bs) for t, bs in blizzards.items()}


class Problem1(_Problem):
    test_solution = 18
    puzzle_solution = 242

    def solution(self) -> int:
        return self.path.length


class Problem2(_Problem):
    test_solution = 54
    puzzle_solution = 720

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
