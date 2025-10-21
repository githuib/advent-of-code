from abc import ABC
from typing import TYPE_CHECKING

from parse import parse  # type: ignore[import-untyped]

from advent_of_code.problems import OneLineProblem

if TYPE_CHECKING:
    from advent_of_code.geo2d import P2


def shoot(
    x_range: tuple[int, int],
    y_range: tuple[int, int],
    v: tuple[int, int],
) -> int | None:
    min_x, max_x = x_range
    min_y, max_y = y_range
    vx, vy = v
    x, y = 0, 0
    highest_y = y
    while x <= max_x and min_y <= y:
        x += vx
        y += vy
        if vy > 0:
            highest_y = y
        if min_x <= x <= max_x and min_y <= y <= max_y:
            # hit me baby, one more time!
            return highest_y
        vx = max(vx - 1, 0)
        vy -= 1
    # epic miss
    return None


class _Problem(OneLineProblem[int], ABC):
    def shoot_that_mofo(self) -> dict[P2, int]:
        min_x, max_x, min_y, max_y = parse(
            "target area: x={:d}..{:d}, y={:d}..{:d}", self.line
        )
        return {
            (vx, vy): highest_y
            for vx in range(max_x + 1)
            for vy in range(min_y, 1000)
            if (highest_y := shoot((min_x, max_x), (min_y, max_y), (vx, vy)))
            is not None
        }


class Problem1(_Problem):
    test_solution = 45
    my_solution = 5151

    def solution(self) -> int:
        return max(self.shoot_that_mofo().values())


class Problem2(_Problem):
    test_solution = 112
    my_solution = 968

    def solution(self) -> int:
        return len(self.shoot_that_mofo())


TEST_INPUT = "target area: x=20..30, y=-10..-5"
