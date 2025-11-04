from typing import TYPE_CHECKING

from parse import with_pattern  # type: ignore[import-untyped]

from advent_of_code.problems import ParsedProblem
from advent_of_code.utils.geo2d import P2

if TYPE_CHECKING:
    from collections.abc import Iterator


class Knot:
    def __init__(self, tail_size: int) -> None:
        self.pos = 0, 0
        self.tail = Knot(tail_size - 1) if tail_size else None

    def step(self, hx: int, hy: int) -> P2:
        self.pos = hx, hy
        if not self.tail:
            return hx, hy
        return self.tail.wiggle_wiggle(hx, hy)

    def wiggle_wiggle(self, hx: int, hy: int) -> P2:
        tx, ty = self.pos
        if tx < hx - 1:
            return self.step(hx - 1, hy)
        if tx > hx + 1:
            return self.step(hx + 1, hy)
        if ty < hy - 1:
            return self.step(hx, hy - 1)
        if ty > hy + 1:
            return self.step(hx, hy + 1)
        return self.step(tx, ty)


class Head(Knot):
    def move(self, dx: int, dy: int, distance: int) -> Iterator[P2]:
        for _ in range(distance):
            x, y = self.pos
            yield self.step(x + dx, y + dy)


@with_pattern(r"U|D|L|R")
def __parse_dir(s: str) -> P2:
    return {"U": (0, 1), "D": (0, -1), "L": (-1, 0), "R": (1, 0)}[s]


class _Problem(ParsedProblem[tuple[P2, int], int]):
    line_pattern = "{:dir} {:d}"

    tail_size: int

    def solution(self) -> int:
        head = Head(self.tail_size)
        return len(
            {
                position
                for (dx, dy), distance in self.parsed_input
                for position in head.move(dx, dy, distance)
            }
        )


class Problem1(_Problem):
    test_solution = 88
    my_solution = 6190

    tail_size = 1


class Problem2(_Problem):
    test_solution = 36
    my_solution = 2516

    tail_size = 9


TEST_INPUT = """
R 5
U 8
L 8
D 3
R 17
D 10
L 25
U 20
"""
