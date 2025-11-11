from abc import ABC
from typing import TYPE_CHECKING

from more_itertools import split_when

from advent_of_code import log
from advent_of_code.problems import MultiLineProblem, NoSolutionFoundError
from advent_of_code.utils.geo2d import DOWN, LEFT, P2, RIGHT, UP, StringGrid2
from advent_of_code.utils.geo3d import P3D, Dir3D, Rotation90deg3D, Trans3

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

DIRECTIONS = [RIGHT, DOWN, LEFT, UP]


class _Problem(MultiLineProblem[int], ABC):
    def __init__(self) -> None:
        self.map_2d = StringGrid2.from_lines(self.lines[:-2])
        log.lazy_debug(self.map_2d.to_lines)
        self.route = [
            (s[0], int("".join(s[1:])))
            for s in split_when("R" + self.lines[-1], lambda _, r: r in "LR")
        ]


class Problem1(_Problem):
    test_solution = 6032
    my_solution = 189140

    def solution(self) -> int:
        walls = self.map_2d.points_with_value("#")
        x, y = (min(x for x, y in self.map_2d if y == 0), 0)
        curr_dir = 3
        for direction, steps in self.route:
            curr_dir = (curr_dir + (1 if direction == "R" else -1)) % 4
            dx, dy = DIRECTIONS[curr_dir]
            for _ in range(steps):
                new_x, new_y = (x + dx), (y + dy)
                if (new_x, new_y) not in self.map_2d:
                    xs = (mx for mx, my in self.map_2d if my == y)
                    ys = (my for mx, my in self.map_2d if mx == x)
                    match curr_dir:
                        case 0:
                            new_x = min(xs)
                        case 1:
                            new_y = min(ys)
                        case 2:
                            new_x = max(xs)
                        case 3:
                            new_y = max(ys)
                if (new_x, new_y) in walls:
                    break
                x, y = new_x, new_y
        return 1000 * (y + 1) + 4 * (x + 1) + curr_dir


class Problem2(_Problem):
    test_solution = 5031
    my_solution = 115063

    def __init__(self) -> None:
        super().__init__()
        self.size = self.var(test=4, puzzle=50)
        self.folding = self.var(
            test=[
                #       u
                # f  f  Fr
                # Ul Ld Dr d
                #       B  Rf
                #
                #          right vec   up vec       outwards
                ((2, 0), (Dir3D.right, Dir3D.up)),  # front
                ((0, 1), (Dir3D.left, Dir3D.front)),  # up
                ((1, 1), (Dir3D.down, Dir3D.front)),  # left
                ((2, 1), (Dir3D.right, Dir3D.front)),  # down
                ((2, 2), (Dir3D.right, Dir3D.down)),  # back
                ((3, 2), (Dir3D.front, Dir3D.down)),  # right
            ],
            puzzle=[
                #   u u
                #   F Rb
                # d Dr
                # L Br
                # Ub
                #          right vec   up vec       outwards
                ((1, 0), (Dir3D.right, Dir3D.up)),  # front
                ((2, 0), (Dir3D.back, Dir3D.up)),  # right
                ((1, 1), (Dir3D.right, Dir3D.front)),  # down
                ((0, 2), (Dir3D.back, Dir3D.down)),  # left
                ((1, 2), (Dir3D.right, Dir3D.down)),  # back
                ((0, 3), (Dir3D.back, Dir3D.left)),  # up
            ],
        )
        f_dict = dict(self.folding)
        self.mapping_3d_to_2d: dict[P3D, P2] = {
            self.map_uv(f_dict, u, v): (u, v) for u, v in self.map_2d
        }

    def map_uv(self, folding: Mapping[P2, tuple[P3D, P3D]], u: int, v: int) -> P3D:
        right, up = folding[u // self.size, v // self.size]
        return P3D(
            *(
                right * (((u % self.size) + 1) * 2 - (self.size + 1))
                - up * (((v % self.size) + 1) * 2 - (self.size + 1))
                + (right ^ up) * self.size
            )
        )

    def walk_route(self) -> tuple[P3D, list[Trans3]]:
        walls_3d: set[P3D] = {
            p3 for p3, p2 in self.mapping_3d_to_2d.items() if self.map_2d[p2] == "#"
        }
        pos = P3D(1 - self.size, 1 - self.size, -self.size)
        transforms = []
        for direction, steps in self.route:
            turn = Rotation90deg3D.z_cw if direction == "L" else Rotation90deg3D.z_ccw
            walls_3d = {wall.transform(turn) for wall in walls_3d}
            pos = pos.transform(turn)
            transforms.append(turn)
            for _ in range(steps):
                x, y, z = pos
                new_y = y - 2
                if new_y < -self.size:
                    if P3D(x, -self.size, 1 - self.size) in walls_3d:
                        break
                    new_y = self.size - 1
                    rotation_to_next_face = Rotation90deg3D.x_ccw
                    walls_3d = {
                        wall.transform(rotation_to_next_face) for wall in walls_3d
                    }
                    transforms.append(rotation_to_next_face)
                elif P3D(x, new_y, z) in walls_3d:
                    break
                pos = P3D(x, new_y, z)
        return pos, transforms

    def find_facing(self, face_coords: P2, transforms: Iterable[Trans3]) -> int:
        facing_map = {Dir3D.left: 0, Dir3D.down: 1, Dir3D.right: 2, Dir3D.up: 3}
        for i in range(6):
            p, (_right, up) = self.folding[i]
            if p == face_coords:
                # Put an "up" (for that face) pointing vector at the final face and
                # see where it's pointing at after all the cube's rotations.
                for turn in transforms:
                    up = up.transform(turn)
                return facing_map[up]
        raise NoSolutionFoundError

    def solution(self) -> int:
        end_pos, transforms = self.walk_route()
        # rotate position back to where it would've been at the beginning
        for turn in reversed(transforms):
            end_pos = end_pos.transform(~turn)
        u, v = self.mapping_3d_to_2d[end_pos]
        facing = self.find_facing((u // self.size, v // self.size), transforms)
        return 1000 * (v + 1) + 4 * (u + 1) + facing


TEST_INPUT = """
        ...#
        .#..
        #...
        ....
...#.......#
........#...
..#....#....
..........#.
        ...#....
        .....#..
        .#......
        ......#.

10R5L5R10L4R5L5
"""
