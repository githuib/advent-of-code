import re
import unicodedata
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator

PRE_a = ord("a") - 1
PRE_A = ord("A") - 1


_ansi_regex = re.compile(r"\x1b\[\d+(;\d+)*m")


def strip_ansi(s: str) -> str:
    return _ansi_regex.sub("", s)


def strlen(s: str) -> int:
    return sum(
        (2 if unicodedata.east_asian_width(c) == "W" else 1) for c in strip_ansi(s)
    )


def pad_with_spaces(s: str, width: int) -> str:
    return s + " " * max(width - strlen(s), 0)


def padded(lines: Iterable[str], max_length: int = None) -> Iterator[str]:
    max_length = max_length or max(len(line) for line in lines)
    for line in lines:
        yield line.ljust(max_length)


def split_at(s: str, pos: int) -> tuple[str, str]:
    return s[:pos], s[pos:]


def split_conditional[T](
    collection: list[T], condition: Callable[[T], bool]
) -> tuple[list[T], list[T]]:
    left = [item for item in collection if condition(item)]
    right = [item for item in collection if item not in left]
    return left, right
