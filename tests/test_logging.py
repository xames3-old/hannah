import pytest
import typing

from hannah import Logger
from hannah import create_logger


def dummy_log_function(
    logger: Logger, msg: str, level: str, **extra: typing.Any
) -> None:
    getattr(logger, level)(msg, extra=extra)


default_formatter_expected_msg = (
    "{} [MainThread] tests.test_logging."
    "dummy_log_function:11 : Test {} message with default formatter\n"
)


@pytest.mark.parametrize(
    ("msg", "level", "expected"),
    (
        (
            "Test debug message with default formatter",
            "debug",
            "",
        ),
        (
            "Test info message with default formatter",
            "info",
            default_formatter_expected_msg.format("O", "info"),
        ),
        (
            "Test warning message with default formatter",
            "warn",
            default_formatter_expected_msg.format("N", "warning"),
        ),
        (
            "Test error message with default formatter",
            "error",
            default_formatter_expected_msg.format("R", "error"),
        ),
    ),
)
def test_with_default_format(
    capsys: typing.Any, msg: str, level: str, expected: str
) -> None:
    logger = create_logger()
    dummy_log_function(logger, msg, level)
    _, stderr = capsys.readouterr()
    assert stderr[20:] == expected


custom_formatter_expected_msg = (
    "{}:root:Test {} message with custom formatter\n"
)


@pytest.mark.parametrize(
    ("msg", "level", "expected"),
    (
        (
            "Test debug message with custom formatter",
            "debug",
            "",
        ),
        (
            "Test info message with custom formatter",
            "info",
            custom_formatter_expected_msg.format("INFO", "info"),
        ),
        (
            "Test warning message with custom formatter",
            "warn",
            custom_formatter_expected_msg.format("WARN", "warning"),
        ),
        (
            "Test error message with custom formatter",
            "error",
            custom_formatter_expected_msg.format("ERROR", "error"),
        ),
    ),
)
def test_with_custom_format(
    capsys: typing.Any, msg: str, level: str, expected: str
) -> None:
    logger = create_logger(format="%(levelname)s:%(name)s:%(message)s")
    dummy_log_function(logger, msg, level)
    _, stderr = capsys.readouterr()
    assert stderr == expected


formatter_with_extra_expected_msg = (
    "127.0.0.1:6969 - Test {} message with extra args\n"
)


@pytest.mark.parametrize(
    ("msg", "level", "expected"),
    (
        (
            "Test debug message with extra args",
            "debug",
            "",
        ),
        (
            "Test info message with extra args",
            "info",
            formatter_with_extra_expected_msg.format("info"),
        ),
        (
            "Test warning message with extra args",
            "warn",
            formatter_with_extra_expected_msg.format("warning"),
        ),
        (
            "Test error message with extra args",
            "error",
            formatter_with_extra_expected_msg.format("error"),
        ),
    ),
)
def test_with_extra_args(
    capsys: typing.Any, msg: str, level: str, expected: str
) -> None:
    logger = create_logger(format="%(addr)s:%(port)s - %(message)s")
    dummy_log_function(logger, msg, level, addr="127.0.0.1", port=6969)
    _, stderr = capsys.readouterr()
    assert stderr == expected
