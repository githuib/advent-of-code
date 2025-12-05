from abc import ABC
from math import atan2, pi
from typing import TYPE_CHECKING

from more_itertools import nth

from advent_of_code.problems import CharacterGridProblem, NoSolutionFoundError

if TYPE_CHECKING:
    from collections.abc import Iterator, Set

    from advent_of_code.utils.geo2d import P2


def asteroids_grouped_by_angle(laser: P2, objects: Set[P2]) -> dict[float, list[P2]]:
    lx, ly = laser
    grouped_by_angle: dict[float, list[P2]] = {}
    for ax, ay in objects:
        if (ax, ay) != laser:
            grouped_by_angle.setdefault(
                (atan2(ax - lx, ly - ay) + pi * 2) % (pi * 2), []
            ).append((ax, ay))
    return grouped_by_angle


class _Problem(CharacterGridProblem[int], ABC):
    def __init__(self) -> None:
        objects = self.grid.points_with_value("#")
        self.grouped_by_angle = max(
            (asteroids_grouped_by_angle(laser, objects) for laser in objects), key=len
        )


class Problem1(_Problem):
    test_solution = 210
    puzzle_solution = 299

    def solution(self) -> int:
        return len(self.grouped_by_angle)


class Problem2(_Problem):
    test_solution = 802
    puzzle_solution = 1419

    def solution(self) -> int:
        asteroids = sorted(self.grouped_by_angle.items())

        def shoot_asteroids() -> Iterator[P2]:
            if asteroids:
                for _angle, asteroids_in_beam in asteroids:
                    yield asteroids_in_beam.pop()
                yield from shoot_asteroids()

        asteroid_200 = nth(shoot_asteroids(), 199)
        if asteroid_200 is None:
            raise NoSolutionFoundError
        ax, ay = asteroid_200
        return ax * 100 + ay


# TEST_INPUT = """
# .#..#
# .....
# #####
# ....#
# ...##
# """

TEST_INPUT = """
.#..##.###...#######
##.############..##.
.#.######.########.#
.###.#######.####.#.
#####.##.#.##.###.##
..#####..#.#########
####################
#.####....###.#.#.##
##.#################
#####.##.###..####..
..######..##.#######
####.##.####...##..#
.#####..#.######.###
##...#.##########...
#.##########.#######
.####.#.###.###.#.##
....##.##.###..#####
.#.#.###########.###
#.#.#.#####.####.###
###.##.####.##.#..##
"""
