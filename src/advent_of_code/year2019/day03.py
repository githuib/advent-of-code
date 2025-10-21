from abc import ABC
from typing import TYPE_CHECKING

from advent_of_code.geo2d import P2, Dir2
from advent_of_code.problems import MultiLineProblem

if TYPE_CHECKING:
    from collections.abc import Iterator

DIRECTIONS = dict(zip("UDLR", Dir2.direct_neighbors, strict=False))


class _Problem(MultiLineProblem[int], ABC):
    def __init__(self):
        def parsed_lines() -> Iterator[dict[P2, int]]:
            for line in self.lines:
                x, y = 0, 0
                path: dict[P2, int] = {}
                steps = 0

                for wire_str in line.split(","):
                    dx, dy = DIRECTIONS[wire_str[0]]
                    length = int(wire_str[1:])
                    sub_path = [
                        ((x + dx * i, y + dy * i), steps + i)
                        for i in range(1, length + 1)
                    ]
                    (x, y), _ = sub_path[-1]
                    path = {**dict(sub_path), **path}
                    steps += length

                yield path

        path1, path2 = parsed_lines()
        self.intersection = {
            p: path1[p] + path2[p] for p in path1.keys() & path2.keys()
        }


class Problem1(_Problem):
    test_solution = None
    my_solution = 5319

    with_steps = True

    def solution(self) -> int:
        return min(abs(x) + abs(y) for x, y in self.intersection)


class Problem2(_Problem):
    test_solution = None
    my_solution = 122514

    with_steps = True

    def solution(self) -> int:
        return min(self.intersection.values())


TEST_INPUT = """

"""
