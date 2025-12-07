from abc import ABC
from typing import TYPE_CHECKING, NamedTuple, Self

from based_utils.algo import DijkstraState

from advent_of_code import log
from advent_of_code.problems import NumGridProblem
from advent_of_code.utils.geo2d import DOWN, LEFT, P2, RIGHT, UP, NumGrid2, Range

if TYPE_CHECKING:
    from collections.abc import Iterator


class Constants:
    def __init__(self, grid: NumGrid2, segment_range: Range) -> None:
        self.grid = grid
        self.min_segment, self.max_segment = segment_range
        self.end = grid.width - 1, grid.height - 1


class Variables(NamedTuple):
    pos: P2 = 0, 0
    from_dir: P2 | None = None
    seg_length: int = 0


DIRS: dict[P2 | None, list[P2]] = {
    LEFT: [LEFT, UP, DOWN],
    RIGHT: [RIGHT, UP, DOWN],
    UP: [UP, LEFT, RIGHT],
    DOWN: [DOWN, LEFT, RIGHT],
    None: [UP, DOWN, LEFT, RIGHT],
}


class LavaState(DijkstraState[Constants, Variables]):
    @property
    def is_end_state(self) -> bool:
        return (
            self.v.pos == self.c.end and not 0 < self.v.seg_length < self.c.min_segment
        )

    @property
    def next_states(self) -> Iterator[Self]:
        x, y = self.v.pos
        for dx, dy in DIRS[self.v.from_dir]:
            pos = x + dx, y + dy
            same_dir = (dx, dy) == self.v.from_dir
            new_seg_length = self.v.seg_length + 1 if same_dir else 1
            if (
                (pos in self.c.grid)
                and (new_seg_length <= self.c.max_segment)
                and (same_dir or not 0 < self.v.seg_length < self.c.min_segment)
            ):
                yield self.move(
                    Variables(pos, from_dir=(dx, dy), seg_length=new_seg_length),
                    distance=self.c.grid[pos],
                )


class _Problem(NumGridProblem[int], ABC):
    segment_range: Range

    def solution(self) -> int:
        path = LavaState.find_path(
            Variables(), Constants(self.grid, self.segment_range)
        )
        log.lazy_debug(
            lambda: self.grid.to_lines(highlighted={s.v.pos for s in path.states})
        )
        return path.length


class Problem1(_Problem):
    test_solution = 102
    puzzle_solution = 953

    segment_range = 0, 3


class Problem2(_Problem):
    test_solution = 94
    puzzle_solution = 1180

    segment_range = 4, 10


TEST_INPUT = """
2413432311323
3215453535623
3255245654254
3446585845452
4546657867536
1438598798454
4457876987766
3637877979653
4654967986887
4564679986453
1224686865563
2546548887735
4322674655533
"""
