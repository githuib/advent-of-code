from abc import ABC
from ast import literal_eval

from more_itertools import chunked

from advent_of_code.problems import MultiLineProblem

type Item = int | list


def compare_items(item_l: Item, item_r: Item) -> bool:
    if isinstance(item_l, int):
        if isinstance(item_r, int):
            return item_l < item_r
        item_l = [item_l]
    if isinstance(item_r, int):
        item_r = [item_r]
    return compare_lists(item_l, item_r)


def compare_lists(list_l: list, list_r: list) -> bool:
    for left, right in zip(list_l, list_r, strict=False):
        if compare_items(left, right):
            return True
        if compare_items(right, left):
            return False
    return len(list_l) < len(list_r)


class Packet(list):
    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Packet):
            return NotImplemented
        return compare_lists(self, other)


class _Problem(MultiLineProblem[int], ABC):
    def __init__(self) -> None:
        self.packets = [Packet(literal_eval(line)) for line in self.lines if line]


class Problem1(_Problem):
    test_solution = 13
    puzzle_solution = 4821

    def solution(self) -> int:
        return sum(
            i for i, (p1, p2) in enumerate(chunked(self.packets, 2), 1) if p1 < p2
        )


class Problem2(_Problem):
    test_solution = 140
    puzzle_solution = 21890

    def solution(self) -> int:
        d1, d2 = Packet([[2]]), Packet([[6]])
        packets = sorted([*self.packets, d1, d2])
        return (packets.index(d1) + 1) * (packets.index(d2) + 1)


TEST_INPUT = """
[1,1,3,1,1]
[1,1,5,1,1]

[[1],[2,3,4]]
[[1],4]

[9]
[[8,7,6]]

[[4,4],4,4]
[[4,4],4,4,4]

[7,7,7,7]
[7,7,7]

[]
[3]

[[[]]]
[[]]

[1,[2,[3,[4,[5,6,7]]]],8,9]
[1,[2,[3,[4,[5,6,0]]]],8,9]
"""
