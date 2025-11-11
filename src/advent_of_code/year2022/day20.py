from abc import ABC
from dataclasses import dataclass, field
from itertools import dropwhile, islice
from typing import TYPE_CHECKING

from advent_of_code.problems import MultiLineProblem

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator


@dataclass
class Node:
    val: int
    prev: Node = field(init=False)
    next: Node = field(init=False)

    @classmethod
    def from_input(cls, it: Iterable[int]) -> Node:
        node = first = Empty
        for num in it:
            n = Node(num)
            if first is Empty:
                first = n
            else:
                node.link(n)
            node = n
        node.link(first)
        return first

    def __iter__(self) -> Iterator[Node]:
        node = self
        while True:
            yield node
            node = node.next

    def move(self, list_size: int) -> None:
        i = self.val % (list_size - 1)
        if i == 0:
            return
        if i < list_size // 2:
            p = self
            for _ in range(i):
                p = p.next
            n = p.next
        else:
            n = self
            for _ in range(list_size - 1 - i):
                n = n.prev
            p = n.prev
        self.prev.link(self.next)
        p.link(self)
        self.link(n)

    def link(self, n: Node) -> None:
        self.next = n
        n.prev = self

    def __repr__(self) -> str:
        return str(self.val)


Empty = Node(0)


class _Problem(MultiLineProblem[int], ABC):
    decryption_key: int
    mixing_amount: int

    def solution(self) -> int:
        size = self.line_count
        it = Node.from_input(int(line) * self.decryption_key for line in self.lines)
        pointers = list(islice(it, size))
        for _ in range(self.mixing_amount):
            for node in pointers:
                node.move(size)
        return sum(
            n.val for n in islice(dropwhile(lambda n: n.val != 0, it), 1000, 3001, 1000)
        )


class Problem1(_Problem):
    test_solution = 3
    puzzle_solution = 23321

    decryption_key = 1
    mixing_amount = 1


class Problem2(_Problem):
    test_solution = 1623178306
    puzzle_solution = 1428396909280

    decryption_key = 811589153
    mixing_amount = 10


TEST_INPUT = """
1
2
-3
3
-2
0
4
"""
