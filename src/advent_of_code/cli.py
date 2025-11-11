import argparse
import logging
import sys
from datetime import UTC, datetime

from yachalk import chalk

from advent_of_code import load_problem, log
from advent_of_code.problems import (
    FatalError,
    NoSolutionFoundError,
    Problem,
    PuzzleData,
)
from advent_of_code.utils.cli import (
    human_readable_duration,
    text_block_from_lines,
    timed,
)


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

    if not actual_solution:
        return ["Attempted solution... 👾 ", "", *mine]

    if my_solution == actual_solution:
        return ["Correct solution! 🍻 ", "", *mine]

    my_answer = f"{chalk.red_bright('✘')} Your answer:"
    actual_answer = f"{chalk.green_bright('✔')} Correct answer:"
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
    return [f"Solved in {duration_str} {emoji} "]


def solve[T](problem_cls: type[Problem[T]]) -> bool:
    problem, dur_init, _dur_init_str = timed(problem_cls)
    answer = problem.actual_solution
    try:
        attempt, dur_solution, _dur_solution_str = timed(problem.solution)

    except NoSolutionFoundError:
        success = False
        output_lines = ["No solution found!? 🤷‍️"]

    except FatalError as exc:
        log.fatal(exc.message)
        success = False
        output_lines = ["The process died before a solution could be found. 💀‍️"]

    else:
        if attempt is None:
            return problem.has_no_input

        success = attempt == answer
        solution_output = solution_lines(attempt, answer)
        # TODO: Might be interesting to show input loading time separately.
        duration_output = duration_lines(dur_init + dur_solution)
        output_lines = [*solution_output, "", *duration_output]

    log.info(text_block_from_lines(output_lines))
    return success


def quiet_solve[T](problem_cls: type[Problem[T]]) -> bool:
    problem = problem_cls()
    answer = problem.actual_solution
    try:
        attempt = problem.solution()

    except NoSolutionFoundError:
        return False

    except FatalError as exc:
        log.fatal(exc.message)
        return False

    else:
        if attempt is None:
            return problem.has_no_input
        return attempt == answer


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

    log.set_level(
        logging.DEBUG
        if args.debugging
        else logging.ERROR
        if args.quiet
        else logging.INFO
    )

    problem_cls = load_problem(
        PuzzleData(
            args.year,
            args.day,
            args.part,
            "none" if args.no_input else "test" if args.test else "puzzle",
        )
    )
    success = quiet_solve(problem_cls) if args.quiet else solve(problem_cls)
    sys.exit(not success)


if __name__ == "__main__":
    main()
