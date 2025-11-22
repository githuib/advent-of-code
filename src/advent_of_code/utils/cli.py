import sys
import time
from itertools import count, zip_longest
from os import get_terminal_size
from typing import TYPE_CHECKING

from based_utils.calx import randf
from based_utils.cli import Colored
from based_utils.colors import Color

from advent_of_code.utils.data import filled_empty, transposed
from advent_of_code.utils.strings import right_justified, strlen

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator


type Lines = Iterable[str]


def refresh_lines(lines: Lines) -> int:
    n = 0
    for line in lines:
        sys.stdout.write(line + "\n")
        n += 1
    return n


def clear_lines(amount: int) -> None:
    for _ in range(amount):
        # \033[1A <-- LINE UP
        # \x1b[2K <-- LINE CLEAR
        sys.stdout.write("\033[1A\x1b[2K")


def animate[T](
    items: Iterable[T],
    format_item: Callable[[T], Lines],
    *,
    fps: int = 60,
    keep_last: bool = True,
    only_every_nth: int = 1,
) -> Iterator[T]:
    lines_written = 0
    for i, item in enumerate(items):
        yield item
        if i % only_every_nth != 0:
            continue

        clear_lines(lines_written)
        lines_written = refresh_lines(format_item(item))
        time.sleep(1 / fps)

    if not keep_last:
        clear_lines(lines_written)


def center(s: str, width: int) -> str:
    length = len(s)
    pad = " " * (max(width - length, 0) // 2)
    padded = pad + s + pad
    return padded + " " if len(padded) < width else padded


def animated(
    lines: Lines, frame_n: Callable[[Lines, int], Lines], *, min_width: int = None
) -> Iterator[Lines]:
    max_width, _max_height = get_terminal_size()
    block_width = max(len(line) for line in lines)
    width_ = max_width if min_width is None else min(min_width, max_width)
    frame_0 = [center(line.ljust(block_width, " "), width_) for line in lines]
    for num in count():
        n = num % width_
        yield frame_n(frame_0, n)


def moving_forward(lines: Lines, *, min_width: int = None) -> Iterator[Lines]:
    def frame_n(frame_0: Lines, n: int) -> Lines:
        return [(line[-n:] + line[:-n]) for line in frame_0]

    return animated(lines, frame_n, min_width=min_width)


def changing_colors(
    lines: Lines, *, min_width: int = None, amount_of_hues: int = 101
) -> Iterator[Lines]:
    def frame_n(frame_0: Lines, n: int) -> Lines:
        color = Color.from_fields(hue=n / amount_of_hues, lightness=0.75)
        background = color.contrasting_hue.contrasting_shade
        return [Colored(line, color, background).formatted for line in frame_0]

    return animated(lines, frame_n, min_width=min_width)


def flashing(
    lines: Lines,
    *,
    min_width: int = None,
    intensity: float = 0.1,
    hue: float = None,
    amount_of_hues: int = 101,
) -> Iterator[Lines]:
    def frame_n(frame_0: Lines, n: int) -> Lines:
        flash = n % 5 == 0 and randf() < intensity * 5
        h = randf() if flash else n / amount_of_hues if hue is None else hue
        fg = Color.from_fields(hue=h, lightness=0.5)
        bg = fg.shade(0.2)
        return [
            Colored(
                line,
                fg.but_with(lightness=0.3) if flash else fg,
                bg.but_with(lightness=0.9) if flash else bg,
            ).formatted
            for line in frame_0
        ]

    return animated(lines, frame_n, min_width=min_width)


def format_table(
    *table_rows: Iterable[str | int],
    min_columns_widths: Iterable[int] = None,
    column_splits: Iterable[int] = None,
    color: Color = None,
) -> Iterator[str]:
    first, *rest = [tr for tr in table_rows if tr]
    trs: list[Iterable[str | int]] = [[], first, [], *rest, []]
    rows = list(filled_empty([[str(v) for v in tr] for tr in trs], ""))

    def max_columns_widths() -> Iterator[int]:
        for col in transposed(rows):
            yield max(strlen(s) for s in col)

    def column_widths() -> Iterator[int]:
        for col_width, min_width in zip_longest(
            max_columns_widths(), min_columns_widths or [], fillvalue=0
        ):
            yield max(col_width, min_width)

    b = len(rows) - 1

    def t(s: str) -> str:
        return Colored(s, color).formatted

    def left(r: int) -> str:
        return t("╔" if r == 0 else "╠" if r == 2 else "╚" if r == b else "║")

    def right(r: int) -> str:
        return t("╗" if r == 0 else "╣" if r == 2 else "╝" if r == b else "║")

    def center(r: int) -> str:
        return t("╦" if r == 0 else "╬" if r == 2 else "╩" if r == b else "║")

    for r_, row in enumerate(rows):
        yield (
            left(r_)
            + "".join(
                (t("═") * (w + 2) if r_ in (0, 2, b) else f" {right_justified(s, w)} ")
                + (
                    f"{right(r_)}  {left(r_)}"
                    if c in (column_splits or [])
                    else right(r_)
                    if c == len(row)
                    else center(r_)
                )
                for c, (s, w) in enumerate(zip(row, column_widths(), strict=True), 1)
            )
        )
