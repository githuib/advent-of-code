from abc import ABC
from enum import IntEnum

from advent_of_code import log
from advent_of_code.geo3d import P3D, Dir3D, Grid3D, Span3D
from advent_of_code.problems import MultiLineProblem
from advent_of_code.utils import timed


class Mat(IntEnum):
    LAVA = 0
    AIR = 1


def exposed_sides(cubes: list[P3D]) -> int:
    sides = {side for cube in cubes for side in [cube * 2 + d for d in Dir3D.all]}
    return len(sides) * 2 - len(cubes) * 6


class _Problem(MultiLineProblem[int], ABC):
    def __init__(self):
        self.lava = [P3D.from_str(line) for line in self.lines]


class Problem1(_Problem):
    test_solution = 64
    my_solution = 4548

    def solution(self) -> int:
        return exposed_sides(self.lava)


class Problem2(_Problem):
    test_solution = 58
    my_solution = 2588

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
        """
        Approach A: Locate trapped air and subtract the
        exposed air sides from the exposed lava sides.
        """
        return exposed_sides(self.lava) - exposed_sides(
            [cube for cube in self.span.points if cube not in self.lava_and_outside]
        )

    def solution_b(self) -> int:
        """
        Approach B: Count the sides of each cube that border an outside cube.
        """
        return sum(
            self.lava_and_outside.get(neighbor, 0)
            for cube in self.lava
            for neighbor in (cube + d for d in Dir3D.all)
        )

    def solution(self) -> int:
        solution_a, ta, ta_str = timed(self.solution_a)
        solution_b, tb, tb_str = timed(self.solution_b)
        assert solution_a == solution_b
        log.info(
            "Runtime solution A: %s %s", ta_str, "<-- congrats!" if ta <= tb else ""
        )
        log.info(
            "Runtime solution B: %s %s", tb_str, "<-- congrats!" if tb <= ta else ""
        )
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
