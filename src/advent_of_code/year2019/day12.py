from abc import ABC
from collections.abc import Iterable
from copy import deepcopy
from math import lcm

from advent_of_code.geo3d import P3D
from advent_of_code.problems import ParsedProblem
from advent_of_code.utils import compare


class Moon:
    def __init__(self, position: P3D) -> None:
        self.position = position
        self.velocity = P3D()

    def change_velocity(self, other: Moon) -> None:
        x, y, z = self.position
        ox, oy, oz = other.position
        vx, vy, vz = self.velocity
        self.velocity = P3D(
            compare(x, ox) + vx, compare(y, oy) + vy, compare(z, oz) + vz
        )
        # self.velocity = self.velocity + P3D(compare(x, ox), compare(y, oy), compare(z, oz))

    def apply_gravity(self) -> None:
        self.position = self.position + self.velocity

    @property
    def total_energy(self) -> int:
        return self.position.manhattan_length * self.velocity.manhattan_length

    def is_equal_on_axis(self, other: Moon, axis: int) -> bool:
        return (
            self.position[axis] == other.position[axis]
            and self.velocity[axis] == other.velocity[axis]
        )


class _Problem(ParsedProblem[Iterable[int], int], ABC):
    line_pattern = "<x={:d}, y={:d}, z={:d}>"

    def __init__(self) -> None:
        self.moons = [Moon(P3D(*p)) for p in self.parsed_input]

    def simulate_motion(self) -> None:
        for moon in self.moons:
            for other in self.moons:
                if moon != other:
                    moon.change_velocity(other)
        for moon in self.moons:
            moon.apply_gravity()


class Problem1(_Problem):
    test_solution = 1940
    my_solution = 10028

    def solution(self) -> int:
        for _ in range(self.var(test=100, puzzle=1000)):
            self.simulate_motion()
        return sum(moon.total_energy for moon in self.moons)


class Problem2(_Problem):
    test_solution = 4686774924
    my_solution = 314610635824376

    def solution(self) -> int:
        original_moons = deepcopy(self.moons)

        steps_vector = P3D()
        steps = 0
        while not all(steps_vector):
            self.simulate_motion()
            steps += 1
            steps_list = list(steps_vector)
            for axis in range(3):
                if all(
                    moon.is_equal_on_axis(original_moon, axis)
                    for moon, original_moon in zip(
                        self.moons, original_moons, strict=False
                    )
                ):
                    steps_list[axis] = steps
            steps_vector = P3D(*steps_list)

        return lcm(steps_vector.x, steps_vector.y, steps_vector.z)


TEST_INPUT = """
<x=-8, y=-10, z=0>
<x=5, y=5, z=10>
<x=2, y=-7, z=3>
<x=9, y=-8, z=-3>
"""
