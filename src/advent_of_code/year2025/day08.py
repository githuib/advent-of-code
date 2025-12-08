from abc import ABC
from itertools import combinations
from math import prod
from typing import TYPE_CHECKING

from more_itertools import first, last, nth_or_last

from advent_of_code.problems import ParsedProblem
from advent_of_code.utils.geo3d import P3D, dist_3

if TYPE_CHECKING:
    from collections.abc import Iterator


class _Problem(ParsedProblem[tuple[int, int, int], int], ABC):
    line_pattern = "{:d},{:d},{:d}"

    def __init__(self) -> None:
        boxes = [P3D(x, y, z) for x, y, z in self.parsed_input]
        self.distances = sorted(combinations(boxes, 2), key=lambda pair: dist_3(*pair))
        self.circuits = [{b} for b in boxes]

    def connected(self) -> Iterator[tuple[P3D, P3D]]:
        n = len(self.parsed_input)
        for b1, b2 in self.distances:
            c1 = first(c for c in self.circuits if b1 in c)
            c2 = first(c for c in self.circuits if b2 in c)
            if c1 != c2:
                c1.update(c2)
                c2.clear()
            yield b1, b2
            if len(c1) == n:
                return


class Problem1(_Problem):
    test_solution = 40
    puzzle_solution = 96672

    def solution(self) -> int:
        connections = self.var(test=10, puzzle=1000)
        _b1, _b2 = nth_or_last(self.connected(), connections - 1)
        return prod(sorted(len(c) for c in self.circuits)[-3:])


class Problem2(_Problem):
    test_solution = 25272
    puzzle_solution = 22517595

    def solution(self) -> int:
        b1, b2 = last(self.connected())
        return b1.x * b2.x


TEST_INPUT = """
162,817,812
57,618,57
906,360,560
592,479,940
352,342,300
466,668,158
542,29,236
431,825,988
739,650,466
52,470,668
216,146,977
819,987,18
117,168,530
805,96,715
346,949,466
970,615,88
941,993,340
862,61,35
984,92,344
425,690,689
"""
