from abc import ABC, abstractmethod
from ast import literal_eval
from functools import reduce
from itertools import permutations
from typing import TYPE_CHECKING

from advent_of_code.problems import MultiLineProblem

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence


class Node(ABC):
    def __init__(self, level: int, parent: Branch | None) -> None:
        self.parent = parent
        self.level = level

    @property
    def is_left(self) -> bool:
        return False if self.parent is None else self.parent.left == self

    @abstractmethod
    def add_to_leaf(self, data: int, *, go_left: bool) -> None:
        pass

    @abstractmethod
    def check_explodes(self) -> bool:
        pass

    @abstractmethod
    def check_splits(self) -> bool:
        pass


class Dummy(Node):
    def __init__(self) -> None:
        super().__init__(level=0, parent=None)
        self.magnitude = 0
        self.data = None

    def add_to_leaf(self, data: int, *, go_left: bool) -> None:
        pass

    def check_explodes(self) -> bool:
        return False

    def check_splits(self) -> bool:
        return False


class Leaf(Node):
    parent: Branch

    def __init__(self, data: int, level: int, parent: Branch) -> None:
        super().__init__(level, parent)
        self._data = data

    @property
    def data(self) -> int:
        return self._data

    @property
    def magnitude(self) -> int:
        return self._data

    def add_to_leaf(self, data: int, *, go_left: bool) -> None:  # noqa: ARG002
        self._data += data

    def check_explodes(self) -> bool:
        # leaves aren't that explosive
        return False

    def check_splits(self) -> bool:
        if self._data < 10:
            return False
        # split that shit!
        n = self._data
        self.parent.add_child(data=[n // 2, n // 2 + n % 2], go_left=self.is_left)
        return True


class Branch(Node):
    def __init__(
        self, data: Sequence | None, level: int, parent: Branch | None
    ) -> None:
        super().__init__(level, parent)
        self._data = data or []
        self.left: Dummy | Leaf | Branch = Dummy()
        self.right: Dummy | Leaf | Branch = Dummy()
        if not data:
            return
        left, right = data
        self.add_child(left, go_left=True)
        self.add_child(right, go_left=False)

    @property
    def data(self) -> Sequence | None:
        return [self.left.data, self.right.data] if self._data else None

    def add_child(self, data: int | Sequence, *, go_left: bool) -> None:
        # kwargs = {"data": data, "level": self.level + 1, "parent": self}
        node: Dummy | Leaf | Branch
        node = (
            Leaf(data, self.level + 1, self)
            if isinstance(data, int)
            else Branch(data, self.level + 1, self)
        )
        if go_left:
            self.left = node
        else:
            self.right = node

    @property
    def magnitude(self) -> int:
        return self.left.magnitude * 3 + self.right.magnitude * 2

    def find_parent(self, *, go_left: bool) -> Branch | None:
        curr = self
        parent = curr.parent
        while parent:
            if go_left ^ curr.is_left:
                return parent
            curr = parent
            parent = curr.parent
        return None

    def add_to_leaf(self, data: int, *, go_left: bool) -> None:
        child = self.left if go_left else self.right
        child.add_to_leaf(data, go_left=go_left)

    def check_explodes(self) -> bool:
        if self.level < 4:
            return self.left.check_explodes() or self.right.check_explodes()
        # KABOOM!!!
        lp = self.find_parent(go_left=True)
        if lp and isinstance(self.left, Leaf):
            lp.left.add_to_leaf(self.left.data, go_left=False)
        rp = self.find_parent(go_left=False)
        if rp and isinstance(self.right, Leaf):
            rp.right.add_to_leaf(self.right.data, go_left=True)
        if isinstance(self.parent, Branch):
            self.parent.add_child(0, go_left=self.is_left)
            return True
        return False

    def check_splits(self) -> bool:
        return self.left.check_splits() or self.right.check_splits()


class Root(Branch):
    def __init__(self, data: Sequence) -> None:
        super().__init__(data, level=0, parent=None)

    def __add__(self, other: Root) -> Root:
        r = Root([self.data, other.data]) if self._data else other
        while r.check_explodes() or r.check_splits():
            continue
        return r


class _Problem(MultiLineProblem[int], ABC):
    def roots(self) -> Iterator[Root]:
        for line in self.lines:
            yield Root(literal_eval(line))


class Problem1(_Problem):
    test_solution = 4140
    my_solution = 4641

    def solution(self) -> int:
        return reduce(lambda t, r: t + r, self.roots()).magnitude


class Problem2(_Problem):
    test_solution = 3993
    my_solution = 4624

    def solution(self) -> int:
        return max((r1 + r2).magnitude for r1, r2 in permutations(self.roots(), 2))


TEST_INPUT = """
[[[0,[5,8]],[[1,7],[9,6]]],[[4,[1,2]],[[1,4],2]]]
[[[5,[2,8]],4],[5,[[9,9],0]]]
[6,[[[6,2],[5,6]],[[7,6],[4,7]]]]
[[[6,[0,7]],[0,9]],[4,[9,[9,0]]]]
[[[7,[6,4]],[3,[1,3]]],[[[5,5],1],9]]
[[6,[[7,3],[3,2]]],[[[3,8],[5,7]],4]]
[[[[5,4],[7,7]],8],[[8,3],8]]
[[9,3],[[9,9],[6,[4,9]]]]
[[2,[[7,7],7]],[[5,8],[[9,3],[0,2]]]]
[[[[5,2],5],[8,[3,7]]],[[5,[7,5]],[4,4]]]
"""
