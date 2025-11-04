import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Self

from more_itertools import strip
from parse import Result, findall  # type: ignore[import-untyped]
from yachalk import chalk

from advent_of_code import InputMode, PuzzleData, RunnerState, log
from advent_of_code.geo2d import Grid2
from advent_of_code.geo3d import P3D
from advent_of_code.utils import human_readable_duration, strlen, timed

if TYPE_CHECKING:
    from collections.abc import Iterator


def solution_lines[T](my_solution: T, actual_solution: T) -> list[str]:
    mine: list[str] = (
        my_solution.strip().splitlines()
        if isinstance(my_solution, str)
        else [str(my_solution)]
    )
    actual: list[str] = (
        [""]
        if (actual_solution is None)
        else actual_solution.strip().splitlines()
        if (isinstance(actual_solution, str))
        else [str(actual_solution)]
    )
    if len(mine) > 1:
        mine = ["", *mine]
    if len(actual) > 1:
        actual = ["", *actual]
    if actual == [""]:
        return ["Attempted solution... 👾 ", "", *mine]
    if mine == actual:
        return ["Correct solution! 🍻 ", "", *mine]
    return ["Wrong solution! 💀"] + (
        [
            f"{mine[0]} {chalk.red_bright('✘')} your answer",
            f"{actual[0]} {chalk.green_bright('✔')} correct answer",
        ]
        if (len(mine) == 1 and len(actual) == 1)
        else ["", "Your answer:", *mine, "", "Right answer:", *actual]
    )


def duration_emoji(duration_str: str) -> str:
    if duration_str.endswith("minutes"):
        return "🦥"
    if duration_str.endswith("seconds"):
        return "🐢"
    if duration_str.endswith("ms"):
        return "🐇"
    return "🚀"


class NoSolutionFoundError(Exception):
    pass


class FatalError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


class Problem[T](ABC):
    test_solution: T | None = None
    my_solution: T | None = None

    line_count: int
    input: str
    corrected_input: str
    is_debugged_run: bool = False
    is_test_run: bool = False

    runner_state: ClassVar[RunnerState]
    data: ClassVar[PuzzleData]

    def __new__(cls) -> Self:
        # Read input into problem instance before its actual __init__() will be called.
        self: Self = super().__new__(cls)

        self.is_debugged_run = cls.runner_state.debugging
        self.is_test_run = cls.runner_state.input_mode == InputMode.TEST
        if cls.runner_state.input_mode != InputMode.NONE:
            self._load_input()
        return self

    def var[V](self, test: V, puzzle: V) -> V:
        return test if self.is_test_run else puzzle

    def _load_input(self) -> None:
        if self.is_test_run:
            self._load_test_input()
        else:
            self._load_puzzle_input()

    def _load_test_input(self) -> None:
        module = sys.modules[self.__module__]
        input_prefix = "TEST_INPUT"
        part_input = f"{input_prefix}_{self.data.part}"
        input_var = part_input if (part_input in dir(module)) else input_prefix
        self._set_input(getattr(module, input_var))

    def _load_puzzle_input(self) -> None:
        path = Path("input") / f"{self.data.year}" / f"{self.data.day:02d}.txt"
        with path.open(encoding="utf8") as input_file:
            self._set_input(input_file.read())

    def _set_input(self, input_: str) -> None:
        self.input = input_
        self.corrected_input = input_.lstrip("\n").rstrip() + "\n"
        self.line_count = self.corrected_input.count("\n")
        self.process_input()

    @property
    def given_solution(self) -> T | None:
        return self.test_solution if self.is_test_run else self.my_solution

    @classmethod
    def solve(cls) -> T | None:
        solution: T | None = None

        try:
            instance, duration_init, _dur_init_str = timed(cls)
            solution, duration_solution, _dur_solution_str = timed(instance.solution)

        except NoSolutionFoundError:
            lines = ["No solution found!? 🤷‍️"]

        except FatalError as exc:
            log.fatal(exc.message)
            lines = ["The process died before a solution could be found. 💀‍️"]

        else:
            if solution is None:
                return None
            lines = solution_lines(solution, instance.given_solution)

            duration_total = duration_init + duration_solution
            duration_str = human_readable_duration(duration_total)
            # TODO: Might be interesting to show input loading time.
            lines += ["", f"Solved in {duration_str} {duration_emoji(duration_str)} "]

        width = max(strlen(line) for line in lines)
        log.info(" " * (width + 4))
        log.info(f" {chalk.bg_hex('332')(' ' * (width + 2))} ")
        for line in lines:
            log.info(
                f" {chalk.bg_hex('332')(f' {line} {" " * (width - strlen(line))}')} "
            )
        log.info(f" {chalk.bg_hex('332')(' ' * (width + 2))} ")
        log.info(" " * (width + 4))

        return solution

    @abstractmethod
    def process_input(self) -> None:
        pass

    @abstractmethod
    def solution(self) -> T:
        pass


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
    grid: Grid2[E]


class GridProblem[T](_GridProblem[str, T], ABC):
    def process_input(self) -> None:
        super().process_input()
        self.grid = Grid2.from_lines(self.lines)


class NumberGridProblem[T](_GridProblem[int, T], ABC):
    def process_input(self) -> None:
        super().process_input()
        self.grid = Grid2.from_lines(self.lines).converted(self.convert_element)

    def convert_element(self, element: str) -> int:
        return int(element)


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
        rs: Iterator[Result] = findall(
            self.multi_line_pattern or self.line_pattern + "\n",
            self.corrected_input,
            extra_types=extra_types,
        )
        self.parsed_input = [r.fixed for r in rs]
        # elif self._regex_pattern:
        #     rc = self._regex_converters or []
        #     self.parsed_regex = [
        #         [(rc[n](g) if n < len(rc) else g) for n, g in enumerate(groups)]
        #         for groups in re.findall(self._regex_pattern, self.corrected_input)
        #     ]
