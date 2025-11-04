import argparse
from datetime import UTC, datetime

from advent_of_code import solve
from advent_of_code.problems import InputMode, PuzzleData, RunnerState


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
    # parser.add_argument("-p", "--pycharm", dest="pycharm", action="store_true")
    args = parser.parse_args()

    input_mode = (
        InputMode.NONE
        if args.no_input
        else InputMode.TEST
        if args.test
        else InputMode.PUZZLE
    )
    solve(
        RunnerState(input_mode, args.debugging),  # , args.pycharm),
        PuzzleData(args.year, args.day, args.part),
    )


if __name__ == "__main__":
    main()
