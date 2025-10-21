from abc import ABC
from collections import Counter

from advent_of_code.problems import MultiLineProblem


class _Problem(MultiLineProblem[int], ABC):
    include_diagonal_lines: bool

    def solution(self) -> int:
        points = []
        for line in self.lines:
            x1, y1, x2, y2 = (
                int(val) for p in line.split(" -> ") for val in p.split(",")
            )
            dir_x = 1 if x2 > x1 else -1
            dir_y = 1 if y2 > y1 else -1

            if y1 == y2:
                # horizontal line
                points += [(x, y1) for x in range(x1, x2 + dir_x, dir_x)]

            elif x1 == x2:
                # vertical line
                points += [(x1, y) for y in range(y1, y2 + dir_y, dir_y)]

            elif self.include_diagonal_lines and abs(x2 - x1) == abs(y2 - y1):
                # diagonal line
                points += list(
                    zip(
                        range(x1, x2 + dir_x, dir_x),
                        range(y1, y2 + dir_y, dir_y),
                        strict=False,
                    )
                )

        return len([p for p, c in Counter(points).items() if c >= 2])
        # return len([p for p, c in Counter(
        # p for line in input_lines for p in foo(line, include_diagonal_lines)).items() if c >= 2])


class Problem1(_Problem):
    test_solution = 5
    my_solution = 7674

    include_diagonal_lines = False


class Problem2(_Problem):
    test_solution = 12
    my_solution = 20898

    include_diagonal_lines = True


TEST_INPUT = """
0,9 -> 5,9
8,0 -> 0,8
9,4 -> 3,4
2,2 -> 2,1
7,0 -> 7,4
6,4 -> 2,0
0,9 -> 2,9
3,4 -> 1,4
0,0 -> 8,8
5,5 -> 8,2
"""
