from abc import ABC
from collections import deque
from functools import partial
from itertools import count, cycle
from typing import TYPE_CHECKING

from based_utils.algo import detect_cycle
from more_itertools import nth_or_last, unzip

from advent_of_code import log
from advent_of_code.problems import OneLineProblem
from advent_of_code.utils.geo2d import NumberGrid2

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

MAX_HEIGHT = 65


SHAPES = [
    [0b11110],  # -
    [0b01000, 0b11100, 0b01000],  # +
    [0b11100, 0b00100, 0b00100],  # _|
    [0b10000, 0b10000, 0b10000, 0b10000],  # |
    [0b11000, 0b11000],  # []
]


def occludes_with(shape: Sequence[int], pattern: Sequence[int], y: int) -> bool:
    return any(i <= y and pattern[y - i] & row for i, row in enumerate(shape))


def board_str(shape: Sequence[int], pattern: Sequence[int], y: int) -> Iterator[str]:
    def value(row_: int, r_: int, c_: int) -> int:
        n = len(shape)
        s = y - min(0, y - n + 1) - r_
        if 0 <= s < n and shape[s] >> c_ & 1:
            return 2
        return row_ >> c_ & 1

    return NumberGrid2(
        ((c, r), value(row, r, c))
        for r, row in enumerate(pattern)
        for c in range(6, -1, -1)
    ).to_lines()


class _Problem(OneLineProblem[int], ABC):
    def play(self) -> Iterator[tuple[int, list[int]]]:
        pattern: deque[int] = deque([0b1111111] * MAX_HEIGHT, maxlen=MAX_HEIGHT)
        height = 0
        directions = cycle(self.line)
        shapes = cycle(SHAPES)
        while True:
            curr_shape = next(shapes)
            for y in count(-4):
                if y == MAX_HEIGHT:
                    msg = "Increase MAX_HEIGHT"
                    raise RuntimeError(msg)
                if next(directions) == "<":
                    if not (
                        any(row & 0b1000000 for row in curr_shape)
                        or occludes_with(
                            moved_to_left := [row << 1 for row in curr_shape],
                            pattern,
                            y,
                        )
                    ):
                        curr_shape = moved_to_left
                elif not (
                    any(row & 0b0000001 for row in curr_shape)
                    or occludes_with(
                        moved_to_right := [row >> 1 for row in curr_shape], pattern, y
                    )
                ):
                    curr_shape = moved_to_right
                if y >= -1 and occludes_with(curr_shape, pattern, y + 1):
                    for i, row in enumerate(curr_shape):
                        if (py := y - i) < 0:
                            pattern.appendleft(row)
                            height += 1
                        else:
                            pattern[py] |= row

                    log.lazy_debug(
                        partial(
                            lambda s, y_: board_str(s, pattern, y_),
                            s=curr_shape[:],
                            y_=y,
                        )
                    )

                    yield height, list(pattern)
                    break

    def height_at_t(self, t: int) -> int:
        height, _pattern = nth_or_last(self.play(), t - 1)
        return height


class Problem1(_Problem):
    test_solution = 3068
    puzzle_solution = 3173

    def solution(self) -> int:
        return self.height_at_t(2022)


class Problem2(_Problem):
    test_solution = 1514285714288
    puzzle_solution = 1570930232582

    def solution(self) -> int:
        _heights, patterns = unzip(self.play())
        cycle_ = detect_cycle(patterns)
        n = 1_000_000_000_000 - cycle_.start
        return (
            self.height_at_t(cycle_.start + cycle_.length)
            - self.height_at_t(cycle_.start)
        ) * (n // cycle_.length) + self.height_at_t(cycle_.start + n % cycle_.length)


TEST_INPUT = ">>><<><>><<<>><>>><<<>>><<<><<<>><>><<>>"
