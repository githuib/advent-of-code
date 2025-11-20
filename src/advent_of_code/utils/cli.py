import sys
from itertools import zip_longest
from typing import TYPE_CHECKING

from based_utils.cli import Colored

from advent_of_code.utils.data import filled_empty, transposed
from advent_of_code.utils.strings import right_justified, strlen

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from based_utils.colors import Color


def print_lines(lines: Iterable[str]) -> None:
    for line in lines:
        sys.stdout.write(line + "\n")


def clear_lines(lines: Iterable[str]) -> None:
    for _ in lines:
        # \033[1A <-- LINE UP
        # \x1b[2K <-- LINE CLEAR
        sys.stdout.write("\033[1A\x1b[2K")


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
