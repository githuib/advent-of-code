import logging
from collections.abc import Callable, Iterator
from functools import cached_property
from logging import Formatter, Handler, Logger, LogRecord, StreamHandler
from os import get_terminal_size
from pprint import pformat

from yachalk import chalk

LogLevel = int  # Literal[10, 20]  # DEBUG, INFO


class LogFormatter(Formatter):
    def __init__(self, app_logger_name: str) -> None:
        super().__init__()
        self.app_logger_name = app_logger_name

    def format(self, record: LogRecord) -> str:
        from_internal_code = record.name == self.app_logger_name

        if from_internal_code and record.levelno < logging.WARNING:
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
        return chalk.hex(
            {
                logging.DEBUG: "888",
                logging.INFO: "ccc",
                logging.WARNING: "f80",
                logging.ERROR: "f30",
                logging.CRITICAL: "f30",
            }[record.levelno]
        )(msg)


class AppLogger:
    def __init__(self, logger: Logger) -> None:
        self._logger = logger
        self._logger.addHandler(self._cli_handler)

    @cached_property
    def _cli_handler(self) -> Handler:
        log_name = self._logger.name

        def log_filter(record: LogRecord) -> bool:
            """Ignore debug messages from 3rd party packages."""
            return record.name == log_name or record.levelno > logging.DEBUG

        handler = StreamHandler()
        handler.addFilter(log_filter)
        handler.setFormatter(LogFormatter(log_name))
        return handler

    def set_level(self, level: LogLevel) -> None:
        self._logger.setLevel(level)

    def debug(self, msg: object) -> None:
        self._logger.debug(msg)

    def info(self, msg: object) -> None:
        self._logger.info(msg)

    def warning(self, msg: object) -> None:
        self._logger.warning(msg)

    def error(self, msg: object) -> None:
        self._logger.error(msg)

    def fatal(self, msg: object) -> None:
        self._logger.fatal(msg)

    def lazy_debug(self, cb: Callable[[], object]) -> None:
        self._logger.debug(cb())

    def lazy_info(self, cb: Callable[[], object]) -> None:
        self._logger.info(cb())

    def debug_action(self, cb: Callable[[], None]) -> None:
        if self._logger.level == logging.DEBUG:
            cb()
