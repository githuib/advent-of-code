from functools import cache
from os import get_terminal_size, terminal_size
from typing import TYPE_CHECKING

from kleur import Color, Colored, ColorStr

if TYPE_CHECKING:
    from collections.abc import Callable

PRE_a = ord("a") - 1
PRE_A = ord("A") - 1


def lowlighted(color: Color) -> Callable[[str], ColorStr]:
    return Colored(color, color.darker())


@cache
def term_size() -> terminal_size:
    return get_terminal_size()
