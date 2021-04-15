import os
from typing import Any
from typing import Callable

import pytest
from hannah._io import IOBase
from hannah._io import IOHelper
from hannah._io import IOWriter
from hannah.exceptions import UnsupportedOperation

HERE = os.getcwd()
PATH = os.path.join(HERE, "io_helper_test.txt")
with open(PATH, "w") as fp:
    fp.write("This is a test.\n")


def dummy_io_base(name: str, args: Any) -> None:
    IOBase().__getattribute__(name)(args)


@pytest.mark.parametrize(
    ("name", "args"),
    (
        ("read", 0),
        ("readline", 0),
        ("readlines", 0),
        ("write", 0),
        ("writelines", []),
    ),
)
def test_io_base_rw(name: str, args: Any) -> None:
    with pytest.raises(UnsupportedOperation, match=rf"\w.+\.{name}\(\).+"):
        dummy_io_base(name, args)


def test_io_base_rotate() -> None:
    with pytest.raises(UnsupportedOperation, match=r"\w.+\.rotate\(\).+"):
        IOBase().rotate()


@pytest.mark.parametrize(
    ("props", "expected"),
    (
        ("parent", "/home/xames3/workshop/repositories/hannah"),
        ("basename", "io_helper_test.txt"),
        ("suffix", ".txt"),
        ("size", 16),
        ("siblings", ["io_helper_test.txt"]),
        ("index", 1),
        ("lines", 1),
    ),
)
def test_io_helper(props: str, expected: str) -> None:
    assert IOHelper(PATH).__getattribute__(props) == expected
    if props == "lines":
        os.remove(PATH)


@pytest.mark.parametrize(("mode", "exc"), ((42, TypeError), ("c", ValueError)))
def test_io_writer_invalid_modes(mode: str, exc: Callable[..., None]) -> None:
    with pytest.raises(exc, match="Invalid mode"):  # type: ignore
        IOWriter(PATH, mode=mode)


def test_io_writer_read() -> None:
    with pytest.raises(UnsupportedOperation, match="File not open"):
        IOWriter(PATH, mode="r").read(0)
