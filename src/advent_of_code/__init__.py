import logging
from dataclasses import dataclass
from enum import Enum
from importlib import import_module
from logging import getLogger
from typing import TYPE_CHECKING

from advent_of_code.log import AppLogger

if TYPE_CHECKING:
    from advent_of_code.problems import Problem

log = AppLogger(getLogger(__name__))


class InputMode(Enum):
    PUZZLE = "puzzle"
    TEST = "test"
    NONE = "none"


@dataclass
class RunnerState:
    input_mode: InputMode
    debugging: bool = False


@dataclass
class PuzzleData:
    year: int
    day: int
    part: int


def solve[T](runner_state: RunnerState, data: PuzzleData) -> tuple[T | None, bool]:
    log.setup(logging.DEBUG if runner_state.debugging else logging.INFO)
    problem_module = import_module(f"{__name__}.year{data.year}.day{data.day:02d}")
    problem_cls: type[Problem[T]] = getattr(problem_module, f"Problem{data.part}")
    problem_cls.data, problem_cls.runner_state = data, runner_state
    return problem_cls.solve()
