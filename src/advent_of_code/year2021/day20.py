from abc import ABC
from typing import TYPE_CHECKING, Self

from based_utils.data.conversion import bits_to_int

from advent_of_code import log
from advent_of_code.problems import MultiLineProblem
from advent_of_code.utils.geo2d import BitGrid2

if TYPE_CHECKING:
    from collections.abc import Iterable


class Image:
    def __init__(self, input_lines: Iterable[str], padding: int) -> None:
        enhance_line, _, *image_lines = input_lines
        self._enhancement = [c == "#" for c in enhance_line]
        self._padding = padding + 1
        self._size = len(image_lines) + self._padding * 2
        grid = BitGrid2.from_lines(image_lines)
        log.lazy_debug(grid.to_lines)
        self._image: list[list[bool]] = [
            [
                grid.get((x - self._padding, y - self._padding), False)
                for x in range(self._size)
            ]
            for y in range(self._size)
        ]

    def _is_in_image(self, x: int, y: int) -> bool:
        min_v, max_v = self._padding, self._size - self._padding
        return min_v <= x < max_v and min_v <= y < max_v

    def enhanced(self) -> Self:
        edge_bit = False
        while self._padding > 1:
            self._padding -= 1
            edge_bit = self._enhancement[edge_bit]
            self._image = [
                [
                    self._enhancement[
                        bits_to_int(
                            [
                                self._image[y + ky][x + kx]
                                for ky in (-1, 0, 1)
                                for kx in (-1, 0, 1)
                            ]
                        )
                    ]
                    if self._is_in_image(x, y)
                    else edge_bit
                    for x in range(self._size)
                ]
                for y in range(self._size)
            ]
            # self.grid = Mat2({(x, y): self._enhancement[bits_to_int([
            #     self.grid[x + kx, y + ky] for ky in (-1, 0, 1) for kx in (-1, 0, 1)
            # ])] if self._is_in_image(x, y) else edge_bit for x, y in self.grid})
        # log.debug(self.grid)
        return self

    def num_light_pixels(self) -> int:
        return sum(b for row in self._image[1:-1] for b in row[1:-1])
        # return sum(b for (x, y), b in self.grid.items() if self._is_in_image(x, y))


class _Problem(MultiLineProblem[int], ABC):
    padding: int

    def solution(self) -> int:
        return Image(self.lines, self.padding).enhanced().num_light_pixels()


class Problem1(_Problem):
    test_solution = 35
    puzzle_solution = 5475

    padding = 2


class Problem2(_Problem):
    test_solution = 3351
    puzzle_solution = 17548

    padding = 50


TEST_INPUT = """
..#.#..#####.#.#.#.###.##.....###.##.#..###.####..#####..#....#..#..##..###..######.###...####..#..#####..##..#.#####...##.#.#..#.##..#.#......#.###.######.###.####...#.##.##..#..#..#####.....#.#....###..#.##......#.....#..#..#..##..#...##.######.####.####.#.#...#.......#..#.#.#...####.##.#......#..#...##.#.##..#...##.#.##..###.#......#.#.......#.#.#.####.###.##...#.....####.#..#..#.##.#....##..#.####....##...##..#...#......#.#.......#.......##..####..#...#.#.#...##..#.#..###..#####........#..####......#..#

#..#.
#....
##..#
..#..
..###
"""
