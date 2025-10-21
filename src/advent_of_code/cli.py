import argparse
from datetime import UTC, datetime
from importlib import import_module
from typing import TYPE_CHECKING

from advent_of_code import InputMode

if TYPE_CHECKING:
    from advent_of_code.problems import Problem


def main() -> None:
    ty, tm, td = (t := datetime.now(UTC).date()).year, t.month, t.day
    y, d = (ty + int(dec := tm == 12) - 1), (td if dec and td <= 25 else None)
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", dest="year", type=int, default=y, choices=[2019, *range(2021, y + 1)])
    parser.add_argument("--day", dest="day", type=int, default=d, choices=list(range(1, 26)), required=not d)
    parser.add_argument("--part", dest="part", type=int, choices=[1, 2], required=True)
    parser.add_argument("-t", "--test", dest="test", action="store_true")
    parser.add_argument("-d", "--debug", dest="debug", action="store_true")
    parser.add_argument("-n", "--no-input", dest="no_input", action="store_true")
    args = parser.parse_args()
    input_mode = InputMode.NONE if args.no_input else InputMode.TEST if args.test else InputMode.PUZZLE
    problem_cls: type[Problem] = getattr(import_module(f"advent_of_code.year{args.year}.day{args.day:02d}"), f"Problem{args.part}")
    problem_cls.solve(args.year, args.day, args.part, input_mode, args.debug)


if __name__ == "__main__":
    main()
