from based_utils.cli import Colored
from based_utils.colors import Colors
from more_itertools import first_true

from advent_of_code.problems import NoSolutionFoundError, OneLineProblem

W, H = 25, 6
N = W * H


class Problem1(OneLineProblem[int]):
    test_solution = None
    puzzle_solution = 1072

    def solution(self) -> int:
        first_line = self.line
        lowest_zero_count = None
        lowest_zeros_layer = None
        for i in range(0, len(first_line), N):
            layer = first_line[i : i + N]
            zero_count = layer.count("0")
            if lowest_zero_count and lowest_zero_count < zero_count:
                continue
            lowest_zero_count = zero_count
            lowest_zeros_layer = layer
        if lowest_zero_count is None or lowest_zeros_layer is None:
            raise NoSolutionFoundError
        return lowest_zeros_layer.count("1") * lowest_zeros_layer.count("2")


def format_char(s: str) -> str:
    if s not in ".#":
        return s

    c = Colors.yellow.very_bright if s == "#" else Colors.blue.dark
    return Colored(s, c, c.darker()).formatted


def colored(s: str) -> str:
    return "".join(format_char(c) for c in s)


class Problem2(OneLineProblem[str]):
    test_solution = None
    puzzle_solution = colored("""
#...##....####.###....##.
#...##....#....#..#....#.
.#.#.#....###..#..#....#.
..#..#....#....###.....#.
..#..#....#....#....#..#.
..#..####.#....#.....##..
""")

    def solution(self) -> str:
        ns = [int(c) for c in self.line]

        def check(i: int) -> bool:
            return i < 2

        pixels = ["#" if first_true(ns[i::N], pred=check) else "." for i in range(N)]
        return colored("\n".join("".join(pixels[i : i + W]) for i in range(0, N, W)))
