from abc import ABC
from collections import deque
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from math import lcm
from operator import add, mul

from parse import parse  # type: ignore[import-untyped]

from advent_of_code.problems import ParsedProblem
from advent_of_code.utils import try_convert


@dataclass
class Monkey:
    items: deque[int]
    operation: Callable[[int], int]
    div: int
    t: int
    f: int
    inspected_count: int = 0

    def inspect_items(self, adjust: Callable[[int], int]) -> Iterator[tuple[int, int]]:
        while self.items:
            self.inspected_count += 1
            w = adjust(self.operation(self.items.popleft()))
            yield self.t if w % self.div == 0 else self.f, w


def __parse_items(s: str) -> deque[int]:
    return deque(int(i) for i in s.split(", "))


def __parse_operation(op_str: str) -> Callable[[int], int]:
    operation, operand = parse("{:op} {:int?}", op_str, extra_types={
        "op": lambda s: {"+": add, "*": mul}[s],
        "int?": lambda s: try_convert(int, s, default=0),
    })
    return lambda w: operation(w, operand or w)


class _Problem(ParsedProblem[tuple[deque[int], Callable[[int], int], int, int, int], int], ABC):
    num_rounds: int

    multi_line_pattern = """Monkey {:d}:
  Starting items: {:items}
  Operation: new = old {:operation}
  Test: divisible by {:d}
    If true: throw to monkey {:d}
    If false: throw to monkey {:d}"""

    def __init__(self):
        self.monkeys = [Monkey(*data) for _, *data in self.parsed_input]

    def do_the_monkey(self, num_rounds: int, adjust: Callable[[int], int]) -> int:
        for _ in range(num_rounds):
            for monkey in self.monkeys:
                for m, w in monkey.inspect_items(adjust):
                    self.monkeys[m].items.append(w)
        x, y = sorted(m.inspected_count for m in self.monkeys)[-2:]
        return x * y


class Problem1(_Problem):
    test_solution = 10605
    my_solution = 112221

    def solution(self) -> int:
        return self.do_the_monkey(20, lambda w: w // 3)


class Problem2(_Problem):
    test_solution = 2713310158
    my_solution = 25272176808

    def solution(self) -> int:
        mod = lcm(*[m.div for m in self.monkeys])
        return self.do_the_monkey(10000, lambda w: w % mod)


TEST_INPUT = """
Monkey 0:
  Starting items: 79, 98
  Operation: new = old * 19
  Test: divisible by 23
    If true: throw to monkey 2
    If false: throw to monkey 3

Monkey 1:
  Starting items: 54, 65, 75, 74
  Operation: new = old + 6
  Test: divisible by 19
    If true: throw to monkey 2
    If false: throw to monkey 0

Monkey 2:
  Starting items: 79, 60, 97
  Operation: new = old * old
  Test: divisible by 13
    If true: throw to monkey 1
    If false: throw to monkey 3

Monkey 3:
  Starting items: 74
  Operation: new = old + 3
  Test: divisible by 17
    If true: throw to monkey 0
    If false: throw to monkey 1
"""
