from typing import NamedTuple

from advent_of_code.geo2d import P2, Grid2
from advent_of_code.problems import NumberGridProblem
from advent_of_code.search import DijkstraState
from advent_of_code.utils import mods


class Constants:
    def __init__(self, cave: Grid2[int]):
        self.cave = cave
        _, self.end_position = cave.span


class Variables(NamedTuple):
    position: P2 = 0, 0


class ChitonState(DijkstraState[Constants, Variables]):
    @property
    def is_finished(self) -> bool:
        return self.v.position == self.c.end_position

    @property
    def next_states(self) -> list[ChitonState]:
        return [
            self.move(distance=dist, position=pos)
            for pos, dist in self.c.cave.neighbors(self.v.position)
        ]


class Problem1(NumberGridProblem[int]):
    test_solution = 40
    my_solution = 583

    def solution(self) -> int:
        return ChitonState.find_path(Variables(), Constants(self.grid)).length


class Problem2(Problem1):
    test_solution = 315
    my_solution = 2927

    def solution(self) -> int:
        w, h = self.grid.size
        path = ChitonState.find_path(
            Variables(),
            Constants(
                Grid2[int](
                    {
                        (x + w * i, y + h * j): mods(risk + i + j, 9, 1)
                        for i in range(5)
                        for j in range(5)
                        for (x, y), risk in self.grid.items()
                    }
                )
            ),
        )
        # path_points: set[P2] = {s.position for s in path.states}
        # print(cave.to_str(lambda p: pixel(p in path_points)))
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
