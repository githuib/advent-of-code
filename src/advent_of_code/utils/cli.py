from itertools import zip_longest
from time import perf_counter_ns
from typing import TYPE_CHECKING, cast

from yachalk import chalk

from advent_of_code.utils.strings import pad_with_spaces, strlen

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator


def timed[T](func: Callable[[], T]) -> tuple[T, int, str]:
    start = perf_counter_ns()
    result = func()
    end = perf_counter_ns()
    nanoseconds = end - start
    return result, nanoseconds, human_readable_duration(nanoseconds)


def human_readable_duration(nanoseconds: int) -> str:
    minutes = int(nanoseconds // 60_000_000_000)
    nanoseconds %= 60_000_000_000
    seconds = int(nanoseconds // 1_000_000_000)
    nanoseconds %= 1_000_000_000
    milliseconds = int(nanoseconds // 1_000_000)
    nanoseconds %= 1_000_000
    microseconds = int(nanoseconds // 1_000)
    nanoseconds %= 1_000
    if minutes:
        return f"{minutes:d}:{seconds:02d}.{milliseconds:03d} minutes"
    if seconds:
        return f"{seconds:d}.{milliseconds:03d} seconds"
    if milliseconds:
        return f"{milliseconds:d}.{microseconds:03d} ms"
    return f"{microseconds:d}.{nanoseconds:03d} µs"


def pixel[T](
    value: T,
    on: str = chalk.hex("0af").bg_hex("0af")("#"),
    off: str = chalk.hex("654").bg_hex("654")("."),
    special: str = chalk.hex("b40").bg_hex("b40")("^"),
    pixels: dict[T, str] = None,
) -> str:
    if isinstance(value, int):
        int_pixels = cast("dict[int, str]", pixels) or {0: off, 1: on, 2: special}
        return int_pixels.get(min(cast("int", value), max(int_pixels.keys())), " ")
    if isinstance(value, str):
        str_pixels = cast("dict[str, str]", pixels) or {".": off, "#": on, "^": special}
        return str_pixels.get(cast("str", value), " ")
    return " "


def table_cell_str(s: str, width: int, row: int) -> str:
    return pad_with_spaces(chalk.underline(s) if row == 0 else s, width)


def table_lines(
    *table: Iterable[object],
    column_sep: str = "  ",
    min_columns_widths: Iterable[int] = None,
) -> Iterator[str]:
    def iter_row_strs() -> Iterator[list[str]]:
        for row_cells in table:
            if row_cells:
                yield [str(v) for v in row_cells]

    cols: list[tuple[str, ...]] = list(zip_longest(*iter_row_strs(), fillvalue=""))

    def max_columns_widths() -> Iterator[int]:
        for col in cols:
            yield max(strlen(s) for s in col)

    def column_widths() -> Iterator[int]:
        for col_width, min_width in zip_longest(
            max_columns_widths(), min_columns_widths or [], fillvalue=0
        ):
            yield max(col_width, min_width)

    rows: Iterator[tuple[str, ...]] = zip(*cols, strict=True)
    for r, row in enumerate(rows):
        yield column_sep.join(
            table_cell_str(s, w, r) for s, w in zip(row, column_widths(), strict=True)
        )
