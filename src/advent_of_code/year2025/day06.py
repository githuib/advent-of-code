from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator

from based_utils.data.iterators import filter_non_empty, split_when_changed
from based_utils.data.strings import equalized_lines
from more_itertools import split_into, transpose
from simpleeval import simple_eval  # type: ignore[import-untyped]

from advent_of_code import log
from advent_of_code.problems import MultiLineProblem

type Column = Iterable[Iterable[str]]


def cleanup(s: Iterable[str]) -> str:
    return "".join(s).strip()


class _Problem(MultiLineProblem[int], ABC):
    @abstractmethod
    def transform_column(self, col: Column) -> Column: ...

    def calx(self) -> Iterator[int]:
        *rows, ops_line = equalized_lines(self.lines)
        operators = list(split_when_changed(ops_line, lambda c: c != " "))
        columns = transpose(split_into(r, [len(s) for s in operators]) for r in rows)
        for col, op in zip(columns, operators, strict=True):
            numbers = filter_non_empty(cleanup(n) for n in self.transform_column(col))
            operation = f" {cleanup(op)} ".join(numbers)
            result = simple_eval(operation)
            log.debug(f"{operation} = {result}")
            yield result

    def solution(self) -> int:
        return sum(self.calx())


class Problem1(_Problem):
    test_solution = 4277556
    puzzle_solution = 5667835681547

    def transform_column(self, col: Column) -> Column:
        return col


class Problem2(_Problem):
    test_solution = 3263827
    puzzle_solution = 9434900032651

    def transform_column(self, col: Column) -> Column:
        return transpose(col)


TEST_INPUT = """
123 328  51 64
 45 64  387 23
  6 98  215 314
*   +   *   +
"""
