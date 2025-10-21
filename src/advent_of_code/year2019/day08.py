from more_itertools import first_true

from advent_of_code.problems import NoSolutionFoundError, OneLineProblem

WIDTH, HEIGHT = 25, 6
SIZE = WIDTH * HEIGHT


class Problem1(OneLineProblem[int]):
    test_solution = None
    my_solution = 1072

    def solution(self) -> int:
        first_line = self.line
        lowest_zero_count = None
        lowest_zeros_layer = None
        for i in range(0, len(first_line), SIZE):
            layer = first_line[i : i + SIZE]
            zero_count = layer.count("0")
            if lowest_zero_count and lowest_zero_count < zero_count:
                continue
            lowest_zero_count = zero_count
            lowest_zeros_layer = layer
        if lowest_zero_count is None or lowest_zeros_layer is None:
            raise NoSolutionFoundError
        return lowest_zeros_layer.count("1") * lowest_zeros_layer.count("2")


class Problem2(OneLineProblem[str]):
    test_solution = None
    my_solution = """
█░░░██░░░░████░███░░░░██░
█░░░██░░░░█░░░░█░░█░░░░█░
░█░█░█░░░░███░░█░░█░░░░█░
░░█░░█░░░░█░░░░███░░░░░█░
░░█░░█░░░░█░░░░█░░░░█░░█░
░░█░░████░█░░░░█░░░░░██░░
"""

    def solution(self) -> str:
        chars = {"0": "░", "1": "█", None: "?"}
        pixels = [
            chars[first_true(self.line[i::SIZE], pred=lambda s: s != "2")]
            for i in range(SIZE)
        ]
        return "\n".join("".join(pixels[i : i + WIDTH]) for i in range(0, SIZE, WIDTH))
