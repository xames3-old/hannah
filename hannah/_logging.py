"""Logging: Capture and control the logs."""

import logging
import logging.handlers
import os
import sys
from datetime import timedelta
from types import TracebackType
from typing import IO
from typing import Any
from typing import MutableMapping
from typing import Optional
from typing import Tuple
from typing import Union

__all__ = [
    "FileHandler",
    "Handler",
    "Logger",
    "RotatingFileHandler",
    "StackFormatter",
    "StreamHandler",
    "TTYInspector",
    "TimedRotatingFileHandler",
    "create_logger",
    "get_logger",
    "stderr",
    "stdout",
]

SysExcInfoType = Tuple[type, BaseException, Optional[TracebackType]]
TupleOfNone = Tuple[None, ...]

BASIC_FORMAT = (
    "%(gray)s%(asctime)s %(color)s%(levelname)5s%(reset)s "
    "%(gray)s[%(threadName)s] %(stack)s:%(lineno)d : %(reset)s%(message)s"
)
DATE_FORMAT = "%b %d %H:%M:%S"

logging._levelToName = {
    60: "TRACE",
    50: "FATAL",
    40: "ERROR",
    30: "WARN",
    20: "INFO",
    10: "DEBUG",
    00: "NOTSET",
}


class StackFormatter(logging.Formatter):
    """Formatter to format the message stack of the log record.

    This class formats the ``record.pathname`` and ``record.exc_info``
    attributes to generate a uniform and clear log message. The class
    adds gray hues to the messages using log levels.

    :param fmt: Log message format, defaults to None.
    :param datefmt: Log datetime format, defaults to None.

    .. seealso::

        :py:meth:`logging.Formatter.format()`
        :py:meth:`logging.Formatter.formatException()`

    """

    hues = {
        60: "\x1b[38;5;128m",
        50: "\x1b[38;5;197m",
        40: "\x1b[38;5;204m",
        30: "\x1b[38;5;215m",
        20: "\x1b[38;5;41m",
        10: "\x1b[38;5;14m",
        00: "\x1b[38;5;14m",
        "gray": "\x1b[38;5;242m",
        "reset": "\x1b[0m",
    }
    attrs = ("color", "gray", "reset")

    def __init__(
        self, fmt: Optional[str] = None, datefmt: Optional[str] = None
    ) -> None:
        """Initialize the formatter."""

        if not fmt:
            fmt = BASIC_FORMAT
        if not datefmt:
            datefmt = DATE_FORMAT
        self.fmt = fmt
        self.datefmt = datefmt

    def colorize(self, record: logging.LogRecord) -> None:
        """Add colors to the logging levels by manipulating record.

        :param record: Instance of the logged event.

        .. note::

            This behavior only works on the TTY interfaces.

        """

        if getattr(record, "isatty", False):
            setattr(record, "color", self.hues[record.levelno])
            setattr(record, "gray", self.hues["gray"])
            setattr(record, "reset", self.hues["reset"])
        else:
            for attr in self.attrs:
                setattr(record, attr, "")

    def decolorize(self, record: logging.LogRecord) -> None:
        """Remove ``color`` and ``reset`` attributes from a record.

        :param record: Instance of the logged event.

        """

        for attr in self.attrs:
            delattr(record, attr)

    def formatException(self, ei: Union[SysExcInfoType, TupleOfNone]) -> str:
        r"""Format exception information as text.

        :param ei: Information about the caught exception.
        :return: Formatted exception information string.

        .. note::

            This implementation does not work directly. The standard
            :py:class:`logging.Formatter` is required. It creates an
            output string with ``\n`` which need to be skipped.

        """

        func, lineno = "<module>", 0
        cls, msg, tbk = ei
        if tbk:
            func, lineno = tbk.tb_frame.f_code.co_name, tbk.tb_lineno
        func = "on" if func in ("<module>", "<lambda>") else f"in {func}() on"
        return f"{cls.__name__}: {msg} line {lineno}"  # type: ignore

    def stack(self, path: str, func: str) -> str:
        """Format path as stack.

        :param path: Pathname of the module which is logging the event.
        :param func: Callable instance which is logging the event.
        :return: *Spring Boot-esque* formatted path.

        .. note::

            If called from a module, the base path of the module would
            be used else "REPL" would be returned for the interpreter
            (stdin) based input.

        """

        if path == "<stdin>":
            return "REPL"
        abspath = "site-packages" if "site-packages" in path else os.getcwd()
        path = path.split(abspath)[-1].replace(os.path.sep, ".")[
            path[0] != ":" : -3
        ]
        if func not in ("<module>", "<lambda>"):
            path += f".{func}"
        return path

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as text.

        If any exception is caught then, it is formatted using the
        :py:meth:`hannah.logging.StackFormatter.formatException` and
        replaced with the original message.

        :param record: Instance of the logged event.
        :return: Captured and formatted output log string.

        """

        setattr(record, "stack", self.stack(record.pathname, record.funcName))
        if record.exc_info:
            record.msg = self.formatException(record.exc_info)
            record.exc_info = record.exc_text = None
        self.colorize(record)
        text = logging.Formatter(self.fmt, self.datefmt).format(record)
        self.decolorize(record)
        return text


class Handler(object):
    """Handler instance which dispatches logging events to streams.

    This is the base handler class which acts as a placeholder to define
    the handler interface. This class can optionally use a formatter
    class to format records as desired.

    :param handler: Handler instance which will output to a stream.
    :param level: Logging level of the logged event, defaults to None.
    :param formatter: Formatter instance to use for formatting record,
        defaults to :py:class:`StackFormatter`.

    """

    def __init__(
        self,
        handler: logging.Handler,
        level: Optional[Union[int, str]] = None,
        formatter: logging.Formatter = StackFormatter,  # type: ignore
    ) -> None:
        """Initialize the handler."""

        self.handler = handler
        self.handler.setFormatter(formatter)
        if level:
            self.handler.setLevel(level)

    def add_handler(self, logger: logging.Logger) -> None:
        """Add handler to the logger object.

        :param logger: Instance of the logging channel.

        """

        logger.addHandler(self.handler)


class FileHandler(Handler):
    """Handler instance which writes logging records to disk files.

    :param filename: Absolute path of the output log file.
    :param mode: Mode in which the file needs to be opened, defaults
        to append.
    :param encoding: Platform-dependent encoding for the file, defaults
        to None.
    :param level: Logging level of the logged event, defaults to None.
    :param formatter: Formatter instance to use for formatting record,
        defaults to :py:class:`StackFormatter`.

    .. seealso::

        :py:class:`Handler`
        :py:class:`logging.FileHandler`

    """

    def __init__(
        self,
        filename: str,
        mode: str = "a",
        encoding: Optional[str] = None,
        level: Optional[Union[int, str]] = None,
        formatter: logging.Formatter = StackFormatter,  # type: ignore
    ) -> None:
        """Open the file and use it as the stream for logging."""

        handler = logging.FileHandler(filename, mode, encoding)
        super().__init__(handler, level, formatter)


class RotatingFileHandler(Handler):
    """Handler instance for logging to a set of files, which switches
    from one file to next when the current file reaches a certain size.

    By default, the file grows indefinitely. You can specifiy particular
    values to allow the file to rollover at a pre-determined size.

    :param filename: Absolute path of the output log file.
    :param mode: Mode in which the file needs to be opened, defaults
        to append.
    :param max_bytes: Maximum size in bytes after which the rollover
        should happen, defaults to 10 MB.
    :param backups: Maximum files to retain after rollover, defaults
        to 5.
    :param encoding: Platform-dependent encoding for the file, defaults
        to None.
    :param level: Logging level of the logged event, defaults to None.
    :param formatter: Formatter instance to use for formatting record,
        defaults to :py:class:`StackFormatter`.

    .. note::

        Rollover occurs whenever the current log file is nearly
        ``max_bytes`` in size. If the ``backups`` >= 1, the system will
        successively create new files with same pathname as the base
        file, but with extensions ".1", ".2", etc. appended to it. For
        example, with a ``backups`` of 5 and a base file name of
        "mira.log", "mira.log.1", "mira.log.2", ... through to
        "mira.log.5". The file being written to is always "mira.log" -
        when it gets filled up, it is closed and renamed to "mira.log.1"
        and if files "mira.log.1", "mira.log.2" etc. exists, then they
        are renamed to "mira.log.2", "mira.log.3", etc. respectively.

        If ``max_bytes`` is zero, rollover never occurs.

    .. seealso::

        :py:class:`Handler`
        :py:class:`logging.handlers.RotatingFileHandler`

    """

    def __init__(
        self,
        filename: str,
        mode: str = "a",
        max_bytes: int = 10000000,
        backups: int = 5,
        encoding: Optional[str] = None,
        level: Optional[Union[int, str]] = None,
        formatter: logging.Formatter = StackFormatter,  # type: ignore
    ) -> None:
        """Open the file and use it as the stream for logging."""

        handler = logging.handlers.RotatingFileHandler(
            filename, mode, max_bytes, backups, encoding
        )
        super().__init__(handler, level, formatter)

    def do_rollover(self) -> Any:
        """Do a rollover when current log file is nearly in size."""

        return self.handler.doRollover()  # type: ignore


class TimedRotatingFileHandler(Handler):
    """Handler instance for logging to a set of files, which switches
    from one file to next at certain timed intervals.

    :param filename: Absolute path of the output log file.
    :param when: Interval of when the rollover should happen, defaults
        to S.
    :param interval: Interval count of the rollover, defaults to 1 day.
    :param backups: Maximum files to retain after rollover, defaults
        to 5.
    :param encoding: Platform-dependent encoding for the file, defaults
        to None.
    :param level: Logging level of the logged event, defaults to None.
    :param formatter: Formatter instance to use for formatting record,
        defaults to :py:class:`StackFormatter`.

    .. note::

        If ``backups`` > 0, when rollover is done, no more than
        ``backups`` files are kept, the oldest ones are deleted.

    .. seealso::

        :py:class:`Handler`
        :py:class:`logging.handlers.TimedRotatingFileHandler`

    """

    def __init__(
        self,
        filename: str,
        when: str = "S",
        interval: Union[int, float, timedelta] = timedelta(days=1),
        backups: int = 5,
        encoding: Optional[str] = None,
        level: Optional[Union[int, str]] = None,
        formatter: logging.Formatter = StackFormatter,  # type: ignore
    ) -> None:
        """Open the file and use it as the stream for logging."""

        handler = logging.handlers.TimedRotatingFileHandler(
            filename, when, self.to_seconds(interval), backups, encoding
        )
        super().__init__(handler, level, formatter)

    def do_rollover(self) -> Any:
        """Do a rollover when current log file is approaching the
        interval.

        :returns: Handler with rollover to perform.

        """

        return self.handler.doRollover()  # type: ignore

    @staticmethod
    def to_seconds(interval: Union[int, float, timedelta]) -> int:
        """Convert the time delta into seconds.

        :param interval: Interval timestamp to convert.
        :returns: Interval in seconds.

        """

        if isinstance(interval, (int, float)):
            interval = timedelta(seconds=interval)
        return int(interval.total_seconds())


class TTYInspector(logging.StreamHandler):
    """StreamHandler instance which inspects if the output stream is a
    TTY.

    .. seealso::

        :py:meth:`logging.StreamHandler.format()`

    """

    def format(self, record: logging.LogRecord) -> str:
        """Add hint if the specified stream is a TTY.

        :param record: Instance of the logged event.
        :return: Formatted string for the output stream.

        """

        if hasattr(self.stream, "isatty"):
            try:
                setattr(record, "isatty", self.stream.isatty())
            except ValueError:
                setattr(record, "isatty", False)
        else:
            setattr(record, "isatty", False)
        strict = super().format(record)
        delattr(record, "isatty")
        return strict


class StreamHandler(Handler):
    """Handler class which writes logging records, appropriately
    formatted to a stream.

    :param stream: IO stream, defaults to sys.stderr.
    :param level: Logging level of the logged event, defaults to None.
    :param formatter: Formatter instance to use for formatting record,
        defaults to :py:class:`Formatter`.

    .. note::

        This class does not close the stream, as ``sys.stdout`` or
        ``sys.stderr`` may be used.

    """

    def __init__(
        self,
        stream: Optional[IO[str]] = sys.stderr,
        level: Optional[Union[int, str]] = None,
        formatter: logging.Formatter = StackFormatter,  # type: ignore
    ) -> None:
        """Initialize the stream handler."""

        super().__init__(TTYInspector(stream), level, formatter)


stderr = StreamHandler()
stdout = StreamHandler(sys.stdout)


class Logger(logging.LoggerAdapter):
    """Logger instance to represent a logging channel.

    This instance uses a ``LoggerAdapter`` which makes it easier to
    specify contextual information in logging output.

    .. seealso::

        :py:meth:`logging.LoggerAdapter.process`

    """

    def process(
        self, msg: Any, kwargs: MutableMapping[str, Any]
    ) -> Tuple[Any, MutableMapping[str, Any]]:
        """Process the logging message and the keyword arguments passed
        to in to a logging call to insert contextual information.

        You can either manipute the message itself, the keyword
        arguments or both. Return the message and modified kwargs to
        suit your needs.

        :param msg: Logged message.
        :param kwargs: Keyword arguments with contextual information.
        :returns: Tuple of message and modified kwargs.

        """

        extra = self.extra.copy()  # type: ignore
        if "extra" in kwargs:
            extra.update(kwargs.pop("extra"))
        for name in kwargs.keys():
            if name == "exc_info":
                continue
            extra[name] = kwargs.pop(name)
        kwargs["extra"] = extra
        return msg, kwargs

    def debug(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        """Log message with ``DEBUG`` severity level."""

        self.logger._log(10, msg, args, **kwargs)

    def info(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        """Log message with ``INFO`` severity level."""

        self.logger._log(20, msg, args, **kwargs)

    def warning(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        """Log message with ``WARNING`` severity level."""

        self.logger._log(30, msg, args, **kwargs)

    def error(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        """Log message with ``ERROR`` severity level."""

        self.logger._log(40, msg, args, **kwargs)

    def critical(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        """Log message with ``CRITICAL`` severity level."""

        self.logger._log(50, msg, args, **kwargs)

    def exception(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        """Log message with ``CRITICAL`` severity level."""

        self.logger._log(60, msg, args, True, **kwargs)

    fatal = critical
    warn = warning


def get_logger(name: Optional[str] = None, **kwargs: Any) -> Logger:
    """Return a logger with the specified name.

    :param name: Logging channel name, defaults to None.
    :returns: Logger instance.

    .. seealso::

        :py:func:`logging.getLogger`

    """

    return Logger(logging.getLogger(name), kwargs)


def create_logger(**kwargs: Any) -> Logger:
    """Create logger for logging system.

    The default behavior is to create a ``RotatingFileHandler`` and
    ``StreamHandler`` which writes to a output log file and sys.stderr
    respectively and then set level for logging events to the handlers.

    :returns: Logger instance.

    .. note::

        This implementation is based on :py:func:`logging.basicConfig`.

    """

    root = logging.getLogger(None)
    for handler in root.handlers[:]:
        root.removeHandler(handler)
        handler.close()
    if len(root.handlers) == 0:
        level = kwargs.get("level", logging.INFO)
        root.setLevel(level)
        format = kwargs.get("format", None)
        datefmt = kwargs.get("datefmt", None)
        formatter = StackFormatter(format, datefmt)
        handlers = kwargs.get("handlers", None)
        if handlers is None:
            handlers = []
            stream = kwargs.get("stream", None)
            handlers.append(StreamHandler(stream, level, formatter))
            filename = kwargs.get("filename", None)
            filemode = kwargs.get("filemode", "a")
            if filename:
                handlers.append(
                    RotatingFileHandler(
                        filename, filemode, level=level, formatter=formatter
                    )
                )
        for handler in handlers:
            handler.add_handler(root)  # type: ignore
        capture_warnings = kwargs.get("capture_warnings", True)
        logging.captureWarnings(capture_warnings)
    name = kwargs.get("name", None)
    return get_logger(name, **kwargs)
