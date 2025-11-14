from enum import Enum
from itertools import zip_longest
from typing import TYPE_CHECKING

from yachalk import chalk

from advent_of_code.utils.data import filled_empty, transposed
from advent_of_code.utils.strings import pad_with_spaces, strlen

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator


class Pixel(Enum):
    GOOD = chalk.hex("0af").bg_hex("0af")("#")
    BAD = chalk.hex("654").bg_hex("654")(".")
    UGLY = chalk.hex("b40").bg_hex("b40")("^")
    DEAD = " "


def table_cell_str(s: str, width: int, row: int) -> str:
    return pad_with_spaces(chalk.underline(s) if row == 0 else s, width)


def format_table(
    *table_rows: Iterable[str | int],
    column_sep: str = "  ",
    min_columns_widths: Iterable[int] = None,
) -> Iterator[str]:
    first, *rest = table_rows
    trs: list[Iterable[str | int]] = [first, [], *rest]
    rows = list(filled_empty([[str(v) for v in tr] for tr in trs], ""))

    def max_columns_widths() -> Iterator[int]:
        for col in transposed(rows):
            yield max(strlen(s) for s in col)

    def column_widths() -> Iterator[int]:
        for col_width, min_width in zip_longest(
            max_columns_widths(), min_columns_widths or [], fillvalue=0
        ):
            yield max(col_width, min_width)

    for r, row in enumerate(rows):
        yield column_sep.join(
            table_cell_str(s, w, r) for s, w in zip(row, column_widths(), strict=True)
        )


def text_block_from_lines(lines: Iterable[str]) -> Iterator[str]:
    def with_bg(s: str) -> str:
        return chalk.bg_hex("af0")(s)

    width = max(strlen(line) for line in lines)
    edge = with_bg(" " * (width + 4))

    def formatted_line(line: str) -> str:
        padding = " " * (width - strlen(line))
        colored = f" {line}{padding} "
        return f"{with_bg(' ')}{colored}{with_bg(' ')}"

    yield edge
    yield formatted_line("")
    for line in lines:
        yield formatted_line(line)
    yield formatted_line("")
    yield edge
