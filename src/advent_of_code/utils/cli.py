from dataclasses import dataclass
from functools import cached_property
from itertools import zip_longest
from typing import TYPE_CHECKING

from based_utils.calx import fractions
from based_utils.colors import Color, color_names
from yachalk import chalk

from advent_of_code.utils.data import filled_empty, transposed
from advent_of_code.utils.strings import right_justified, strlen

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator


@dataclass(frozen=True)
class Colored:
    value: object
    color: Color | None = None
    background: Color | None = None

    def with_color(self, color: Color) -> Colored:
        return Colored(self.value, color, self.background)

    def with_background(self, background: Color) -> Colored:
        return Colored(self.value, self.color, background)

    @cached_property
    def formatted(self) -> str:
        s = str(self.value)
        if self.color:
            s = chalk.hex(self.color.hex)(s)
        if self.background:
            s = chalk.bg_hex(self.background.hex)(s)
        return s

    def __repr__(self) -> str:
        return self.formatted

    def __str__(self) -> str:
        return self.formatted


def color_shades(c: Color) -> Iterator[str]:
    for f in fractions(9):
        s = c.shade(f)
        yield Colored(f" {f * 100:.0f}% ", s.contrasting_shade, s).formatted


def color_line(c: Color, n: str = "") -> str:
    h = "   " if n == "grey" else f"{c.hue * 360:03.0f}"
    return "".join(color_shades(c)) + Colored(f" {h} {n}", c).formatted


def color_lines() -> Iterator[str]:
    yield color_line(Color.grey(), "grey")
    for n in color_names:
        yield color_line(Color.from_name(n), n)


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
