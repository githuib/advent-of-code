from collections.abc import Callable, Iterator
from functools import cached_property
from logging import Formatter, LogRecord
from os import get_terminal_size
from pprint import pformat

from based_utils.cli import Colored, ConsoleHandlers, LogLevel, LogMeister
from based_utils.colors import Color


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
            return pformat(record.msg, width=get_terminal_size()[0])

        # Warnings & errors (or external package loggings): add prefix and color
        fmt = f"{'' if from_internal_code else '[%(name)s] '}%(levelname)s: %(message)s"
        msg = Formatter(fmt).format(record)
        prefix, *_ = msg.split(record.message)
        msg = msg.replace("\n", "\n" + prefix)
        color = {
            LogLevel.DEBUG: Color.grey(0.5),
            LogLevel.INFO: Color.grey(0.75),
            LogLevel.WARNING: Color.from_name("orange"),
            LogLevel.ERROR: Color.from_name("red"),
            LogLevel.CRITICAL: Color.from_name("red"),
        }[LogLevel(record.levelno)]
        return Colored(msg, color).formatted


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

    def debug_action(self, cb: Callable[[], None]) -> None:
        if self._main_logger.level == LogLevel.DEBUG:
            cb()
