from abc import ABC

from advent_of_code.problems import MultiLineProblem, NoSolutionFoundError


class Body:
    parent: Body | None = None

    @property
    def ancestors(self) -> list[Body]:
        if self.parent is None:
            return []
        return [self.parent, *self.parent.ancestors]


class _Problem(MultiLineProblem[int], ABC):
    def big_bang(self) -> dict[str, Body]:
        universe = {}
        for line in self.lines:
            left, right = line.split(")")
            if left not in universe:
                universe[left] = Body()
            if right not in universe:
                universe[right] = Body()
            universe[right].parent = universe[left]
        return universe


class Problem1(_Problem):
    test_solution = None
    puzzle_solution = 162439

    def solution(self) -> int:
        return sum(len(body.ancestors) for body in self.big_bang().values())


class Problem2(_Problem):
    test_solution = None
    puzzle_solution = 367

    def solution(self) -> int:
        universe = self.big_bang()
        my_ancestors = universe["YOU"].ancestors
        santas_ancestors = universe["SAN"].ancestors
        for body in my_ancestors:
            if body in santas_ancestors:
                return my_ancestors.index(body) + santas_ancestors.index(body)
        raise NoSolutionFoundError


TEST_INPUT = """

"""
