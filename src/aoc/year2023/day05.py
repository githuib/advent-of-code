from abc import ABC
from functools import reduce
from itertools import batched
from typing import TYPE_CHECKING

from more_itertools import split_at

from aoc import log
from aoc.problems import MultiLineProblem

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from aoc.geo2d import Range

MapEntry = tuple[int, int, int]


class _Problem(MultiLineProblem[int], ABC):
    def __init__(self):
        seeds, *maps = split_at(self.lines, lambda x: x == "")
        self.seeds = [int(i) for i in seeds[0][7:].split()]
        items = [[[int(i) for i in vals.split()] for vals in m[1:]] for m in maps]
        self.maps = [sorted((s, s + o, d - s) for d, s, o in f) for f in items]
        log.debug("Seeds: %s", self.seeds)
        log.debug("Maps: %s", self.maps)


class Problem1(_Problem):
    test_solution = 35
    my_solution = 309796150

    def solution(self) -> int:
        def get_next_value(item: int, m: list[MapEntry]) -> int:
            for start, end, offset in m:
                if start <= item < end:
                    return item + offset
            return item
        return min(reduce(get_next_value, self.maps, seed) for seed in self.seeds)


class Problem2(_Problem):
    test_solution = 46
    my_solution = 50716416

    def solution(self) -> int:
        def get_next_ranges(ranges: Iterable[Range], m: list[MapEntry]) -> Iterator[Range]:
            for r in ranges:
                s, e = r
                for start, end, offset in m:
                    if s < start:
                        yield s, min(e, start)
                    if start >= e:
                        break
                    if s >= end:
                        continue
                    yield max(s, start) + offset, min(end, e) + offset
                    s = end
                else:
                    if s < e:
                        yield s, e
        seed_ranges: Iterable[Range] = ((s, s + o) for s, o in batched(self.seeds, 2, strict=True))
        return min(s for s, _ in reduce(get_next_ranges, self.maps, seed_ranges))


TEST_INPUT = """
seeds: 79 14 55 13

seed-to-soil map:
50 98 2
52 50 48

soil-to-fertilizer map:
0 15 37
37 52 2
39 0 15

fertilizer-to-water map:
49 53 8
0 11 42
42 0 7
57 7 4

water-to-light map:
88 18 7
18 25 70

light-to-temperature map:
45 77 23
81 45 19
68 64 13

temperature-to-humidity map:
0 69 1
1 0 69

humidity-to-location map:
60 56 37
56 93 4
"""
