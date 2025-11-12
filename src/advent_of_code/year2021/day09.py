from abc import ABC
from collections import Counter, defaultdict
from math import prod

from advent_of_code.problems import MultiLineProblem


class _Problem(MultiLineProblem[int], ABC):
    def __init__(self) -> None:
        self.height_map = defaultdict(
            lambda: 9,
            [
                ((x, y), int(val))
                for y, line in enumerate(self.lines)
                for x, val in enumerate(line)
            ],
        )


class Problem1(_Problem):
    test_solution = 15
    puzzle_solution = 591

    def solution(self) -> int:
        return sum(
            val + 1
            for (x, y), val in self.height_map.copy().items()
            if (
                val < self.height_map[x - 1, y]
                and val < self.height_map[x + 1, y]
                and val < self.height_map[x, y - 1]
                and val < self.height_map[x, y + 1]
            )
        )


class Problem2(_Problem):
    test_solution = 1134
    puzzle_solution = 1113424

    def solution(self) -> int:
        merged: dict[int, set[int]] = defaultdict(set)
        basin_id = 0
        for (x, y), val in self.height_map.copy().items():
            if val == 9:
                continue

            left = self.height_map[x - 1, y]
            above = self.height_map[x, y - 1]

            if left < 0:
                # part of left neighbor's basin
                self.height_map[x, y] = left
                if left != above < 0:
                    # top and left are in different basins: merge
                    merged[left].add(above)
            elif above < 0:
                # part of top neighbor's basin
                self.height_map[x, y] = above
            else:
                # new basin
                basin_id -= 1
                self.height_map[x, y] = basin_id

        basins = Counter([v for v in self.height_map.values() if v < 0])
        for k, v in merged.items():
            for x in v:
                basins[k] += basins[x]
                basins[x] = 0
        return prod(v for _, v in basins.most_common(3))


TEST_INPUT = """
2199943210
3987894921
9856789892
8767896789
9899965678
"""
