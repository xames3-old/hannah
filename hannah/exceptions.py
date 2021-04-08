"""
Exceptions: Collections of all the exceptions raised by H.A.N.N.A.H.

"""

import os
import textwrap
from typing import Any

__all__ = [
    "HannahException",
    "UnsupportedOperation",
]


class HannahException(Exception):
    """
    Base class for all the exceptions raised by H.A.N.N.A.H.

    It provides a way to safely raise exceptions when there is some
    valid reason for it to be raised. In case the exception is raised
    by the system and there is no reason for it, then it is considered
    as a probable bug and steps to report this bug are displayed.

    .. code-block:: python

        class FooError(HannahException):
            pass

        raise FooError(msg='Something went wrong', valid=True)

    """

    def __init__(self, valid: bool = False, **kwargs: Any) -> None:

        for name, value in kwargs.items():
            setattr(self, name, value)
        self.msg = self.msg if self.msg else ""  # type: ignore
        if not valid and self.msg:
            self.msg += self.report()
        super().__init__(self.msg)

    def __str__(self) -> str:
        """Return formatted message output."""

        return self.msg.format(**vars(self))  # type: ignore

    def report(self) -> str:
        """Return bug report warning."""

        try:
            width = os.get_terminal_size().columns
        except OSError:
            width = 80
        title = " YIKES! There's a bug! ".center(width, "-")
        msg = (
            "If you are seeing this, then there is something wrong with "
            "H.A.N.N.A.H and not your code. Please report this bug here: "
            '"https://github.com/kaamiki/hannah/issues/new" so that we can '
            "fix the issue at the earliest. It would be a great help if you "
            "could provide the steps, traceback information or even a sample "
            "code for reproducing this bug while submitting an issue."
        )
        wrapper = textwrap.TextWrapper(width)
        return f"\n\n{title}\n{wrapper.fill(msg)}\n\n"


class UnsupportedOperation(HannahException):
    """Exception to be raised when operations which are not supported
    are called."""

    pass
