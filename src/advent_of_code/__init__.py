from functools import cache
from importlib import import_module
from os import get_terminal_size, terminal_size
from typing import TYPE_CHECKING

from based_utils.colors import Colors
from gaffe import raises

from .logs import AppLogger

if TYPE_CHECKING:
    from .problems import Problem, PuzzleData

log = AppLogger(__name__)

C = Colors


@cache
def term_size() -> terminal_size:
    return get_terminal_size()


@raises(ModuleNotFoundError)
def load_problem[T](data: PuzzleData) -> type[Problem[T]]:
    problem_module = import_module(f"{__name__}.year{data.year}.day{data.day:02d}")
    problem_cls: type[Problem[T]] = getattr(problem_module, f"Problem{data.part}")
    problem_cls.data = data
    return problem_cls
