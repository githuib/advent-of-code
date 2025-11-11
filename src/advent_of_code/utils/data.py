from collections.abc import Callable
from functools import cached_property
from itertools import chain, pairwise, repeat, takewhile, tee
from typing import TYPE_CHECKING, Protocol, Self, runtime_checkable

from more_itertools import before_and_after

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator, Mapping


Predicate = Callable[..., bool]


@runtime_checkable
class Sortable(Protocol):
    def __lt__(self, other: Self) -> bool: ...


class Unique:
    def __init__(self, data: Sortable) -> None:
        self.data = data

    def __lt__(self, other: Self) -> bool:
        return self.data < other.data

    def __repr__(self) -> str:
        return repr(self.data)


class WithClearablePropertyCache:
    def clear_property_cache(self) -> None:
        """Invalidate all cached properties (so they will be recomputed the first time they're accessed again)."""
        cls = self.__class__
        cache = self.__dict__
        for attr in list(cache.keys()):
            if isinstance(getattr(cls, attr, None), cached_property):
                del cache[attr]


def contains[T](this: Iterable[T], that: Iterable[T]) -> bool:
    return all(c in this for c in that)


def invert_dict[K, V](d: Mapping[K, V]) -> dict[V, K]:
    return {v: k for k, v in d.items()}


def pairwise_circular[T](it: Iterable[T]) -> Iterator[tuple[T, T]]:
    a, b = tee(it)
    return zip(a, chain(b, (next(b),)), strict=True)


def tripletwise_circular[T](it: Iterable[T]) -> Iterator[tuple[T, T, T]]:
    a, b, c = tee(it, 3)
    return zip(a, chain(b, (next(b),)), chain(c, (next(c), next(c))), strict=True)


def repeat_transform[T](
    value: T,
    *,
    transform: Callable[[T], T],
    times: int = None,
    while_condition: Callable[[T], bool] = None,
) -> Iterator[T]:
    if while_condition:
        yield from takewhile(
            while_condition, repeat_transform(value, transform=transform, times=times)
        )
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


def smart_range(start: int, stop: int, *, inclusive: bool = False) -> Iterable[int]:
    direction = 1 if start <= stop else -1
    if inclusive:
        stop += direction
    return range(start, stop, direction)


def split_items[T](items: Iterable[T], *, delimiter: T = None) -> Iterator[list[T]]:
    """
    Split any iterable (not just string).

    >>> list(split_items([]))
    [[]]
    >>> list(split_items([1]))
    [[1]]
    >>> list(split_items([None]))
    [[], []]
    >>> list(split_items([1, 2, None]))
    [[1, 2], []]
    >>> list(split_items([None, 1, 2]))
    [[], [1, 2]]
    >>> list(split_items([1, None, 2]))
    [[1], [2]]
    >>> list(split_items([None, 1, None, 2, 3, None]))
    [[], [1], [2, 3], []]
    >>> list(split_items([1, None, None, 2, 3]))
    [[1], [], [2, 3]]
    >>> list(split_items([1, None, 2, 3, None, None, 4, 5, 6, None, None, None]))
    [[1], [2, 3], [], [4, 5, 6], [], [], []]
    >>> list(
    ...     split_items(
    ...         [1, 2, 3, 1, 1, 2, 2, 3, 3, 1, 1, 1, 2, 2, 2, 3, 3, 3], delimiter=3
    ...     )
    ... )
    [[1, 2], [1, 1, 2, 2], [], [1, 1, 1, 2, 2, 2], [], [], []]
    """
    it = iter(items)
    while True:
        segment, it = before_and_after(lambda i: i != delimiter, it)
        yield list(segment)
        try:
            next(it)
        except StopIteration:
            break


def grouped_pairs[K, V](pairs: Iterable[tuple[K, V]]) -> dict[K, list[V]]:
    """
    Group items by key(item).

    >>> grouped_pairs(
    ...     [
    ...         ("Alice", 3),
    ...         ("Bob", 6),
    ...         ("Charles", 4),
    ...         ("Alice", 8),
    ...         ("Charles", 5),
    ...         ("Bob", 2),
    ...         ("Charles", 7),
    ...         ("Alice", 9),
    ...         ("Charles", 1),
    ...     ]
    ... )
    {'Alice': [3, 8, 9], 'Bob': [6, 2], 'Charles': [4, 5, 7, 1]}
    """
    result: dict[K, list[V]] = {}
    for k, v in pairs:
        result.setdefault(k, []).append(v)
    return result


def filled_empty[T](rows: Iterable[Iterable[T]], value: T) -> Iterator[list[T]]:
    rows_seq = [list(row) for row in rows]
    max_width = max(len(row) for row in rows_seq)
    for row in rows_seq:
        yield [*row, *([value] * (max_width - len(row)))]


def transposed[T](rows: Iterable[Iterable[T]]) -> Iterator[list[T]]:
    for col in zip(*rows, strict=True):
        yield list(col)


def rotated_cw[T](rows: Iterable[Iterable[T]]) -> Iterator[list[T]]:
    return reversed(list(transposed(rows)))


def rotated_ccw[T](rows: Iterable[Iterable[T]]) -> Iterator[list[T]]:
    return transposed(reversed(list(rows)))


def transposed_lines(lines: Iterable[str]) -> Iterator[str]:
    for col in zip(*lines, strict=True):
        yield "".join(col)


# def map_to_int_ids[D: Iterator | list | tuple | dict](data: D) -> D:
#     ids = {}
#     ids_gen = count()
#
#     def map_to_int_ids_rec(value: D) -> D:
#         if isinstance(value, Iterator):
#             return (map_to_int_ids_rec(v) for v in value)
#         if isinstance(value, list):
#             return [map_to_int_ids_rec(v) for v in value]
#         if isinstance(value, tuple):
#             return tuple(map_to_int_ids_rec(v) for v in value)
#         if isinstance(value, dict):
#             return {k: map_to_int_ids_rec(v) for k, v in value.items()}
#         if not isinstance(value, Hashable):
#             error = f"Item is not hashable: {value}"
#             raise TypeError(error)
#         if value not in ids:
#             ids[value] = next(ids_gen)
#         return ids[value]
#
#     return map_to_int_ids_rec(data)
