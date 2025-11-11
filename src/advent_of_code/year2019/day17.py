from typing import TYPE_CHECKING

from more_itertools import last

from advent_of_code import log
from advent_of_code.utils.geo2d import P2, NumberGrid2

from .intcode import IntcodeProblem

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

# ORDER = [0, 3, 1, 2]  # UP, RIGHT, DOWN, LEFT


class Problem1(IntcodeProblem[int]):
    my_solution = 2804

    def solution(self) -> int:
        grid = "".join(
            chr(output) for output in self.computer.run_to_next_output()
        ).splitlines()

        return sum(
            row * col
            for row in range(2, len(grid) - 2, 2)
            for col in range(2, len(grid[0]) - 2, 2)
            if (
                grid[row][col] == "#"
                and grid[row - 1][col] == "#"
                and grid[row + 1][col] == "#"
                and grid[row][col - 1] == "#"
                and grid[row][col + 1] == "#"
            )
        )


def process_output(runner: Iterable[int]) -> Iterator[tuple[P2, int]]:
    x = 0
    y = 0
    char_values = {".": 0, "#": 1, "^": 2}
    for output in runner:
        c = chr(output)
        if c == "\n":
            if x == 0:
                break
            x = 0
            y += 1
        else:
            yield (x, y), char_values[c]
            x += 1


class Problem2(Problem1):
    my_solution = 833429

    def solution(self) -> int:
        self.computer.program[0] = 2

        runner = self.computer.run_to_next_output()

        # stage 1: Constructed path from first output
        processed = process_output(runner)
        log.lazy_debug(lambda: NumberGrid2(processed).to_lines())

        # Stage 2: Patterns derived manually after looking at path
        self.computer.inputs = [
            ord(c)
            for s in ["ABACABCCAB", "R8L55R8", "R66R8L8L66", "L66L55L8", "n"]
            for c in ",".join(s) + "\n"
        ]
        return last(runner)


TEST_INPUT = ""
