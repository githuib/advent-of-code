from collections.abc import Callable
from itertools import chain, pairwise, repeat, takewhile, tee
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator, Mapping


Predicate = Callable[..., bool]


@runtime_checkable
class Sortable(Protocol):
    def __lt__(self, other: object) -> bool: ...


class Unique:
    def __init__(self, data: object) -> None:
        self.data = data

    def __lt__(self, other: object) -> bool:
        if isinstance(other, Unique) and isinstance(self.data, Sortable):
            return self.data < other.data
        return NotImplemented

    def __repr__(self) -> str:
        return repr(self.data)


def contains[T](this: Iterable[T], that: Iterable[T]) -> bool:
    return all(c in this for c in that)


def invert_dict[K, V](d: Mapping[K, V]) -> dict[V, K]:
    return {v: k for k, v in d.items()}


def pairwise_circular[T](it: Iterable[T]) -> Iterator[tuple[T, T]]:
    a, b = tee(it)
    return zip(a, chain(b, (next(b),)), strict=False)


def tripletwise_circular[T](it: Iterable[T]) -> Iterator[tuple[T, T, T]]:
    a, b, c = tee(it, 3)
    return zip(a, chain(b, (next(b),)), chain(c, (next(c), next(c))), strict=False)


def repeat_transform[T](
    value: T,
    transform: Callable[[T], T],
    times: int = None,
    while_condition: Callable[[T], bool] = None,
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


def smart_range(start: int, stop: int, *, inclusive: bool = False) -> Iterable[int]:
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
