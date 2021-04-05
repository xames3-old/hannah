"""Exceptions: Collections of all the exceptions raised by Hannah."""

import os
import textwrap
from typing import Any
from typing import Optional


class HannahError(Exception):
    """Base exception class for all errors raised by Hannah."""

    msg: Optional[str] = None

    def __init__(self, valid: bool = False, **kwargs: Any) -> None:

        if not valid and self.msg:
            self.msg += self.report()
        super().__init__(self.msg)
        for name, value in kwargs.items():
            setattr(self, name, value)

    def __str__(self) -> str:
        """Return formatted message output."""

        return self.msg.format(**vars(self)) if self.msg else ""

    def report(self) -> str:
        """Return bug report warning."""

        width = os.get_terminal_size().columns
        title = "YIKES! There's a bug!".center(width, "-")
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


class FileSystemError(HannahError):
    """Base class for all FileSystem related exceptions."""

    pass


class FileAlreadyClosedError(FileSystemError):
    """Exception to be raised when trying to close a closed file."""

    msg = "File {filename!r} is already closed"


class PermissionDeniedError(FileSystemError):
    """Exception to be raised when permissions aren't provided to file."""

    msg = "File {filename!r} doesn't have enough permissions"
