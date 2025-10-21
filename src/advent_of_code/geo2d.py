from collections.abc import Callable, Iterable, Iterator, Mapping
from dataclasses import dataclass
from functools import cached_property
from math import hypot
from os import get_terminal_size
from typing import ClassVar, Literal, overload

from advent_of_code.utils import pairwise_circular, pixel, triplewise_circular

P2 = tuple[int, int]
Range = tuple[int, int]
Line2 = tuple[P2, P2]


class Dir2:
    up = (0, -1)
    down = (0, 1)
    left = (-1, 0)
    right = (1, 0)

    direct_neighbors: ClassVar[list[P2]] = [up, down, left, right]

    left_up = (-1, -1)
    left_down = (-1, 1)
    right_up = (1, -1)
    right_down = (1, 1)

    diagonal_neighbors: ClassVar[list[P2]] = [left_down, right_up, left_up, right_down]

    all_neighbors: ClassVar[list[P2]] = [up, down, left, right, left_up, left_down, right_up, right_down]


def neighbors_2(pos: P2, points: Iterable[P2] | None = None, directions: Iterable[P2] | None = None) -> Iterator[P2]:
    x, y = pos
    for dx, dy in (directions or Dir2.direct_neighbors):
        new_pos = x + dx, y + dy
        if points is None or new_pos in points:
            yield new_pos


def manhattan_dist_2(p1: P2, p2: P2) -> int:
    (x1, y1), (x2, y2) = p1, p2
    return abs(x2 - x1) + abs(y2 - y1)


def loop_length(points: Iterable[P2]) -> int:
    """
    >>> loop_length([(6, 0), (6, 5), (4, 5), (4, 7), (0, 5), (2, 5), (2, 2), (0, 2), (0, 0)])
    30
    """
    return sum(manhattan_dist_2(p, q) for p, q in pairwise_circular(points))


def area(points: Iterable[P2]) -> int:
    """
    >>> area([(6, 0), (6, 5), (4, 5), (4, 7), (0, 5), (2, 5), (2, 2), (0, 2), (0, 0)])
    28
    """
    return abs(sum(x2 * (y3 - y1) for (_, y1), (x2, _), (_, y3) in triplewise_circular(points))) // 2


def grid_area(points: Iterable[P2], include_loop: bool = True) -> int:
    """
    >>> grid_area([(6, 0), (6, 5), (4, 5), (4, 7), (0, 5), (2, 5), (2, 2), (0, 2), (0, 0)])
    44
    >>> grid_area([(6, 0), (6, 5), (4, 5), (4, 7), (0, 5), (2, 5), (2, 2), (0, 2), (0, 0)], include_loop=False)
    14
    """
    ps = list(points)
    return area(ps) + (loop_length(ps) if include_loop else -loop_length(ps)) // 2 + 1


def cross_2(p1: P2, p2: P2) -> int:
    (x1, y1), (x2, y2) = p1, p2
    return x1 * y2 - x2 * y1


def intersect_2(line_1: Line2, line_2: Line2, segments: bool) -> tuple[float, float] | None:
    """
    https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection#Given_two_points_on_each_line
    https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection#Given_two_points_on_each_line_segment
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
        return (xs1 * t + xe1 * (1 - t), ys1 * t + ye1 * (1 - t)) if 0 <= t <= 1 else None

    c = cross_2(e1, s1), cross_2(e2, s2)
    return cross_2(c, (dx1, dx2)) / d_cross, cross_2(c, (dy1, dy2)) / d_cross


def intersect_lines_2(line_1: Line2, line_2: Line2) -> tuple[float, float] | None:
    """
    https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection#Given_two_points_on_each_line
    """
    return intersect_2(line_1, line_2, segments=False)


def intersect_segments_2(line_1: Line2, line_2: Line2) -> tuple[float, float] | None:
    """
    https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection#Given_two_points_on_each_line_segment
    """
    return intersect_2(line_1, line_2, segments=True)


class Grid2[E](dict[P2, E]):
    def __init__(
        self,
        d: Mapping[P2, E] | Iterable[P2] | None = None,
        default: E = None,
        infinite: bool = False,
    ):
        if isinstance(d, Mapping):
            super().__init__(d)
        elif isinstance(d, Iterable) and default is not None:
            super().__init__(dict.fromkeys(d, default))
        else:
            super().__init__({})
        self.infinite = infinite
        if infinite:
            # make sure current width & height are cached
            _ = self.size

    @classmethod
    def from_lines(cls: type[Grid2], lines: list[str]) -> Grid2[str]:
        return Grid2({
            (x, y): element
            for y, line in enumerate(lines)
            for x, element in enumerate(line)
        })

    def converted[C](self: Grid2[E], converter: Callable[[E], C]) -> Grid2[C]:
        return Grid2({p: converter(v) for p, v in self.items()})

    def __getitem__(self, key: P2) -> E:
        if self.infinite:
            x, y = key
            return super().__getitem__((x % self.width, y % self.height))
        return super().__getitem__(key)

    @property
    def span(self) -> tuple[P2, P2]:
        xs, ys = zip(*self.keys(), strict=False)
        return (min(xs), min(ys)), (max(xs), max(ys))

    @cached_property
    def width(self) -> int:
        (x_min, _), (x_max, _) = self.span
        return x_max - x_min + 1

    @cached_property
    def height(self) -> int:
        (_, y_min), (_, y_max) = self.span
        return y_max - y_min + 1

    @cached_property
    def size(self) -> P2:
        return self.width, self.height

    @cached_property
    def area(self) -> int:
        return self.width * self.height

    @overload
    def neighbors(
        self,
        pos: P2,
        include_values: Literal[False],
        directions: Iterable[P2] | None = None,
    ) -> Iterator[P2]: ...

    @overload
    def neighbors(
        self,
        pos: P2,
        include_values: Literal[True] = True,
        directions: Iterable[P2] | None = None,
    ) -> Iterator[tuple[P2, E]]: ...

    def neighbors(
        self,
        pos: P2,
        include_values: bool = True,
        directions: Iterable[P2] | None = None,
    ) -> Iterator[P2 | tuple[P2, E]]:
        for n in neighbors_2(pos, None if self.infinite else self, directions):
            yield (n, self[n]) if include_values else n

    def point_with_value(self, value: E) -> P2:
        points = self.points_with_value(value)
        assert len(points) == 1
        return points.pop()

    def points_with_value(self, *value: E) -> set[P2]:
        return self.points_with_values(value)

    def points_with_values(self, values: Iterable[E]) -> set[P2]:
        return {p for p, v in self.items() if v in values}

    def to_str(
        self,
        value_func: Callable[[P2, E | None], str] | None = None,
        min_x: int | None = None,
        max_x: int | None = None,
        min_y: int | None = None,
        max_y: int | None = None,
    ) -> str:
        (x_min, y_min), (x_max, y_max) = self.span
        xl, yl = min_x or x_min, min_y or y_min
        xh, yh = max_x or x_max, max_y or y_max
        max_width = get_terminal_size()[0]
        return "\n".join("".join(
            value_func((x, y), self.get((x, y))) if value_func else pixel(self.get((x, y)))
            for x in range(xl, min(xl + max_width, xh + 1))
        ) for y in range(yl, yh + 1)) + "\n"

    def __repr__(self) -> str:
        return self.to_str()


# class NumberMat2(Mat2[int]):
#     # def __init__(self, d: Mapping[P2, int] = None):
#     #     super().__init__(d)
#     #     # # elif isinstance(d, Iterable):
#     #     # #     super().__init__({p: 1 for p in d})
#     #     # else:
#     #     #     super().__init__({})
#
#     # @classmethod
#     # def from_lines(
#     #     cls: type[Mat2],
#     #     lines: Iterable[Iterable[E]],
#     #     # convert_element: Callable[[str], int] = None,
#     # ) -> Mat2[int]:
#     #     # if convert_element is None:
#     #     #     def convert_element(element):
#     #     #         return 1 if element == '#' else 0
#     #     # converted_lines = [[convert_element(c) for c in line] for line in lines]
#     #     return Mat2({
#     #         (x, y): element
#     #         for y, line in enumerate(converted_lines)
#     #         for x, element in enumerate(line)
#     #     })
#
#     def to_str(
#         self,
#         value_func: Callable[[P2, E], E] = None,
#         min_x: int = None,
#         max_x: int = None,
#         min_y: int = None,
#         max_y: int = None,
#     ) -> str:
#         (x_min, y_min), (x_max, y_max) = self.span
#         xl, yl = min_x or x_min, min_y or y_min
#         xh, yh = max_x or x_max, max_y or y_max
#         max_width = get_terminal_size()[0]
#         foo = self[3, 4]
#         return '\n'.join(''.join(
#             value_func((x, y), self[x, y]) if value_func else pixel(self[x, y])
#             for x in range(xl, min(xl + max_width, xh + 1))
#         ) for y in range(yl, yh + 1)) + '\n'


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
#         d: Mapping[P2D, int] | Iterable[P2D] | Mapping[P2, int] | Iterable[P2] | None = None,
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
#         value_func: Callable[[P2D], str] = None,
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
#             value_func(P2D(x, y)) if value_func else pixel(self.get(P2D(x, y)))
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
