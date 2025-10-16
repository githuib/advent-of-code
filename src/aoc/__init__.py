import logging
from enum import Enum
from os import get_terminal_size
from pprint import pformat
from typing import ClassVar

from yachalk import chalk

log = logging.getLogger("aoc")


class InputMode(Enum):
    PUZZLE = "puzzle"
    TEST = "test"
    NONE = "none"


class LogFormatter(logging.Formatter):
    def format(self, record):
        prefix = "" if record.name == "root" else "[%(name)s] "
        if record.levelno < logging.WARNING and not prefix:
            # Debugging & info: just print the raw message (which could already be formatted)
            if isinstance(record.msg, str):
                return logging.Formatter(prefix + "%(message)s").format(record)
            return pformat(record.msg, width=get_terminal_size()[0])
        # Warnings & errors: add prefix and color
        msg = logging.Formatter(prefix + "%(levelname)s: %(message)s").format(record)
        prefix, *_ = msg.split(record.message)
        msg = msg.replace("\n", "\n" + prefix)
        return chalk.hex({
            logging.DEBUG: "888",
            logging.INFO: "ccc",
            logging.WARNING: "f80",
            logging.ERROR: "f30",
            logging.CRITICAL: "f30",
        }[record.levelno])(msg)


class AOC:
    input_mode: ClassVar[InputMode]
    debugging: ClassVar[bool] = False

    @classmethod
    def setup(cls, input_mode: InputMode, debugging: bool):
        cls.input_mode, cls.debugging = input_mode, debugging
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        debug_handler = logging.StreamHandler()
        debug_handler.addFilter(lambda record: record.name == "root" or record.levelno > logging.DEBUG)
        debug_handler.setLevel(logging.DEBUG if debugging else logging.INFO)
        debug_handler.setFormatter(LogFormatter())
        logger.addHandler(debug_handler)


# def logging.debug(*args: object | Callable[[], object]) -> None:
#     if not AOC.debugging:
#         return
#     if not args:
#         print()
#     for o in args:
#         if callable(o):
#             logging.debug(o())
#         elif isinstance(o, str):
#             print(o)
#         else:
#             pprint(o, width=get_terminal_size()[0])
#
#
# def logging.debug_iter(it: Iterator[T]) -> Iterator[T]:
#     if not AOC.debugging:
#         return it
#     orig, extra = tee(it)
#     logging.debug(list(extra))
#     return orig
