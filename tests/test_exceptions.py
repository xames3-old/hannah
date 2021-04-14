from typing import Callable

import pytest
from hannah.exceptions import HannahException
from hannah.exceptions import UnsupportedOperation


def dummy_func(exc: Callable[..., None], msg: str, valid: bool) -> None:
    raise exc(msg=msg, valid=valid)  # type: ignore


@pytest.mark.parametrize(
    ("exc", "msg", "valid", "match"),
    (
        (
            HannahException,
            "A new HannahException raised",
            True,
            "HannahException",
        ),
        (
            HannahException,
            "Another HannahException raised",
            False,
            "https://github.com/",
        ),
        (
            UnsupportedOperation,
            "A new UnsupportedOperation raised",
            True,
            "UnsupportedOperation",
        ),
        (
            UnsupportedOperation,
            "Another UnsupportedOperation raised",
            False,
            "https://github.com/",
        ),
    ),
)
def test_hannah_exception(
    exc: Callable[..., None], msg: str, valid: bool, match: str
) -> None:
    with pytest.raises(exc, match=match):  # type: ignore
        dummy_func(exc, msg, valid)
