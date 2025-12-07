from abc import ABC

from based_utils.cli import Colored
from based_utils.colors import Color

from advent_of_code import log
from advent_of_code.problems import NumGridProblem
from advent_of_code.utils.geo2d import P2, all_directions


def format_value(_p: P2, v: int, _colored: Colored) -> Colored:
    if v == 10:
        return Colored(".", Color.from_name("blue", lightness=0.33, saturation=0.66))
    if v > 10:
        c_special = Color.from_name("red", lightness=0.66)
        return Colored(chr(v), c_special, c_special.contrasting_shade)
    return Colored(v, Color.from_name("green", lightness=0.66))


class _Problem(NumGridProblem[int], ABC):
    def __init__(self) -> None:
        log.lazy_debug(lambda: self.grid.to_lines(format_value=format_value))

        self.symbols_parts: dict[P2, list[P2]] = {}
        self.parts: dict[P2, int] = {}
        curr_num = ""
        curr_symbol: P2 | None = None
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                val = self.grid[x, y]
                if val < 10:
                    curr_num += str(val)
                    for n, v in self.grid.neighbors((x, y), directions=all_directions):
                        if v > 10:
                            curr_symbol = n
                if (val >= 10 and curr_num != "") or x == self.grid.width - 1:
                    if curr_symbol is not None:
                        self.symbols_parts.setdefault(curr_symbol, []).append((x, y))
                        self.parts[x, y] = int(curr_num)
                    curr_num = ""
                    curr_symbol = None

    def parse_value(self, c: str) -> int:
        return int(c) if c.isdigit() else 10 if c == "." else ord(c)


class Problem1(_Problem):
    test_solution = 4361
    puzzle_solution = 554003

    def solution(self) -> int:
        return sum(self.parts.values())


class Problem2(_Problem):
    test_solution = 467835
    puzzle_solution = 87263515

    def solution(self) -> int:
        return sum(
            self.parts[v[0]] * self.parts[v[1]]
            for k, v in self.symbols_parts.items()
            if self.grid[k] == ord("*") and len(v) == 2
        )


TEST_INPUT = """
467..114..
...*......
..35..633.
......#...
617*......
.....+.58.
..592.....
......755.
...$.*....
.664.598..
"""
