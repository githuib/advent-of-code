import argparse
import sys
from datetime import UTC, datetime

from based_utils.cli import LogLevel, human_readable_duration, timed
from based_utils.cli.formats import FAIL, OK
from based_utils.colors import Color

from . import load_problem, log
from .problems import FatalError, NoSolutionFoundError, Problem, PuzzleData
from .utils.cli import format_table


def solution_lines[T](my_solution: T, actual_solution: T | None) -> list[str]:
    mine: list[str] = (
        my_solution.splitlines() if isinstance(my_solution, str) else [str(my_solution)]
    )
    actual: list[str] = (
        [""]
        if (actual_solution is None)
        else actual_solution.splitlines()
        if (isinstance(actual_solution, str))
        else [str(actual_solution)]
    )
    if len(mine) > 1:
        mine = ["", *mine]
    if len(actual) > 1:
        actual = ["", *actual]

    if not actual_solution:
        return ["Attempted solution... 👾 ", *mine]

    if my_solution == actual_solution:
        return ["Correct solution! 🍻 ", *mine]

    my_answer = f"{FAIL} Your answer:"
    actual_answer = f"{OK} Correct answer:"
    return ["Wrong solution! 💀"] + (
        [f"{my_answer}    {mine[0]}", f"{actual_answer} {actual[0]}"]
        if (len(mine) == 1 and len(actual) == 1)
        else ["", my_answer, *mine, "", actual_answer, *actual]
    )


def duration_lines(duration: int) -> list[str]:
    duration_str = human_readable_duration(duration)
    if duration_str.endswith("minutes"):
        emoji = "🦥"
    elif duration_str.endswith("seconds"):
        emoji = "🐢"
    elif duration_str.endswith("ms"):
        emoji = "🐇"
    else:
        emoji = "🚀"
    return [f"Solved in {duration_str} {emoji}"]


def solve[T](problem_cls: type[Problem[T]]) -> bool:
    problem, dur_init = timed(problem_cls)
    sol_actual = problem.actual_solution
    try:
        sol_mine, dur_solution = timed(problem.solution)

    except NoSolutionFoundError:
        is_correct_solution = False
        output_lines = ["No solution found!? 🤷‍️"]

    except FatalError as exc:
        log.fatal(exc.message)
        is_correct_solution = False
        output_lines = ["The process died before a solution could be found. 💀‍️"]

    else:
        if sol_mine is None:
            return sol_actual is None

        mine = sol_mine.strip() if isinstance(sol_mine, str) else sol_mine
        actual = sol_actual.strip() if isinstance(sol_actual, str) else sol_actual
        is_correct_solution = mine == actual
        # TODO: Might be interesting to show input loading time separately.
        dur = dur_init + dur_solution
        output_lines = [*solution_lines(mine, actual), "", *duration_lines(dur)]

    color = Color.from_name("blue", lightness=0.35)
    log.info(format_table(*[[line] for line in output_lines], color=color))
    return is_correct_solution


def main() -> None:
    ty, tm, td = (t := datetime.now(UTC).date()).year, t.month, t.day
    y, d = (ty + int(dec := tm == 12) - 1), (td if dec and td <= 25 else None)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--year", dest="year", type=int, default=y, choices=[2019, *range(2021, y + 1)]
    )
    parser.add_argument(
        "--day",
        dest="day",
        type=int,
        default=d,
        choices=list(range(1, 26)),
        required=not d,
    )
    parser.add_argument("--part", dest="part", type=int, choices=[1, 2], required=True)
    parser.add_argument("-t", "--test", dest="test", action="store_true")
    parser.add_argument("-d", "--debug", dest="debugging", action="store_true")
    parser.add_argument("-n", "--no-input", dest="no_input", action="store_true")
    parser.add_argument("-q", "--quiet", dest="quiet", action="store_true")
    # parser.add_argument("-p", "--pycharm", dest="pycharm", action="store_true")
    args = parser.parse_args()

    with log.context(
        LogLevel.DEBUG
        if args.debugging
        else LogLevel.ERROR
        if args.quiet
        else LogLevel.INFO
    ):
        data = PuzzleData(
            args.year,
            args.day,
            args.part,
            "none" if args.no_input else "test" if args.test else "puzzle",
        )
        success = solve(load_problem(data))

    sys.exit(not success)
