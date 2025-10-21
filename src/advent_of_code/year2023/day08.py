from abc import ABC
from itertools import cycle, takewhile
from math import lcm
from typing import TYPE_CHECKING

from more_itertools import ilen

from advent_of_code import log
from advent_of_code.problems import MultiLineProblem

if TYPE_CHECKING:
    from collections.abc import Iterator

    from advent_of_code.utils import Predicate


class _Problem(MultiLineProblem[int], ABC):
    def __init__(self) -> None:
        self.directions = self.lines[0]
        self.network = {line[:3]: (line[7:10], line[12:15]) for line in self.lines[2:]}
        log.debug(self.network)

    def steps_from(self, start: str, while_condition: Predicate) -> int:
        def path_from(node: str) -> Iterator[str]:
            for d in cycle(self.directions):
                yield node
                left, right = self.network[node]
                node = left if d == "L" else right
        return ilen(takewhile(while_condition, path_from(start)))


class Problem1(_Problem):
    test_solution = 6
    my_solution = 16343

    def solution(self) -> int:
        return self.steps_from("AAA", lambda n: n != "ZZZ")


class Problem2(_Problem):
    test_solution = 6
    my_solution = 15299095336639

    def solution(self) -> int:
        return lcm(*[
            self.steps_from(start, lambda n: n[-1] != "Z")
            for start in self.network if start[-1] == "A"
        ])


TEST_INPUT_1 = """
LLR

AAA = (BBB, BBB)
BBB = (AAA, ZZZ)
ZZZ = (ZZZ, ZZZ)
"""

TEST_INPUT_2 = """
LR

11A = (11B, XXX)
11B = (XXX, 11Z)
11Z = (11B, XXX)
22A = (22B, XXX)
22B = (22C, 22C)
22C = (22Z, 22Z)
22Z = (22B, 22B)
XXX = (XXX, XXX)
"""

# TEST_INPUT = """
# RL
#
# AAA = (BBB, CCC)
# BBB = (DDD, EEE)
# CCC = (ZZZ, GGG)
# DDD = (DDD, DDD)
# EEE = (EEE, EEE)
# GGG = (GGG, GGG)
# ZZZ = (ZZZ, ZZZ)
# """
