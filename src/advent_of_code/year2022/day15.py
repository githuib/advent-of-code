from abc import ABC

from advent_of_code.problems import ParsedProblem
from advent_of_code.utils.geo2d import (
    P2,
    Line2,
    intersect_segments_2,
    manhattan_dist_2,
    ordinal_directions,
)


def coverage(sensor: P2, beacon: P2, y: int) -> P2 | None:
    sx, sy = sensor
    dist = manhattan_dist_2(sensor, beacon)
    dy = abs(y - sy)
    if dy > dist:
        return None
    return sx - dist + dy, sx + dist - dy


def merge(first: P2, *rest: P2) -> list[P2]:
    min1, max1 = first
    if not rest:
        return [first]
    merged = []
    not_merged = []
    for min2, max2 in rest:
        if max1 + 1 >= min2 and min1 <= max2 + 1:
            merged.append((min(min1, min2), max(max1, max2)))
        else:
            not_merged.append((min2, max2))
    if merged:
        return merge(*not_merged, *merged)
    return [*merge(*not_merged), first]


class _Problem(ParsedProblem[tuple[int, int, int, int], int], ABC):
    line_pattern = "Sensor at x={:d}, y={:d}: closest beacon is at x={:d}, y={:d}"

    def __init__(self) -> None:
        self.locations = [((sx, sy), (bx, by)) for sx, sy, bx, by in self.parsed_input]
        self.size = self.var(test=10, puzzle=2_000_000)


class Problem1(_Problem):
    test_solution = 26
    puzzle_solution = 5144286

    def solution(self) -> int:
        merged = merge(
            *(c for s, b in self.locations if (c := coverage(s, b, self.size)))
        )
        return sum(high - low + 1 for low, high in merged) - sum(
            y == self.size and any(low <= x <= high for low, high in merged)
            for x, y in {p for pair in self.locations for p in pair}
        )


def intersect(line_1: Line2, line_2: Line2) -> P2 | None:
    i = intersect_segments_2(line_1, line_2)
    if i is None:
        return None
    x, y = i
    return int(x), int(y)


class Problem2(_Problem):
    test_solution = 56000011
    puzzle_solution = 10229191267339

    def solution(self) -> int:
        tuning_frequency = 4_000_000
        # size = 20 if self.input_mode == InputMode.TEST else tuning_frequency

        sensor_coverage = [(s, manhattan_dist_2(s, b)) for s, b in self.locations]
        edges = [
            [
                (
                    # just outside left/right coverage border
                    (sx + dx * (c + 1), sy),
                    # just outside up/down coverage border
                    (sx, sy + dy * (c + 1)),
                )
                for (sx, sy), c in sensor_coverage
            ]
            for dx, dy in ordinal_directions
        ]

        uncovered_gaps = {
            intersection
            for line_1 in {
                # edges just outside sensors' coverage going /
                ((x1, y1), (x2, y2))
                for (x1, y1), (x2, y2) in edges[0]
                for (ox1, oy1), (ox2, oy2) in edges[1]
                if y1 - x1 == oy1 - ox1 and x1 <= ox1 and ox2 <= x2
            }
            for line_2 in {
                # edges just outside sensors' coverage going \
                ((x1, y1), (x2, y2))
                for (x1, y1), (x2, y2) in edges[2]
                for (ox1, oy1), (ox2, oy2) in edges[3]
                if x1 + y1 == ox1 + oy1 and x1 <= ox1 and ox2 <= x2
            }
            if (intersection := intersect(line_1, line_2))
            and all(manhattan_dist_2(intersection, s) > d for s, d in sensor_coverage)
            # It's a trap!
            # Narrowing it down to boundaries as described in the assignment actually seems pretty
            # useless (using this approach), but could be done by adding this to the condition:
            # and 0 <= p.x <= size and 0 <= p.y <= size
        }

        assert len(uncovered_gaps) == 1
        x, y = uncovered_gaps.pop()
        return int(x) * tuning_frequency + int(y)


TEST_INPUT = """
Sensor at x=2, y=18: closest beacon is at x=-2, y=15
Sensor at x=9, y=16: closest beacon is at x=10, y=16
Sensor at x=13, y=2: closest beacon is at x=15, y=3
Sensor at x=12, y=14: closest beacon is at x=10, y=16
Sensor at x=10, y=20: closest beacon is at x=10, y=16
Sensor at x=14, y=17: closest beacon is at x=10, y=16
Sensor at x=8, y=7: closest beacon is at x=2, y=10
Sensor at x=2, y=0: closest beacon is at x=2, y=10
Sensor at x=0, y=11: closest beacon is at x=2, y=10
Sensor at x=20, y=14: closest beacon is at x=25, y=17
Sensor at x=17, y=20: closest beacon is at x=21, y=22
Sensor at x=16, y=7: closest beacon is at x=15, y=3
Sensor at x=14, y=3: closest beacon is at x=15, y=3
Sensor at x=20, y=1: closest beacon is at x=15, y=3
"""
