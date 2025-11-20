from abc import ABC
from collections import deque
from collections.abc import Iterable
from itertools import count, cycle
from typing import TYPE_CHECKING

from based_utils.algo import detect_cycle
from more_itertools import nth_or_last, unzip

from advent_of_code import log
from advent_of_code.problems import OneLineProblem
from advent_of_code.utils.geo2d import StringGrid2

if TYPE_CHECKING:
    from collections.abc import Iterator

MAX_HEIGHT = 65

SHAPES = [
    [0b11110],  # -
    [0b01000, 0b11100, 0b01000],  # +
    [0b11100, 0b00100, 0b00100],  # _|
    [0b10000, 0b10000, 0b10000, 0b10000],  # |
    [0b11000, 0b11000],  # []
]

Shape = list[int]
Pattern = Iterable[int]


class MaxHeightReachedError(RuntimeError):
    def __init__(self) -> None:
        super().__init__(
            f"Maximum height reached: {MAX_HEIGHT}. Increase MAX_HEIGHT or check if something is wrong with the code."
        )


class _Problem(OneLineProblem[int], ABC):
    def play(self) -> Iterator[tuple[int, int, Pattern, Shape]]:
        pattern = deque([0b1111111] * MAX_HEIGHT, maxlen=MAX_HEIGHT)
        height = 0
        directions = cycle(self.line)
        shapes = cycle(SHAPES)

        def occludes_with(shape: Shape, y_: int) -> bool:
            return any(
                r <= y_ and pattern[y_ - r] & row_ for r, row_ in enumerate(shape)
            )

        def try_move(d: str, shape: Shape, y_: int) -> Shape:
            to_left = d == "<"
            moved = [row_ << 1 if to_left else row_ >> 1 for row_ in shape]
            side = 0b1000000 if to_left else 0b0000001
            occ_side = any(r & side for r in shape)
            occ_pat = occludes_with(moved, y_)
            return shape if occ_side or occ_pat else moved

        while True:
            curr_shape = next(shapes)
            for y in count(-4):
                if y == MAX_HEIGHT:
                    raise MaxHeightReachedError

                curr_shape = try_move(next(directions), curr_shape, y)

                if y < -1 or not occludes_with(curr_shape, y + 1):
                    continue

                for i, row in enumerate(curr_shape):
                    py = y - i
                    if py < 0:
                        pattern.appendleft(row)
                        height += 1
                    else:
                        pattern[py] |= row

                yield height, y, pattern, curr_shape
                break

    def height_at_t(self, t: int) -> int:
        def format_state(item: tuple[int, int, Pattern, Shape]) -> Iterator[str]:
            _height, y, pattern, shape = item

            def value(row_: int, r: int, c: int) -> str:
                n = len(shape)
                s = y - min(0, y - n + 1) - r
                if 0 <= s < n and shape[s] >> c & 1:
                    return "^"
                return "#" if row_ >> c & 1 else "."

            return StringGrid2(
                ((c, r), value(row, r, c))
                for r, row in enumerate(pattern)
                for c in range(6, -1, -1)
            ).to_lines()

        it = log.debug_animated(self.play(), format_state, frame_rate=1000)
        state_at_t = nth_or_last(it, t - 1)
        log.lazy_debug(lambda: format_state(state_at_t))
        height, *_ = state_at_t
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
        _heights, _ys, patterns, _shapes = unzip(self.play())
        cycle_ = detect_cycle(patterns)
        n = 1_000_000_000_000 - cycle_.start
        return (
            self.height_at_t(cycle_.start + cycle_.length)
            - self.height_at_t(cycle_.start)
        ) * (n // cycle_.length) + self.height_at_t(cycle_.start + n % cycle_.length)


TEST_INPUT = ">>><<><>><<<>><>>><<<>>><<<><<<>><>><<>>"
