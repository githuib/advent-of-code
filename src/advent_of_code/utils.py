from collections.abc import Callable, Hashable, Iterable, Iterator
from itertools import chain, count, pairwise, repeat, takewhile, tee
from time import perf_counter_ns
from typing import (
    Protocol,
    overload,
    runtime_checkable,
)

from yachalk import chalk

from advent_of_code import AOC, log

Predicate = Callable[..., bool]


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


@runtime_checkable
class Sortable(Protocol):
    def __lt__(self, other: object) -> bool: ...


class Unique:
    def __init__(self, data: object):
        self.data = data

    def __lt__(self, other: object) -> bool:
        if isinstance(other, Unique) and isinstance(self.data, Sortable):
            return self.data < other.data
        return NotImplemented

    def __repr__(self) -> str:
        return repr(self.data)


def pixel(
    value,
    on: str = chalk.hex("0af").bg_hex("0af")("#"),
    off: str = chalk.hex("654").bg_hex("654")("."),
    special: str = chalk.hex("b40").bg_hex("b40")("^"),
    pixels: dict[int | str, str] | None = None,
) -> str:
    if value is None:
        value = -1
    if pixels is None:
        pixels = (
            {0: off, 1: on, 2: special}
            if isinstance(value, int)
            else {".": off, "#": on, "^": special}
        )
    return pixels.get(min(value, max(pixels.keys())), " ")


# def logging.debug_grid(
#     grid: Iterable[Iterable[int]],
#     on: str = chalk.hex('0af').bg_hex('0af')('#'),
#     off: str = chalk.hex('654').bg_hex('654')('.'),
#     special: str = chalk.hex('b40').bg_hex('b40')('^'),
#     pixels: dict[int, str] = None,
# ) -> None:
#     if not AOC.debugging:
#         return
#     for row in grid:
#         logging.debug(''.join(pixel(v, on, off, special, pixels) for v in row))


def debug_table(
    table: Iterable[Iterable[object]], widths: Iterable[int] | None = None
) -> None:
    if not AOC.debugging:
        return
    rows = [
        [(v if isinstance(v, tuple) else (str(v), len(str(v)))) for v in row]
        for row in table
    ]
    widths_ = [max(length for _, length in col) for col in zip(*rows, strict=False)]
    for i, w in enumerate(widths or []):
        widths_[i] = w
    for i, row in enumerate(rows):
        log.debug(
            " %s",
            "   ".join(
                (chalk.underline(s) if i == 0 else s) + " " * (w - length)
                for (s, length), w in zip(row, widths_, strict=False)
            ),
        )


def compose_number(numbers: Iterable[int]) -> int:
    return int("".join(str(n) for n in numbers))


def bits_to_int(bits: Iterable[bool]) -> int:
    """
    >>> bits_to_int([True, False, False, True, False, True, True])
    75
    """
    return int("".join([f"{b:d}" for b in bits]), 2)


def int_to_bits(i: int, min_length: int = 0) -> list[bool]:
    """
    >>> int_to_bits(75)
    [True, False, False, True, False, True, True]
    >>> int_to_bits(75, min_length=10)
    [False, False, False, True, False, False, True, False, True, True]
    """
    s = f"{i:b}"
    if min_length:
        s = s.zfill(min_length)
    return [c == "1" for c in s]


def mods(x: int, y: int, shift: int = 0) -> int:
    return (x - shift) % y + shift


def compare(v1: int, v2: int) -> int:
    return (v1 < v2) - (v1 > v2)


@overload
def try_convert[T, R](cls: Callable[[T], R], val: T, default: R) -> R: ...


@overload
def try_convert[T, R](cls: Callable[[T], R], val: T, default: None) -> R | None: ...


def try_convert[T, R](cls: Callable[[T], R], val: T, default: R = None) -> R | None:
    try:
        return cls(val)
    except ValueError:
        return default


def invert_dict[K, V](d: dict[K, V]) -> dict[V, K]:
    return {v: k for k, v in d.items()}


def pairwise_circular[T](it: Iterable[T]) -> Iterator[tuple[T, T]]:
    a, b = tee(it)
    return zip(a, chain(b, (next(b),)), strict=False)


def triplewise_circular[T](it: Iterable[T]) -> Iterator[tuple[T, T, T]]:
    a, b, c = tee(it, 3)
    return zip(a, chain(b, (next(b),)), chain(c, (next(c), next(c))), strict=False)


def repeat_transform[T](
    value: T,
    transform: Callable[[T], T],
    times: int | None = None,
    while_condition: Callable[[T], bool] | None = None,
) -> Iterator[T]:
    if while_condition:
        yield from takewhile(while_condition, repeat_transform(value, transform, times))
    else:
        for _ in repeat(None) if times is None else repeat(None, times):
            value = transform(value)
            yield value


def first_when[T](it: Iterable[T], predicate: Callable[[T], bool]) -> tuple[int, T]:
    for step, item in enumerate(it, 1):
        if predicate(item):
            return step, item
    raise StopIteration


def first_duplicate[T](it: Iterable[T]) -> tuple[int, T]:
    for i, (item1, item2) in enumerate(pairwise(it), 1):
        if item1 == item2:
            return i, item1
    raise StopIteration


def smart_range(start: int, stop: int, inclusive: bool = False) -> Iterable[int]:
    direction = 1 if start <= stop else -1
    if inclusive:
        stop += direction
    # print(start, stop, direction)
    return range(start, stop, direction)


def grouped[T](input_values: Iterable[T], delimeter: T = None) -> Iterator[list[T]]:
    group: list[T] = []
    for value in input_values:
        if (delimeter and value == delimeter) or not value:
            yield group
            group = []
        else:
            group.append(value)
    yield group


def group_tuples[K, V](items: Iterable[tuple[K, V]]) -> dict[K, list[V]]:
    """
    Group items in a dict by key(item).
    >>> group_tuples(
    ...     [
    ...         ("m", "Arnold"),
    ...         ("f", "Billie"),
    ...         ("m", "Charles"),
    ...         ("m", "Dirk"),
    ...         ("f", "Emma"),
    ...     ]
    ... )
    {'m': ['Arnold', 'Charles', 'Dirk'], 'f': ['Billie', 'Emma']}
    """
    result: dict[K, list[V]] = {}
    for key, value in items:
        result.setdefault(key, []).append(value)
    return result


def group_by[K, V](items: Iterable[V], key: Callable[[V], K]) -> dict[K, list[V]]:
    """
    Group items in a dict by key(item).
    >>> group_by(
    ...     ["Alice", "Bill", "Bob", "Charles", "Arnold", "Chuck"], key=lambda s: s[0]
    ... )
    {'A': ['Alice', 'Arnold'], 'B': ['Bill', 'Bob'], 'C': ['Charles', 'Chuck']}
    """
    result: dict[K, list[V]] = {}
    for value in items:
        result.setdefault(key(value), []).append(value)
    return result


def transposed(lines: Iterable[str]) -> Iterator[str]:
    for col in zip(*lines, strict=False):
        yield "".join(col)


def map_to_int_ids[D: Iterator | list | tuple | dict](data: D) -> D:
    ids = {}
    ids_gen = count()

    def map_to_int_ids_rec(value):
        if isinstance(value, Iterator):
            return (map_to_int_ids_rec(v) for v in value)
        if isinstance(value, list):
            return [map_to_int_ids_rec(v) for v in value]
        if isinstance(value, tuple):
            return tuple(map_to_int_ids_rec(v) for v in value)
        if isinstance(value, dict):
            return {k: map_to_int_ids_rec(v) for k, v in value.items()}
        if not isinstance(value, Hashable):
            return ValueError(f"Item is not hashable: {value}")
        if value not in ids:
            ids[value] = next(ids_gen)
        return ids[value]

    return map_to_int_ids_rec(data)


def padded(lines: Iterable[str], maxlen: int | None = None) -> Iterator[str]:
    maxlen = maxlen or max(len(line) for line in lines)
    for line in lines:
        yield line.ljust(maxlen)


def split_at(s: str, pos: int) -> tuple[str, str]:
    return s[:pos], s[pos:]


def split_conditional[T](
    collection: list[T],
    condition: Callable[[T], bool],
) -> tuple[list[T], list[T]]:
    left = [item for item in collection if condition(item)]
    right = [item for item in collection if item not in left]
    return left, right


def contains[T](this: Iterable[T], that: Iterable[T]) -> bool:
    return all(c in this for c in that)
