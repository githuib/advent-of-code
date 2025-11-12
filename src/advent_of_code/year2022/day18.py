from abc import ABC
from enum import IntEnum
from typing import TYPE_CHECKING

from based_utils.cli import human_readable_duration, timed

from advent_of_code import log
from advent_of_code.problems import MultiLineProblem
from advent_of_code.utils.geo3d import P3D, Dir3D, Grid3D, Span3D

if TYPE_CHECKING:
    from collections.abc import Sequence


class Mat(IntEnum):
    LAVA = 0
    AIR = 1


def exposed_sides(cubes: Sequence[P3D]) -> int:
    sides = {side for cube in cubes for side in [cube * 2 + d for d in Dir3D.all]}
    return len(sides) * 2 - len(cubes) * 6


class _Problem(MultiLineProblem[int], ABC):
    def __init__(self) -> None:
        self.lava = [P3D.from_str(line) for line in self.lines]


class Problem1(_Problem):
    test_solution = 64
    puzzle_solution = 4548

    def solution(self) -> int:
        return exposed_sides(self.lava)


def best_solution_str(sol: int, other: int) -> str:
    return f"Runtime solution A: {human_readable_duration(sol)}{' <-- congrats! 🍻' if sol <= other else ''}"


class Problem2(_Problem):
    test_solution = 58
    puzzle_solution = 2588

    def __init__(self) -> None:
        super().__init__()
        self.lava_and_outside = Grid3D(dict.fromkeys(self.lava, Mat.LAVA))
        p1, p2 = self.lava_and_outside.span
        self.span = Span3D(p1 - P3D.unity(), p2 + P3D.unity())

        # locate_outside cubes
        stack: list[P3D] = [p1]
        while stack:
            cube = stack.pop()
            self.lava_and_outside[cube] = Mat.AIR
            for d in Dir3D.all:
                neighbor = cube + d
                if neighbor in self.span and neighbor not in self.lava_and_outside:
                    stack.append(neighbor)

    def solution_a(self) -> int:
        """Approach A: Locate trapped air and subtract the exposed air sides from the exposed lava sides."""
        return exposed_sides(self.lava) - exposed_sides(
            [cube for cube in self.span.points if cube not in self.lava_and_outside]
        )

    def solution_b(self) -> int:
        """Approach B: Count the sides of each cube that border an outside cube."""
        return sum(
            self.lava_and_outside.get(neighbor, 0)
            for cube in self.lava
            for neighbor in (cube + d for d in Dir3D.all)
        )

    def solution(self) -> int:
        solution_a, ta = timed(self.solution_a)
        solution_b, tb = timed(self.solution_b)
        assert solution_a == solution_b
        log.info(best_solution_str(ta, tb))
        log.info(best_solution_str(tb, ta))
        return solution_a


TEST_INPUT = """
2,2,2
1,2,2
3,2,2
2,1,2
2,3,2
2,2,1
2,2,3
2,2,4
2,2,6
1,2,5
3,2,5
2,1,5
2,3,5
"""
