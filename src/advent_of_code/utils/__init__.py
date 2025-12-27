from typing import TYPE_CHECKING

from kleur import Color, Colored, ColorStr

if TYPE_CHECKING:
    from collections.abc import Callable

_LOWER_ALPHABET_START = ord("a") - 1


def lower_to_num(c: str) -> int:
    return ord(c) - _LOWER_ALPHABET_START


def num_to_lower(n: int) -> str:
    return chr(_LOWER_ALPHABET_START + n)


_UPPER_ALPHABET_START = ord("A") - 1


def upper_to_num(c: str) -> int:
    return ord(c) - _UPPER_ALPHABET_START


def num_to_upper(n: int) -> str:
    return chr(_UPPER_ALPHABET_START + n)


def lowlighted(color: Color) -> Callable[[str], ColorStr]:
    return Colored(color, color.darker())
