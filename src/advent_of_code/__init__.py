from importlib import import_module
from logging import getLogger
from typing import TYPE_CHECKING

from advent_of_code.log import AppLogger

if TYPE_CHECKING:
    from advent_of_code.problems import Problem, PuzzleData

log = AppLogger(getLogger(__name__))


def load_problem[T](data: PuzzleData) -> type[Problem[T]]:
    problem_module = import_module(f"{__name__}.year{data.year}.day{data.day:02d}")
    problem_cls: type[Problem[T]] = getattr(problem_module, f"Problem{data.part}")
    problem_cls.data = data
    return problem_cls
