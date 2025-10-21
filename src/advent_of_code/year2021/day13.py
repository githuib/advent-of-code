from abc import ABC
from collections import deque
from typing import TYPE_CHECKING

from advent_of_code.problems import MultiLineProblem

if TYPE_CHECKING:
    from advent_of_code.geo2d import P2


class _Problem[T](MultiLineProblem[T], ABC):
    def __init__(self) -> None:
        self.points: set[P2] = set()
        self._folds: deque[tuple[str, int]] = deque([])

        parse_fold = False
        for line in self.lines:
            if not line:
                parse_fold = True
                continue
            if parse_fold:
                # line with pattern "fold along direction=n"
                _, _, fold = line.split()
                direction, n = fold.split("=")
                self._folds.appendleft((direction, int(n)))
            else:
                # line with pattern "x,y"
                x, y = line.split(",")
                self.points.add((int(x), int(y)))

    def fold_next(self) -> None:
        direction, n = self._folds.pop()
        for x, y in self.points.copy():
            if direction == "x" and x > n:
                self.points.remove((x, y))
                self.points.add((n * 2 - x, y))
            elif direction == "y" and y > n:
                self.points.remove((x, y))
                self.points.add((x, n * 2 - y))


class Problem1(_Problem[int]):
    test_solution = 17
    my_solution = 743

    def solution(self) -> int:
        self.fold_next()
        return len(self.points)


class Problem2(_Problem[str]):
    test_solution = """
█████
█░░░█
█░░░█
█░░░█
█████
"""
    my_solution = """
███░░░██░░███░░█░░░░░██░░█░░█░█░░█░█░░░
█░░█░█░░█░█░░█░█░░░░█░░█░█░█░░█░░█░█░░░
█░░█░█░░░░█░░█░█░░░░█░░█░██░░░████░█░░░
███░░█░░░░███░░█░░░░████░█░█░░█░░█░█░░░
█░█░░█░░█░█░░░░█░░░░█░░█░█░█░░█░░█░█░░░
█░░█░░██░░█░░░░████░█░░█░█░░█░█░░█░████
"""

    def solution(self) -> str:
        while self._folds:
            self.fold_next()
        width = max(x for x, _ in self.points) + 1
        height = max(y for _, y in self.points) + 1
        return "\n".join("".join(
            "█" if (x, y) in self.points else "░"
            for x in range(width)
        ) for y in range(height))


TEST_INPUT = """
6,10
0,14
9,10
0,3
10,4
4,11
6,0
6,12
4,1
0,13
10,12
3,4
3,0
8,4
1,10
2,14
8,10
9,0

fold along y=7
fold along x=5
"""
