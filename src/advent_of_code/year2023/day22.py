from abc import ABC
from typing import TYPE_CHECKING, Self

from advent_of_code import log
from advent_of_code.problems import ParsedProblem
from advent_of_code.utils.geo3d import P3D

if TYPE_CHECKING:
    from advent_of_code.utils.geo2d import P2


class Brick:
    def __init__(self, p_min: P3D, p_max: P3D) -> None:
        self.p_min, self.p_max = p_min, p_max
        self.connected_bottom, self.connected_top = set[Brick](), set[Brick]()

    def __lt__(self, other: object) -> bool:
        if isinstance(other, Brick):
            return self.p_min.z < other.p_min.z
        return NotImplemented

    def move(self, offset: int) -> None:
        diff = P3D(0, 0, offset)
        self.p_min += diff
        self.p_max += diff

    def supporting(self: Self, foundation: set[Brick] = None) -> set[Brick]:
        return {
            bt
            for bt in self.connected_top
            if bt.connected_bottom.issubset(foundation or {self})
        }

    def total_supporting(self) -> int:
        def total_supporting_rec(bricks: set[Brick], foundation: set[Brick]) -> int:
            supported = {s for b in bricks for s in b.supporting(foundation)}
            if supported:
                return total_supporting_rec(supported, foundation | supported)
            return len(foundation) - 1

        return total_supporting_rec({self}, {self})

    def __repr__(self) -> str:
        return f"{self.p_min} ~ {self.p_max}"


class _Problem(ParsedProblem[tuple[P3D, P3D], int], ABC):
    line_pattern = "{:p3}~{:p3}"

    def __init__(self) -> None:
        self.bricks = sorted(
            [Brick(p_min, p_max + P3D.unity()) for p_min, p_max in self.parsed_input]
        )
        log.debug(self.bricks)
        tops: dict[P2, Brick] = {}
        for brick in self.bricks:
            bricks_below: set[Brick] = {
                b
                for x in range(brick.p_min.x, brick.p_max.x)
                for y in range(brick.p_min.y, brick.p_max.y)
                if (b := tops.get((x, y)))
            }
            max_top = max((b.p_max.z for b in bricks_below), default=1)
            brick.move(max_top - brick.p_min.z)
            for supporting_brick in bricks_below:
                if supporting_brick.p_max.z == max_top:
                    supporting_brick.connected_top.add(brick)
                    brick.connected_bottom.add(supporting_brick)
            for x in range(brick.p_min.x, brick.p_max.x):
                for y in range(brick.p_min.y, brick.p_max.y):
                    tops[x, y] = brick


class Problem1(_Problem):
    test_solution = 5
    puzzle_solution = 409

    def solution(self) -> int:
        return sum(not b.supporting() for b in self.bricks)


class Problem2(_Problem):
    test_solution = 7
    puzzle_solution = 61097

    def solution(self) -> int:
        return sum(b.total_supporting() for b in self.bricks)


TEST_INPUT = """
1,0,1~1,2,1
0,0,2~2,0,2
0,2,3~2,2,3
0,0,4~0,2,4
2,0,5~2,2,5
0,1,6~2,1,6
1,1,8~1,1,9
"""
