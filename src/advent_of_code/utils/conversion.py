from typing import TYPE_CHECKING, overload

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable


@overload
def try_convert[T, R](cls: Callable[[T], R], val: T, *, default: R) -> R: ...


@overload
def try_convert[T, R](
    cls: Callable[[T], R], val: T, *, default: None = None
) -> R | None: ...


def try_convert[T, R](cls: Callable[[T], R], val: T, *, default: R = None) -> R | None:
    try:
        return cls(val)
    except ValueError:
        return default


def compose_number(numbers: Iterable[int]) -> int:
    return int("".join(str(n) for n in numbers))


def bits_to_int(bits: Iterable[bool]) -> int:
    """
    Convert boolean array -> number.

    >>> bits_to_int([True, False, False, True, False, True, True])
    75
    """
    return int("".join([f"{b:d}" for b in bits]), 2)


def int_to_bits(i: int, min_length: int = 0) -> list[bool]:
    """
    Convert number -> boolean array.

    >>> int_to_bits(75)
    [True, False, False, True, False, True, True]
    >>> int_to_bits(75, min_length=10)
    [False, False, False, True, False, False, True, False, True, True]
    """
    s = f"{i:b}"
    if min_length:
        s = s.zfill(min_length)
    return [c == "1" for c in s]
