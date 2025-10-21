from collections.abc import Iterable, Iterator, Mapping
from functools import cached_property
from typing import NamedTuple

P3 = tuple[int, int, int]


class P3D(NamedTuple):
    x: int = 0
    y: int = 0
    z: int = 0

    @classmethod
    def from_str(cls: type[P3D], s: str) -> P3D:
        x, y, z = s.split(",")
        return cls(int(x.strip()), int(y.strip()), int(z.strip()))

    @classmethod
    def unity(cls: type[P3D]) -> P3D:
        return cls(1, 1, 1)

    @property
    def manhattan_length(self) -> int:
        x, y, z = self
        return abs(x) + abs(y) + abs(z)

    def manhattan_distance_to(self, other: P3D) -> int:
        return (other - self).manhattan_length

    def __neg__(self):
        x, y, z = self
        return P3D(-x, -y, -z)

    def __abs__(self) -> P3D:
        x, y, z = self
        return P3D(abs(x), abs(y), abs(z))

    def __add__(self, other: object) -> P3D:
        if isinstance(other, P3D):
            x, y, z = self
            ox, oy, oz = other
            return P3D(x + ox, y + oy, z + oz)
        return NotImplemented

    def __sub__(self, other: object) -> P3D:
        if isinstance(other, P3D):
            x, y, z = self
            ox, oy, oz = other
            return P3D(x - ox, y - oy, z - oz)
        return NotImplemented

    def __mul__(self, factor: int) -> P3D:  # type: ignore[override]
        x, y, z = self
        return P3D(x * factor, y * factor, z * factor)

    def __floordiv__(self, factor: int) -> P3D:
        x, y, z = self
        return P3D(x // factor, y // factor, z // factor)

    # def __truediv__(self, factor: Number) -> Point3D:
    #     return Point3D(self.x / factor, self.y / factor, self.z / factor)

    def __xor__(self, other: object) -> P3D:
        if isinstance(other, P3D):
            return self.cross(other)
        return NotImplemented

    def __rshift__(self, other: object) -> int:
        if isinstance(other, P3D):
            return self.manhattan_distance_to(other)
        return NotImplemented

    @property
    def volume(self) -> int:
        x, y, z = self
        return x * y * z

    def cross(self, other: P3D) -> P3D:
        x, y, z = self
        ox, oy, oz = other
        return P3D(
            y * oz - z * oy,
            z * ox - x * oz,
            x * oy - y * ox,
        )

    def transform(self: P3D, transformation: Trans3) -> P3D:
        """
                               z       x       y
        (x, y, z) transform (2, a), (0, b), (1, c) =  (z * a, x * b, y * c)
        """
        return P3D(*[self[i] * n for i, n in transformation])  # pylint: disable=unsubscriptable-object

    def inv_transform(self, transformation: Trans3) -> P3D:
        """
            0        1        2              0        1        2
        [(2, dx), (0, dy), (1, dz)]  ->  [(1, dy), (2, dz), (0, dx)]
                               z       x       y
        (x, y, z) inv_trans (2, a), (0, b), (1, c)
                               y       z       x
        (x, y, z) transform (1, b), (2, c), (0, a) =  (y * b, z * c, x * a)
        """
        td = {n: (i, d) for i, (n, d) in enumerate(transformation)}
        return P3D(*[self[i] * n for i, n in (td[0], td[1], td[2])])  # pylint: disable=unsubscriptable-object

    @classmethod
    def min(cls, p1: P3D, p2: P3D) -> P3D:
        x1, y1, z1 = p1
        x2, y2, z2 = p2
        return P3D(min(x1, x2), min(y1, y2), min(z1, z2))

    @classmethod
    def max(cls, p1: P3D, p2: P3D) -> P3D:
        x1, y1, z1 = p1
        x2, y2, z2 = p2
        return P3D(max(x1, x2), max(y1, y2), max(z1, z2))

    # def __repr__(self):
    #     return f'({self.x}, {self.y}, {self.z})'

    def rotated_90_x(self, clockwise: bool = True) -> P3D:
        return self.transform(Rotation90deg3D.x_cw if clockwise else Rotation90deg3D.x_ccw)

    def rotated_90_y(self, clockwise: bool = True) -> P3D:
        return self.transform(Rotation90deg3D.y_cw if clockwise else Rotation90deg3D.y_ccw)

    def rotated_90_z(self, clockwise: bool = True) -> P3D:
        return self.transform(Rotation90deg3D.z_cw if clockwise else Rotation90deg3D.z_ccw)


class Dir3D:
    left = P3D(-1, 0, 0)
    right = P3D(1, 0, 0)
    up = P3D(0, -1, 0)
    down = P3D(0, 1, 0)
    front = P3D(0, 0, -1)
    back = P3D(0, 0, 1)
    all = (left, right, up, down, front, back)


class Span3D:
    def __init__(self, p1: P3D, p2: P3D, fix_order: bool = False):
        if fix_order:
            # (x1, y1, z1), (x2, y2, z2) = p1, p2
            # self.p_min = P3D(min(x1, x2), min(y1, y2), min(z1, z2))
            # self.p_max = P3D(max(x1, x2), max(y1, y2), max(z1, z2))
            self.p_min, self.p_max = P3D.min(p1, p2), P3D.max(p1, p2)
        else:
            self.p_min, self.p_max = p1, p2

    def __hash__(self) -> int:
        return hash((self.p_min, self.p_max))

    def __contains__(self, other: object) -> bool:
        if isinstance(other, P3D):
            x_min, y_min, z_min = self.p_min
            x_max, y_max, z_max = self.p_max
            x, y, z = other
            return (
                x_min <= x <= x_max and
                y_min <= y <= y_max and
                z_min <= z <= z_max
            )
        if isinstance(other, Span3D):
            return other == self & other
        return NotImplemented

    def __and__(self, other: Span3D) -> Span3D:
        p_min = P3D.max(self.p_min, other.p_min)
        p_max = P3D.min(self.p_max, other.p_max)
        return Span3D(p_min, P3D.max(p_min - P3D.unity(), p_max))

    def __eq__(self, other: object):
        if isinstance(other, Span3D):
            return (self.p_min, self.p_max) == (other.p_min, other.p_max)
        return NotImplemented

    def __bool__(self) -> bool:
        return self.volume != 0

    def __repr__(self):
        return f"{self.p_min} {self.p_max}"

    @property
    def volume(self) -> int:
        return (self.p_max + P3D.unity() - self.p_min).volume

    @property
    def points(self) -> Iterator[P3D]:
        for x in range(self.p_min.x, self.p_max.x + 1):
            for y in range(self.p_min.y, self.p_max.y + 1):
                for z in range(self.p_min.z, self.p_max.z + 1):
                    yield P3D(x, y, z)


class Grid3D(dict[P3D, int]):
    def __init__(self, d: Mapping[P3D, int] | Iterable[P3D] | None = None, default: int = 1):
        if isinstance(d, Mapping):
            super().__init__(d)
        elif isinstance(d, Iterable):
            super().__init__(dict.fromkeys(d, default))
        else:
            super().__init__({})

    @property
    def span(self) -> tuple[P3D, P3D]:
        xs, ys, zs = zip(*self.keys(), strict=False)
        return P3D(min(xs), min(ys), min(zs)), P3D(max(xs), max(ys), max(zs))

    @cached_property
    def width(self) -> int:
        p_min, p_max = self.span
        return p_max.x - p_min.x + 1

    @cached_property
    def height(self) -> int:
        p_min, p_max = self.span
        return p_max.y - p_min.y + 1

    @cached_property
    def depth(self) -> int:
        p_min, p_max = self.span
        return p_max.z - p_min.z + 1

    @cached_property
    def size(self) -> P3D:
        return P3D(self.width, self.height, self.depth)

    @property
    def volume(self) -> int:
        return self.width * self.height * self.depth

    def neighbors(self, pos: P3D) -> Iterator[P3D]:
        for d in Dir3D.all:
            new_pos = pos + d
            if new_pos in self:
                yield new_pos

    def transform(self, transformation: Trans3) -> Grid3D:
        return Grid3D({p.transform(transformation): v for p, v in self.items()})

    def rotated_90_x(self, clockwise: bool = True) -> Grid3D:
        return Grid3D({p.rotated_90_x(clockwise): v for p, v in self.items()})

    def rotated_90_y(self, clockwise: bool = True) -> Grid3D:
        return Grid3D({p.rotated_90_y(clockwise): v for p, v in self.items()})

    def rotated_90_z(self, clockwise: bool = True) -> Grid3D:
        return Grid3D({p.rotated_90_z(clockwise): v for p, v in self.items()})


class Trans3(NamedTuple):
    """
    Could result in a rotation, mirroring or a combination of both, in "90 degree" terms.
                           z       x       y
    (x, y, z) transform (2, a), (0, b), (1, c) =  (z * a, x * b, y * c)
    """
    a: tuple[int, int]
    b: tuple[int, int]
    c: tuple[int, int]

    @property
    def inverse(self) -> Trans3:
        """
            0        1        2              0        1        2
        [(2, dx), (0, dy), (1, dz)]  ->  [(1, dy), (2, dz), (0, dx)]
        """
        td = {n: (i, d) for i, (n, d) in enumerate(self)}
        return Trans3(td[0], td[1], td[2])

    def __invert__(self):
        return self.inverse


class Rotation90deg3D:
    x_cw = Trans3((0, 1), (2, 1), (1, -1))  # (x, y, z) -> (x, z, -y)
    x_ccw = Trans3((0, 1), (2, -1), (1, 1))  # (x, y, z) -> (x, -z, y)
    y_cw = Trans3((2, 1), (1, 1), (0, -1))  # (x, y, z) -> (z, y, -x)
    y_ccw = Trans3((2, -1), (1, 1), (0, 1))  # (x, y, z) -> (-z, y, x)
    z_cw = Trans3((1, -1), (0, 1), (2, 1))  # (x, y, z) -> (-y, x, z)
    z_ccw = Trans3((1, 1), (0, -1), (2, 1))  # (x, y, z) -> (y, -x, z)


# all 24 possible (90 degree) orientations of a 3D object
# (imagine a cube: keep of its 6 sides pointing in a fixed direction, it can be rotated 4 times)
ROTATIONS_3D = [
    Trans3((0, 1), (1, 1), (2, 1)),  # no rotation

    Trans3((0, 1), (2, 1), (1, -1)),  # x cw
    Trans3((0, 1), (1, -1), (2, -1)),  # x 180
    Trans3((0, 1), (2, -1), (1, 1)),  # x ccw

    Trans3((2, 1), (1, 1), (0, -1)),  # y cw
    Trans3((0, -1), (1, 1), (2, -1)),  # y 180
    Trans3((2, -1), (1, 1), (0, 1)),  # y ccw

    Trans3((1, -1), (0, 1), (2, 1)),  # z cw
    Trans3((0, -1), (1, -1), (2, 1)),  # z 180
    Trans3((1, 1), (0, -1), (2, 1)),  # z ccw

    Trans3((0, -1), (2, 1), (1, 1)),  # -yz 180
    Trans3((0, -1), (2, -1), (1, -1)),  # yz 180

    Trans3((2, 1), (1, -1), (0, 1)),  # xz 180
    Trans3((2, -1), (1, -1), (0, -1)),  # -xz 180

    Trans3((1, 1), (0, 1), (2, -1)),  # xy 180
    Trans3((1, -1), (0, -1), (2, -1)),  # -xy 180

    Trans3((1, 1), (2, 1), (0, 1)),  # xyz cw
    Trans3((1, 1), (2, -1), (0, -1)),
    Trans3((1, -1), (2, 1), (0, -1)),
    Trans3((1, -1), (2, -1), (0, 1)),
    Trans3((2, 1), (0, 1), (1, 1)),
    Trans3((2, 1), (0, -1), (1, -1)),
    Trans3((2, -1), (0, 1), (1, -1)),
    Trans3((2, -1), (0, -1), (1, 1)),
]

# ROTATIONS_3D = [
#     Transform3D(
#         (x, a),
#         (y, b),
#         (z, a * b * (((y - x) + 1) % 3 - 1)),
#     )
#     for x, y, z in permutations((0, 1, 2))
#     for a in (1, -1)
#     for b in (1, -1)
# ]


# @dataclass(frozen=True)
# class P3D(Generic[N]):
#     x: N
#     y: N
#     z: N
#
#     @property
#     def as_tuple(self) -> tuple[N, N, N]:
#         return self.x, self.y, self.z
#
#     @classmethod
#     def unity(cls):
#         return cls(1, 1, 1)
#
#     @property
#     def manhattan_length(self) -> N:
#         return abs(self.x) + abs(self.y) + abs(self.z)
#
#     def manhattan_distance_to(self, other: P3D) -> N:
#         return (other - self).manhattan_length
#
#     def __neg__(self) -> P3D:
#         return P3D(-self.x, -self.y, -self.z)
#
#     def __abs__(self) -> P3D:
#         return P3D(abs(self.x), abs(self.y), abs(self.z))
#
#     def __add__(self, other: object) -> P3D:
#         if not isinstance(other, P3D):
#             return NotImplemented
#         return P3D(self.x + other.x, self.y + other.y, self.z + other.z)
#
#     def __sub__(self, other: object) -> P3D:
#         if not isinstance(other, P3D):
#             return NotImplemented
#         return P3D(self.x - other.x, self.y - other.y, self.z - other.z)
#
#     def __mul__(self, factor: N) -> P3D:  # type: ignore[override]
#         return P3D(self.x * factor, self.y * factor, self.z * factor)
#
#     def __floordiv__(self, factor: N) -> P3D:
#         return P3D(self.x // factor, self.y // factor, self.z // factor)
#
#     # def __truediv__(self, factor: Number) -> Point3D:
#     #     return Point3D(self.x / factor, self.y / factor, self.z / factor)
#
#     def __xor__(self, other: object) -> P3D:
#         if not isinstance(other, P3D):
#             return NotImplemented
#         return self.cross(other)
#
#     def __rshift__(self, other: object) -> N:
#         if not isinstance(other, P3D):
#             return NotImplemented
#         return self.manhattan_distance_to(other)
#
#     @property
#     def volume(self) -> N:
#         return self.x * self.y * self.z
#
#     def cross(self, other: P3D) -> P3D:
#         return P3D(
#             self.y * other.z - self.z * other.y,
#             self.z * other.x - self.x * other.z,
#             self.x * other.y - self.y * other.x,
#         )
#
#     def transform(self, transformation: Trans3) -> P3D:
#         """
#                                z       x       y
#         (x, y, z) transform (2, a), (0, b), (1, c) =  (z * a, x * b, y * c)
#         """
#         return P3D(*[self.as_tuple[i] * n for i, n in transformation])
#
#     def inv_transform(self, transformation: Trans3) -> P3D:
#         """
#             0        1        2              0        1        2
#         [(2, dx), (0, dy), (1, dz)]  ->  [(1, dy), (2, dz), (0, dx)]
#                                z       x       y
#         (x, y, z) inv_trans (2, a), (0, b), (1, c)
#                                y       z       x
#         (x, y, z) transform (1, b), (2, c), (0, a) =  (y * b, z * c, x * a)
#         """
#         td = {n: (i, d) for i, (n, d) in enumerate(transformation)}
#         return P3D(*[self.as_tuple[i] * n for i, n in (td[0], td[1], td[2])])
#
#     @classmethod
#     def min(cls, p1: P3D, p2: P3D) -> P3D:
#         return P3D(min(p1.x, p2.x), min(p1.y, p2.y), min(p1.z, p2.z))
#
#     @classmethod
#     def max(cls, p1: P3D, p2: P3D) -> P3D:
#         return P3D(max(p1.x, p2.x), max(p1.y, p2.y), max(p1.z, p2.z))
#
#     # def __repr__(self):
#     #     return f'({self.x}, {self.y}, {self.z})'
#
#     def rotated_90_x(self, clockwise: bool = True) -> P3D:
#         return self.transform(Rotation90deg3D.x_cw if clockwise else Rotation90deg3D.x_ccw)
#
#     def rotated_90_y(self, clockwise: bool = True) -> P3D:
#         return self.transform(Rotation90deg3D.y_cw if clockwise else Rotation90deg3D.y_ccw)
#
#     def rotated_90_z(self, clockwise: bool = True) -> P3D:
#         return self.transform(Rotation90deg3D.z_cw if clockwise else Rotation90deg3D.z_ccw)
