from typing import TYPE_CHECKING, NamedTuple

from based_utils.algo import DijkstraState
from based_utils.math import mods

from advent_of_code import log
from advent_of_code.problems import NumGridProblem
from advent_of_code.utils.geo2d import P2, NumGrid2

if TYPE_CHECKING:
    from collections.abc import Iterator


class Constants:
    def __init__(self, cave: NumGrid2) -> None:
        self.cave = cave
        _, self.end_position = cave.span


class Variables(NamedTuple):
    position: P2 = 0, 0


class ChitonState(DijkstraState[Constants, Variables]):
    @property
    def is_end_state(self) -> bool:
        return self.v.position == self.c.end_position

    @property
    def next_states(self) -> Iterator[ChitonState]:
        for pos, dist in self.c.cave.neighbors(self.v.position):
            yield self.move(Variables(pos), distance=dist)


class Problem1(NumGridProblem[int]):
    test_solution = 40
    puzzle_solution = 583

    def solution(self) -> int:
        path = ChitonState.find_path(Variables(), Constants(self.grid))
        log.lazy_debug(
            lambda: self.grid.to_lines(highlighted={s.v.position for s in path.states})
        )
        return path.length


class Problem2(Problem1):
    test_solution = 315
    puzzle_solution = 2927

    def solution(self) -> int:
        w, h = self.grid.size
        grid = NumGrid2(
            {
                (x + w * i, y + h * j): mods(risk + i + j, 9, 1)
                for i in range(5)
                for j in range(5)
                for (x, y), risk in self.grid.items()
            }
        )
        path = ChitonState.find_path(Variables(), Constants(grid))
        log.lazy_debug(
            lambda: grid.to_lines(highlighted={s.v.position for s in path.states})
        )
        return path.length


TEST_INPUT = """
1163751742
1381373672
2136511328
3694931569
7463417111
1319128137
1359912421
3125421639
1293138521
2311944581
"""
