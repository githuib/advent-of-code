from abc import ABC, abstractmethod
from collections.abc import Mapping, MutableMapping, Set
from dataclasses import dataclass
from functools import cache, cached_property
from math import hypot
from os import get_terminal_size
from typing import TYPE_CHECKING, Literal, Self

from based_utils.calx import randf
from based_utils.cli import Colored
from based_utils.colors import Color
from based_utils.data.iterators import (
    Predicate,
    pairwise_circular,
    tripletwise_circular,
)
from based_utils.data.mixins import WithClearablePropertyCache

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator

type P2 = tuple[int, int]
type Range = tuple[int, int]
type Line2 = tuple[P2, P2]


# class D2:
UP = 0, -1
DOWN = 0, 1
LEFT = -1, 0
RIGHT = 1, 0

LEFT_UP = -1, -1
LEFT_DOWN = -1, 1
RIGHT_UP = 1, -1
RIGHT_DOWN = 1, 1


# Side = Literal[LEFT, RIGHT]
sides: list[P2] = [LEFT, RIGHT]

# CardinalDirection = Literal[UP, DOWN] | Side
cardinal_directions: list[P2] = [UP, DOWN, *sides]

# OrdinalDirection = Literal[LEFT_UP, RIGHT_UP, LEFT_DOWN, RIGHT_DOWN]
ordinal_directions: list[P2] = [LEFT_UP, RIGHT_UP, LEFT_DOWN, RIGHT_DOWN]
# ordinal_directions: list[P2] = [LEFT_DOWN, RIGHT_UP, LEFT_UP, RIGHT_DOWN] # <-- Order in 2022/15

# Direction = CardinalDirection | OrdinalDirection
all_directions: list[P2] = [*cardinal_directions, *ordinal_directions]

type Side = Literal["L", "R"]
type CardinalDirection = Literal["U", "D"] | Side


def rotate(direction: CardinalDirection, side: Side) -> CardinalDirection:
    # (curr_dir + (1 if direction == "R" else -1)) % 4
    match (direction, side):
        case ("U", "L") | ("D", "R"):
            return "L"
        case ("U", "R") | ("D", "L"):
            return "R"
        case ("L", "R") | ("R", "L"):
            return "U"
        case ("L", "L") | ("R", "R"):
            return "D"
    raise NotImplementedError


def neighbors_2(
    pos: P2, points: Iterable[P2] = None, directions: Iterable[P2] = None
) -> Iterator[P2]:
    x, y = pos
    for dx, dy in directions or cardinal_directions:
        new_pos = x + dx, y + dy
        if points is None or new_pos in points:
            yield new_pos


def manhattan_dist_2(p1: P2, p2: P2) -> int:
    (x1, y1), (x2, y2) = p1, p2
    return abs(x2 - x1) + abs(y2 - y1)


def loop_length(points: Iterable[P2]) -> int:
    """
    Circumference of polygon.

    >>> loop_length(
    ...     [(6, 0), (6, 5), (4, 5), (4, 7), (0, 5), (2, 5), (2, 2), (0, 2), (0, 0)]
    ... )
    30
    """
    return sum(manhattan_dist_2(p, q) for p, q in pairwise_circular(points))


def area(points: Iterable[P2]) -> int:
    """
    Area of polygon.

    >>> area([(6, 0), (6, 5), (4, 5), (4, 7), (0, 5), (2, 5), (2, 2), (0, 2), (0, 0)])
    28
    """
    return (
        abs(
            sum(
                x2 * (y3 - y1)
                for (_, y1), (x2, _), (_, y3) in tripletwise_circular(points)
            )
        )
        // 2
    )


def grid_area(points: Iterable[P2], *, include_loop: bool = True) -> int:
    """
    Area of grid.

    >>> grid_area(
    ...     [(6, 0), (6, 5), (4, 5), (4, 7), (0, 5), (2, 5), (2, 2), (0, 2), (0, 0)]
    ... )
    44
    >>> grid_area(
    ...     [(6, 0), (6, 5), (4, 5), (4, 7), (0, 5), (2, 5), (2, 2), (0, 2), (0, 0)],
    ...     include_loop=False,
    ... )
    14
    """
    ps = list(points)
    return area(ps) + (loop_length(ps) if include_loop else -loop_length(ps)) // 2 + 1


def cross_2(p1: P2, p2: P2) -> int:
    (x1, y1), (x2, y2) = p1, p2
    return x1 * y2 - x2 * y1


def intersect_2(
    line_1: Line2, line_2: Line2, *, segments: bool
) -> tuple[float, float] | None:
    """
    Intersection of two lines.

    👉 https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection#Given_two_points_on_each_line
    👉 https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection#Given_two_points_on_each_line_segment.
    """
    (xs1, ys1), (xe1, ye1) = s1, e1 = line_1
    (xs2, ys2), (xe2, ye2) = s2, e2 = line_2
    d1 = dx1, dy1 = xe1 - xs1, ye1 - ys1
    d2 = dx2, dy2 = xe2 - xs2, ye2 - ys2
    d_cross = cross_2(d1, d2)

    if d_cross == 0:
        return None

    if segments:
        de = xe1 - xe2, ye1 - ye2
        t = cross_2(de, d2) / d_cross
        return (
            (xs1 * t + xe1 * (1 - t), ys1 * t + ye1 * (1 - t)) if 0 <= t <= 1 else None
        )

    c = cross_2(e1, s1), cross_2(e2, s2)
    return cross_2(c, (dx1, dx2)) / d_cross, cross_2(c, (dy1, dy2)) / d_cross


def intersect_lines_2(line_1: Line2, line_2: Line2) -> tuple[float, float] | None:
    """https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection#Given_two_points_on_each_line."""
    return intersect_2(line_1, line_2, segments=False)


def intersect_segments_2(line_1: Line2, line_2: Line2) -> tuple[float, float] | None:
    """https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection#Given_two_points_on_each_line_segment."""
    return intersect_2(line_1, line_2, segments=True)


@dataclass(frozen=True)
class Crop:
    left: int = 0
    right: int = 0
    top: int = 0
    bottom: int = 0


class Grid2[T](Mapping[P2, T], ABC):
    _default_value: T

    class NoDefaultError(Exception):
        def __init__(self) -> None:
            super().__init__("Default value needs to be provided")

    def __init__(
        self,
        items: Mapping[P2, T] | Iterable[tuple[P2, T]] | None = None,
        *,
        default_value: T = None,
        cyclic: bool = False,
    ) -> None:
        if default_value is not None:
            self._default_value = default_value

        self._grid: dict[P2, T] = dict(items or {})

        self.cyclic = cyclic

    def __len__(self) -> int:
        return len(self._grid)

    def __iter__(self) -> Iterator[P2]:
        return iter(self._grid)

    def __getitem__(self, pos: P2) -> T:
        if not self._grid:
            raise KeyError(pos)

        x, y = pos
        if self.cyclic:
            x, y = x % self.width, y % self.height
        else:
            (x_min, y_min), (x_max, y_max) = self.span
            if not (x_min <= x <= x_max and y_min <= y <= y_max):
                raise KeyError(pos)

        try:
            return self._grid[x, y]
        except KeyError:
            return self._default_value

    def __contains__(self, pos: object) -> bool:
        return pos in self._grid

    def __or__(self, other: Mapping[P2, T]) -> Self:
        return self.__class__(self._grid | dict(other))

    @cached_property
    def x_range(self) -> tuple[int, int]:
        xs = [x for x, _ in self.keys()]
        return min(xs), max(xs)

    @cached_property
    def y_range(self) -> tuple[int, int]:
        ys = [y for _, y in self.keys()]
        return min(ys), max(ys)

    @cached_property
    def span(self) -> tuple[P2, P2]:
        x_min, x_max = self.x_range
        y_min, y_max = self.y_range
        return (x_min, y_min), (x_max, y_max)

    @cached_property
    def width(self) -> int:
        x_min, x_max = self.x_range
        return x_max - x_min + 1

    @cached_property
    def height(self) -> int:
        y_min, y_max = self.y_range
        return y_max - y_min + 1

    @cached_property
    def size(self) -> P2:
        return self.width, self.height

    @cached_property
    def area(self) -> int:
        return self.width * self.height

    @property
    def rows(self) -> Iterator[list[T]]:
        (x_min, y_min), (x_max, y_max) = self.span
        for y in range(y_min, y_max + 1):
            yield [self[x, y] for x in range(x_min, x_max + 1)]

    @property
    def columns(self) -> Iterator[list[T]]:
        (x_min, y_min), (x_max, y_max) = self.span
        for x in range(x_min, x_max + 1):
            yield [self[x, y] for y in range(y_min, y_max + 1)]

    def point_with_value(self, value: T) -> P2:
        try:
            point, *_ = self.points_with_value(value)
        except ValueError as e:
            raise LookupError from e
        else:
            return point

    def points_with_value(self, *values: T) -> frozenset[P2]:
        return frozenset(p for p, v in self.items() if v in values)

    def points_where(self, predicate: Predicate[T]) -> frozenset[P2]:
        return frozenset(p for p, v in self.items() if predicate(v))

    def neighbors(
        self, pos: P2, directions: Iterable[P2] = None
    ) -> Iterator[tuple[P2, T]]:
        for n in neighbors_2(pos, None if self.cyclic else self, directions):
            yield n, self[n]

    @classmethod
    @abstractmethod
    def _parse_value(cls, value_str: str) -> T: ...

    @classmethod
    def from_lines(
        cls: type[Self],
        lines: Iterable[str],
        *,
        parse_value: Callable[[str], T] = None,
        ignore: str = " ",
    ) -> Self:
        return cls(
            ((x, y), (parse_value or cls._parse_value)(c))
            for y, line in enumerate(lines)
            for x, c in enumerate(line)
            if c not in ignore
        )

    @abstractmethod
    def _format_value(self, pos: P2, value: T) -> Colored: ...

    def to_lines(
        self,
        *,
        format_value: Callable[[P2, T, Colored], Colored] = None,
        highlighted: Set[P2] = None,
        crop: Crop = None,
        crop_to_terminal: bool = True,
    ) -> Iterator[str]:
        (x_lo, y_lo), (x_hi, y_hi) = self.span

        if crop_to_terminal:
            max_width, max_height = get_terminal_size()
            # Keep centered horizontally
            x_cropped = max(0, self.width - max_width)
            x_lo += x_cropped // 2
            x_hi -= (x_cropped - 1) // 2 + 1
            # Crop from bottom
            y_cropped = max(0, self.height - max_height + 1)
            y_hi -= y_cropped

        if crop:
            x_lo += crop.left
            x_hi -= crop.right
            y_lo += crop.top
            y_hi -= crop.bottom

        def fmt(pos: P2) -> str:
            value = self[pos]
            s = self._format_value(pos, value)
            if format_value:
                s = format_value(pos, value, s)
            if pos in (highlighted or {}):
                c = (s.color or Color.from_name("green")).but_with(lightness=0.8)
                s = s.with_color(c).with_background(c.with_changed(lightness=0.5))
            return s.formatted

        for y in range(y_lo, y_hi + 1):
            yield "".join(fmt((x, y)) for x in range(x_lo, x_hi + 1))


@cache
def _colors(n: int) -> list[Color]:
    h = randf()
    return [
        Color.from_fields(
            lightness=i / n, saturation=(i / n) ** 0.5, hue=h + i * (n // 2 + 1) / n
        )
        for i in range(n)
    ]


class CharGrid2(Grid2[str]):
    _default_value = ""

    @classmethod
    def _parse_value(cls, value_str: str) -> str:
        return value_str

    def _format_value(self, _pos: P2, value: str) -> Colored:
        values = ".#^"
        try:
            n = values.index(value)
        except ValueError:
            n = 3
        color = _colors(5)[n]
        return Colored(value, color, color.with_changed(lightness=0.75))


class NumGrid2(Grid2[int]):
    _default_value = 0

    @classmethod
    def _parse_value(cls, value_str: str) -> int:
        return int(value_str)

    def _format_value(self, _pos: P2, value: int) -> Colored:
        if value < 0:
            return Colored(".")
        return Colored(
            str(value) if value < 10 else "+",
            Color.from_name("green").shade(0.15 + min(value, 10) * 0.035),
        )


class BitGrid2(Grid2[bool]):
    _default_value = False

    @classmethod
    def _parse_value(cls, value_str: str) -> bool:
        return value_str == "#"

    def _format_value(
        self,
        _pos: P2,
        value: bool,  # noqa: FBT001
    ) -> Colored:
        c_bad, c_good, _ = _colors()
        color = c_good if value else c_bad
        return Colored("#" if value else ".", color, color.with_changed(lightness=0.75))


class _MutableGrid2[T](
    Grid2[T], MutableMapping[P2, T], WithClearablePropertyCache, ABC
):
    def __init__(
        self,
        items: Mapping[P2, T] | Iterable[tuple[P2, T]] | None = None,
        *,
        default_value: T = None,
        cyclic: bool = False,
        allow_extention: bool = False,
    ) -> None:
        super().__init__(items, default_value=default_value, cyclic=cyclic)
        self._allow_extention = allow_extention or not items

    def __setitem__(self, pos: P2, value: T, /) -> None:
        """
        Update the value at the given position.

        >>> class MNG(NumGrid2, _MutableGrid2[int]):
        ...     pass
        >>> grid = MNG({(0, 0): 1, (1, 2): 1, (2, 1): 1}, default_value=2)
        >>> list(grid.rows)
        [[1, 2, 2], [2, 2, 1], [2, 1, 2]]
        >>> grid[0, 2] = 3
        >>> list(grid.rows)
        [[1, 2, 2], [2, 2, 1], [3, 1, 2]]
        >>> grid[2, 3] = 3
        Traceback (most recent call last):
            ...
        KeyError: (2, 3)
        >>> grid.update({(0, 1): 3, (3, 0): 3, (3, 2): 3})
        Traceback (most recent call last):
            ...
        KeyError: (3, 0)
        >>> grid_2 = MNG(
        ...     {(0, 0): 1, (1, 2): 1, (2, 1): 1}, default_value=2, allow_extention=True
        ... )
        >>> list(grid_2.rows)
        [[1, 2, 2], [2, 2, 1], [2, 1, 2]]
        >>> grid_2[0, 2] = 3
        >>> grid_2[2, 3] = 3
        >>> list(grid_2.rows)
        [[1, 2, 2], [2, 2, 1], [3, 1, 2], [2, 2, 3]]
        >>> grid_2.update({(0, 1): 3, (3, 0): 3, (3, 2): 3})
        >>> list(grid_2.rows)
        [[1, 2, 2, 3], [3, 2, 1, 2], [3, 1, 2, 3], [2, 2, 3, 2]]
        >>> grid_3 = MNG(default_value=2)
        >>> grid_3[0, 2] = 3
        >>> grid_3[2, 3] = 3
        >>> list(grid_3.rows)
        [[3, 2, 2], [2, 2, 3]]
        >>> grid_3.update({(0, 1): 3, (3, 0): 3, (3, 2): 3})
        >>> list(grid_3.rows)
        [[2, 2, 2, 3], [3, 2, 2, 2], [3, 2, 2, 3], [2, 2, 3, 2]]
        """
        try:
            _ = self[pos]
        except KeyError:
            will_extend = True
        else:
            will_extend = False

        if will_extend:
            if not self._allow_extention:
                # We're not allowed to set an item we can't access
                # (or: only allowed to "update", not to extend the grid).
                raise KeyError(pos)
            # Clear cached properties so they will be recalculated based on the extended grid.
            self.clear_property_cache()

        self._grid[pos] = value

    def __delitem__(self, pos: P2, /) -> None:
        del self._grid[pos]

    def __or__(self, other: Mapping[P2, T]) -> Self:
        return self.__class__(
            self._grid | dict(other), allow_extention=self._allow_extention
        )


class MutableCharGrid2(CharGrid2, _MutableGrid2[str]):
    pass


class MutableNumGrid2(NumGrid2, _MutableGrid2[int]):
    pass


class MutableBitGrid2(BitGrid2, _MutableGrid2[int]):
    pass


@dataclass(frozen=True)
class P2D:
    x: int = 0
    y: int = 0

    @property
    def as_tuple(self) -> P2:
        return self.x, self.y

    def __neg__(self) -> P2D:
        return P2D(-self.x, -self.y)

    def __add__(self, other: object) -> P2D:
        if isinstance(other, P2D):
            ox, oy = other.x, other.y
        elif isinstance(other, tuple):
            ox, oy = other
        else:
            return NotImplemented
        return P2D(self.x + ox, self.y + oy)

    def __sub__(self, other: object) -> P2D:
        if isinstance(other, P2D):
            return P2D(self.x - other.x, self.y - other.y)
        return NotImplemented

    def __mul__(self, factor: int) -> P2D:
        return P2D(self.x * factor, self.y * factor)

    # def __truediv__(self, factor: Number) -> P2D:
    #     return P2D(self.x / factor, self.y / factor)

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, P2D):
            return (self.x, self.y) == (other.x, other.y)
        return NotImplemented

    def __lt__(self, other: P2D) -> bool:
        return self.length < other.length

    def __abs__(self) -> P2D:
        return P2D(abs(self.x), abs(self.y))

    def __rshift__(self, other: P2D) -> int:
        return self.manhattan_distance_to(other)

    @property
    def length(self) -> float:
        return hypot(self.x, self.y)

    def distance_to(self, other: P2D) -> float:
        return (other - self).length

    @property
    def manhattan_length(self) -> int:
        return abs(self.x) + abs(self.y)

    def manhattan_distance_to(self, other: P2D) -> int:
        return (other - self).manhattan_length

    # @property
    # def angle(self) -> float:
    #     return (atan2(self.x, -self.y) + pi * 2) % (pi * 2)


# @dataclass
# class Span2D:
#     p1: P2D
#     p2: P2D
#
#     def __contains__(self, p: P2D) -> bool:
#         return (
#             self.p1.x <= p.x <= self.p2.x and
#             self.p1.y <= p.y <= self.p2.y
#         )
#
#     @property
#     def points(self) -> Iterator[P2D]:
#         for x in range(self.p1.x, self.p2.x + 1):
#             for y in range(self.p1.y, self.p2.y + 1):
#                 yield P2D(x, y)


# class Matrix2D(dict[P2D, int]):
#     def __init__(
#         self,
#         d: Mapping[P2D, int] | Iterable[P2D] | Mapping[P2, int] | Iterable[P2] = None,
#     ):
#         d = d or {}
#         items: Iterable[tuple[P2D | P2, int]]
#         if isinstance(d, Mapping):
#             items = d.items()
#         else:
#             items = [(i, 1) for i in d]
#         super().__init__({(P2D(*p) if isinstance(p, tuple) else p): v for p, v in items})
#
#     def __getitem__(self, key: object) -> int:
#         if isinstance(key, P2D):
#             return super().__getitem__(key)
#         if isinstance(key, tuple):
#             return super().__getitem__(P2D(*key))
#         raise NotImplementedError
#
#     def __setitem__(self, key: object, value: int) -> None:
#         if isinstance(key, P2D):
#             super().__setitem__(key, value)
#         elif isinstance(key, tuple):
#             super().__setitem__(P2D(*key), value)
#         else:
#             raise NotImplementedError
#
#     def __contains__(self, key: object) -> bool:
#         if isinstance(key, P2D):
#             return super().__contains__(key)
#         if isinstance(key, tuple):
#             return super().__contains__(P2D(*key))
#         raise NotImplementedError
#
#     # @overload
#     # def get(self, point: MatrixKeyT, default: int) -> int: ...  # type: ignore[override]
#     #
#     # @overload
#     # def get(self, point: MatrixKeyT, default: None) -> int | None: ...  # type: ignore[override]
#
#     def get(self, point: P2D, default: int = None) -> int | None:  # type: ignore[override]
#         try:
#             return self[point]
#         except KeyError:
#             return default
#
#     @property
#     def span(self) -> tuple[P2D, P2D]:
#         x, y = zip(*self.keys())
#         return P2D(min(x), min(y)), P2D(max(x), max(y))
#
#     @cached_property
#     def width(self) -> int:
#         p_min, p_max = self.span
#         return p_max.x - p_min.x + 1
#
#     @cached_property
#     def height(self) -> int:
#         p_min, p_max = self.span
#         return p_max.y - p_min.y + 1
#
#     @property
#     def size(self):
#         return self.width * self.height
#
#     def neighbors(self, pos: P2D) -> Iterator[P2D]:
#         for d in Dir2.all:
#             new_pos = pos + d
#             if new_pos in self:
#                 yield new_pos
#
#     def to_str(
#         self,
#         format_value: Callable[[P2D], str] = None,
#         min_x: int = None,
#         max_x: int = None,
#         min_y: int = None,
#         max_y: int = None,
#     ) -> str:
#         p_min, p_max = self.span
#         xl, yl = min_x or p_min.x, min_y or p_min.y
#         xh, yh = max_x or p_max.x, max_y or p_max.y
#         max_width = get_terminal_size()[0]
#         return '\n'.join(''.join(
#             format_value(P2D(x, y)) if format_value else pixel(self.get(P2D(x, y)))
#             for x in range(xl, min(xl + max_width, xh + 1))
#         ) for y in range(yl, yh + 1)) + '\n'
#
#     def __str__(self) -> str:
#         return self.to_str()


# @dataclass
# class Line2D:
#     p1: P2T
#     p2: P2T
#
#     def intersection(self, other: Line2D) -> P2T | None:
#         return intersect_2((self.p1, self.p2), (other.p1, other.p2))
#         # (x1, y1), (x2, y2) = self.p1, self.p2
#         # (ox1, oy1), (ox2, oy2) = other.p1, other.p2
#         # dsx, dsy = x2 - x1, y2 - y1
#         # dx, dy = x2 - ox2, y2 - oy2
#         # dox, doy = ox2 - ox1, oy2 - oy1
#         # t = (dx * doy - dy * dox) / (dsx * doy - dsy * dox)
#         # return (
#         #     int(x1 * t + x2 * (1 - t)),
#         #     int(y1 * t + y2 * (1 - t)),
#         # ) if 0 <= t <= 1 else None
#
#     def __hash__(self):
#         return hash((self.p1, self.p2))
#
#     def __and__(self, other: Line2D) -> P2T | None:
#         return self.intersection(other)


# class P2(NamedTuple):
#     x: int
#     y: int
#
#     def __neg__(self) -> P2:
#         x, y, = self
#         return P2(-x, -y)
#
#     def __add__(self, other: object) -> P2:
#         if isinstance(other, P2):
#             x, y = self
#             ox, oy = other
#             return P2(x + ox, y + oy)
#         return NotImplemented
#
#     def __sub__(self, other: object) -> P2:
#         if isinstance(other, P2):
#             x, y = self
#             ox, oy = other
#             return P2(x - ox, y - oy)
#         return NotImplemented
#
#     def __mul__(self, factor: int) -> P2:  # type: ignore[override]
#         x, y = self
#         return P2(x * factor, y * factor)
#
#     # def __hash__(self) -> int:
#     #     return hash(*self)
#
#     # def __eq__(self, other: object) -> bool:
#     #     if isinstance(other, P2):
#     #         return self == other.x, other.y
#     #     return NotImplemented
#
#     def __lt__(self, other: object) -> bool:
#         if isinstance(other, P2):
#             return self.length < other.length
#         return NotImplemented
#
#     def __abs__(self) -> P2:
#         x, y = self
#         return P2(abs(x), abs(y))
#
#     def __rshift__(self, other: P2) -> int:
#         return self.manhattan_distance_to(other)
#
#     @property
#     def length(self) -> float:
#         x, y = self
#         return sqrt(x**2 + y**2)
#
#     def distance_to(self, other: P2) -> float:
#         return (other - self).length
#
#     @property
#     def manhattan_length(self) -> int:
#         return abs(self.x) + abs(self.y)
#
#     def manhattan_distance_to(self, other: P2) -> int:
#         return (other - self).manhattan_length
#
#     @property
#     def angle(self) -> float:
#         x, y = self
#         return (atan2(x, -y) + pi * 2) % (pi * 2)
