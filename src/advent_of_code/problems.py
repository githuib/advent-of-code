import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import ClassVar, Literal, Self

from gaffe import raises
from more_itertools import strip
from parse import findall  # type: ignore[import-untyped]

import advent_of_code

from .utils.geo2d import BitGrid2, CharGrid2, Grid2, NumGrid2
from .utils.geo3d import P3D

PKG_NAME = advent_of_code.__name__


class NoSolutionFoundError(Exception):
    def __init__(self) -> None:
        super().__init__("No solution found!? 🤷‍")


type InputMode = Literal["puzzle", "test", "none"]


@dataclass
class PuzzleData:
    year: int
    day: int
    part: int
    input_mode: InputMode


class Problem[T](ABC):
    test_solution: T | None = None
    puzzle_solution: T | None = None

    line_count: int
    input: str
    corrected_input: str
    is_test_run: bool = False
    has_no_input: bool = False

    data: ClassVar[PuzzleData]

    def __new__(cls) -> Self:
        # Read input into problem instance before its actual __init__() will be called.
        self: Self = super().__new__(cls)

        self.is_test_run = cls.data.input_mode == "test"
        self.has_no_input = cls.data.input_mode == "none"
        if not self.has_no_input:
            self._load_input()
        return self

    @raises(FileNotFoundError)
    def _load_input(self) -> None:
        if self.is_test_run:
            self._load_test_input()
        else:
            self._load_puzzle_input()

    def _load_test_input(self) -> None:
        module, v = sys.modules[self.__module__], "TEST_INPUT"
        v_part = f"{v}_{self.data.part}"
        self._set_input(getattr(module, v_part if (v_part in dir(module)) else v))

    def _load_puzzle_input(self) -> None:
        path = Path("input") / f"{self.data.year}" / f"{self.data.day:02d}.txt"
        with path.open(encoding="utf8") as input_file:
            self._set_input(input_file.read())

    def _set_input(self, input_: str) -> None:
        self.input = input_
        self.corrected_input = input_.lstrip("\n").rstrip() + "\n"
        self.line_count = self.corrected_input.count("\n")
        self.process_input()

    def var[V](self, *, test: V, puzzle: V) -> V:
        return test if self.is_test_run else puzzle

    @abstractmethod
    def process_input(self) -> None:
        pass

    @property
    def actual_solution(self) -> T | None:
        return self.test_solution if self.is_test_run else self.puzzle_solution

    @abstractmethod
    def solution(self) -> T:
        pass


@raises(ModuleNotFoundError)
def load_problem[T](data: PuzzleData) -> type[Problem[T]]:
    y, d, p = f"year{data.year}", f"day{data.day:02d}", f"Problem{data.part}"
    problem_cls: type[Problem[T]] = getattr(import_module(f".{y}.{d}", PKG_NAME), p)
    problem_cls.data = data
    return problem_cls


class OneLineProblem[T](Problem[T], ABC):
    line: str

    def process_input(self) -> None:
        self.line = self.input.strip()


class MultiLineProblem[T](Problem[T], ABC):
    lines: list[str]

    def process_input(self) -> None:
        self.lines = list(
            strip(self.corrected_input.splitlines(), lambda line: line == "")
        )


class _GridProblem[E, T](MultiLineProblem[T], ABC):
    grid_cls: type[Grid2[E]]
    grid: Grid2[E]

    @abstractmethod
    def parse_value(self, c: str) -> E:
        pass

    def process_input(self) -> None:
        super().process_input()
        self.grid = self.grid_cls.from_lines(self.lines, parse_value=self.parse_value)


class CharGridProblem[T](_GridProblem[str, T], ABC):
    grid_cls = CharGrid2
    grid: CharGrid2

    def parse_value(self, c: str) -> str:
        return c


class NumGridProblem[T](_GridProblem[int, T], ABC):
    grid_cls = NumGrid2
    grid: NumGrid2

    def parse_value(self, c: str) -> int:
        return int(c)


class BitGridProblem[T](_GridProblem[bool, T], ABC):
    grid_cls = BitGrid2
    grid: BitGrid2

    def parse_value(self, c: str) -> bool:
        return c != "."


class ParsedProblem[R, T](Problem[T], ABC):
    line_pattern: str = ""
    multi_line_pattern: str = ""
    # _regex_pattern: str | None
    # _regex_converters: list[Callable[[str], Any]] | None

    parsed_input: list[R]
    # parsed_regex: list[list]

    def process_input(self) -> None:
        if not self.line_pattern and not self.multi_line_pattern:
            msg = "Either line_pattern or multi_line_pattern should be set."
            raise TypeError(msg)
        prefix = "__parse_"
        module = sys.modules[self.__module__]
        extra_types = {
            f[len(prefix) :]: getattr(module, f)
            for f in dir(module)
            if f.startswith(prefix)
        } | {"p3": P3D.from_str}

        self.parsed_input = [
            r.fixed
            for r in findall(
                self.multi_line_pattern or self.line_pattern + "\n",
                self.corrected_input,
                extra_types=extra_types,
            )
        ]
        # elif self._regex_pattern:
        #     rc = self._regex_converters or []
        #     self.parsed_regex = [
        #         [(rc[n](g) if n < len(rc) else g) for n, g in enumerate(groups)]
        #         for groups in re.findall(self._regex_pattern, self.corrected_input)
        #     ]
