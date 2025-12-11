from collections.abc import Callable, Iterator
from functools import cached_property
from logging import Formatter, LogRecord
from pprint import pformat
from typing import TYPE_CHECKING

from based_utils.cli import ConsoleHandlers, LogLevel, LogMeister
from kleur import Colored, Colors
from ternimator import animate_iter, consume

import advent_of_code

if TYPE_CHECKING:
    from ternimator import AnimParams


class LogFormatter(Formatter):
    def __init__(self, app_logger_name: str) -> None:
        super().__init__()
        self.app_logger_name = app_logger_name

    def format(self, record: LogRecord) -> str:
        from_internal_code = record.name == self.app_logger_name

        if from_internal_code and record.levelno < LogLevel.WARNING:
            # Debugging & info: just print the raw message (which could already be formatted)
            if isinstance(record.msg, Iterator):
                record.msg = "".join(f"{line}\n" for line in record.msg)
            if isinstance(record.msg, str):
                return Formatter("%(message)s").format(record)
            max_width, _max_height = advent_of_code.term_size()
            return pformat(record.msg, width=max_width)

        # Warnings & errors (or external package loggings): add prefix and color
        fmt = f"{'' if from_internal_code else '[%(name)s] '}%(levelname)s: %(message)s"
        msg = Formatter(fmt).format(record)
        prefix, *_ = msg.split(record.message)
        msg = msg.replace("\n", "\n" + prefix)
        color = {
            LogLevel.DEBUG: Colors.grey,
            LogLevel.INFO: Colors.grey.bright,
            LogLevel.WARNING: Colors.orange,
            LogLevel.ERROR: Colors.red,
            LogLevel.CRITICAL: Colors.red,
        }[LogLevel(record.levelno)]
        return str(Colored(msg, color))


class AppLogger(LogMeister):
    @cached_property
    def _console_handlers(self) -> ConsoleHandlers:
        main_name = self._main_name
        stdout_handler, stderr_handler = super()._console_handlers

        def ignore_3rd_party_debug(record: LogRecord) -> bool:
            """Don't handle DEBUG messages unless they came from this codebase."""
            return record.levelno > LogLevel.DEBUG or record.name.startswith(main_name)

        stdout_handler.addFilter(ignore_3rd_party_debug)

        formatter = LogFormatter(main_name)
        stdout_handler.setFormatter(formatter)
        stderr_handler.setFormatter(formatter)

        return stdout_handler, stderr_handler

    def debug(self, msg: object) -> None:
        self._main_logger.debug(msg)

    def info(self, msg: object) -> None:
        self._main_logger.info(msg)

    def warning(self, msg: object) -> None:
        self._main_logger.warning(msg)

    def error(self, msg: object) -> None:
        self._main_logger.error(msg)

    def fatal(self, msg: object) -> None:
        self._main_logger.fatal(msg)

    def lazy_debug(self, cb: Callable[[], object]) -> None:
        self._main_logger.debug(cb())

    def lazy_info(self, cb: Callable[[], object]) -> None:
        self._main_logger.info(cb())

    def debug_action[T](self, cb: Callable[[], T]) -> T | None:
        return cb() if self._main_logger.level == LogLevel.DEBUG else None

    def debug_animated_iter[T](
        self, items: Iterator[T], params: AnimParams = None
    ) -> Iterator[T]:
        yield from (
            animate_iter(items, params)
            if self._main_logger.level == LogLevel.DEBUG
            else items
        )

    def debug_animated[T](self, items: Iterator[T], params: AnimParams = None) -> None:
        consume(self.debug_animated_iter(items, params))
