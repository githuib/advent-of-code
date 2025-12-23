import sys
from argparse import ArgumentParser, Namespace
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from based_utils.cli import (
    LogLevel,
    Table,
    human_readable_duration,
    killed_by_errors,
    timed,
)
from kleur.formatting import FAIL, OK, Colored

from advent_of_code import C

from . import log
from .problems import InputMode, NoSolutionFoundError, PuzzleData, load_problem

if TYPE_CHECKING:
    from collections.abc import Iterator


def solution_lines[T](my_solution: T, actual_solution: T | None) -> Iterator[str]:
    mine: list[str] = (
        my_solution.splitlines() if isinstance(my_solution, str) else [str(my_solution)]
    )

    if actual_solution is None:
        yield "Attempted solution... 👾 "
        yield from mine

    elif my_solution == actual_solution:
        yield "Correct solution! 🍻 "
        yield from mine

    else:
        yield "Wrong solution! 💀"

        actual: list[str] = (
            actual_solution.splitlines()
            if (isinstance(actual_solution, str))
            else [str(actual_solution)]
        )

        my_answer = f"{FAIL} Your answer:"
        actual_answer = f"{OK} Correct answer:"
        if len(mine) == 1 and len(actual) == 1:
            w = max(len(my_answer), len(actual_answer))
            yield f"{my_answer.ljust(w)} {mine[0]}"
            yield f"{actual_answer.ljust(w)} {actual[0]}"
        else:
            yield ""
            yield my_answer
            yield ""
            yield from mine
            yield ""
            yield actual_answer
            yield ""
            yield from actual


def duration_lines(duration: int) -> Iterator[str]:
    duration_str = human_readable_duration(duration)
    if duration_str.endswith("minutes"):
        emoji = "🦥"
    elif duration_str.endswith("seconds"):
        emoji = "🐢"
    elif duration_str.endswith("ms"):
        emoji = "🐇"
    else:
        emoji = "🚀"
    yield f"Solved in {duration_str} {emoji}"


def output_lines[T](
    my_solution: T, actual_solution: T | None, duration: int
) -> Iterator[str]:
    yield from solution_lines(my_solution, actual_solution)
    yield ""
    yield from duration_lines(duration)


table = Table(style_table=Colored(C.blue.dark))


# @raises(FileNotFoundError, NoSolutionFoundError)
def solve(puzzle_data: PuzzleData) -> bool:
    problem_cls = load_problem(puzzle_data)
    problem, dur_init = timed(problem_cls)
    sol_actual = problem.actual_solution
    sol_mine, dur_solution = timed(problem.solution)
    if sol_mine is None:
        return sol_actual is None

    mine = sol_mine.strip() if isinstance(sol_mine, str) else sol_mine
    actual = sol_actual.strip() if isinstance(sol_actual, str) else sol_actual
    # TODO: Might be interesting to show input loading time separately.
    duration = dur_init + dur_solution

    table_rows = ([line] for line in output_lines(mine, actual, duration))
    log.info(table(*table_rows))

    return mine == actual


def _parse_args() -> Namespace:
    today = datetime.now(UTC).date()
    y, m, d = today.year, today.month, today.day
    days = list(range(1, 26))
    is_aoc_month = m == 12
    is_aoc_day = is_aoc_month and d in days

    year = y if is_aoc_month else y - 1
    day = d if is_aoc_day else 25

    # Path().glob("year*")

    parser = ArgumentParser()
    parser.add_argument(
        "--year",
        dest="year",
        type=int,
        default=year,
        choices=[2019, *range(2021, year + 1)],
    )
    parser.add_argument(
        "--day",
        dest="day",
        type=int,
        default=day,
        choices=days,
        required=not is_aoc_day,
    )
    parser.add_argument("--part", dest="part", type=int, choices=[1, 2], required=True)
    parser.add_argument("-t", "--test", dest="test", action="store_true")
    parser.add_argument("-d", "--debug", dest="debugging", action="store_true")
    parser.add_argument("-n", "--no-input", dest="no_input", action="store_true")
    return parser.parse_args()


@killed_by_errors(FileNotFoundError, ModuleNotFoundError, NoSolutionFoundError)
def main() -> None:
    args = _parse_args()
    input_mode: InputMode = (
        "none" if args.no_input else "test" if args.test else "puzzle"
    )
    puzzle_data = PuzzleData(args.year, args.day, args.part, input_mode)
    with log.context(LogLevel.DEBUG if args.debugging else LogLevel.INFO):
        success = solve(puzzle_data)
    sys.exit(not success)
