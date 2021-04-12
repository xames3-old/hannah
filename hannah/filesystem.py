"""Filesystem: Utility for reading-writing files."""

import fnmatch
import os
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional

from hannah import UnsupportedOperation


class IOBase(object):
    """The base class for all I/O classes.

    This class provides dummy implementation for many methods that
    derived class can override selectively; the default implementation
    represents a file that cannot be read or written.

    Even though IOBase does not declare read or write because their
    signatures will vary, implementations should consider those methods
    part of the interface. Also, implmentations may raise
    UnsupportedOperation when operations they do not support are
    called.

    Note that calling any method (even inquiries) on a closed stream
    is undefined. Implementation may raise error in this case.

    IOBase (and its subclasses) support the iterator protocol,
    meaning that an IOBase object can be iterated over yielding the
    lines in a stream.

    IOBase also supports the :keyword:`with` statement.

    """

    _readable = False
    _writable = False

    def __enter__(self) -> "IOBase":
        """Context management protocol. Return self."""

        self._check_closed()
        return self

    def __exit__(self, *args: Any) -> None:
        """Context management protocol. Calls close()."""

        self.close()

    def __iter__(self) -> "IOBase":
        """Iterator protocol. Return self."""

        self._check_closed()
        return self

    def flush(self) -> None:
        """Flush write buffer, if applicable.

        This is not implemented for read-only and non-blocking streams.

        """

        self._check_closed()

    _closed = False

    def close(self) -> None:
        """Flush and close the I/O object.

        This method has no effect if the file is already closed.

        """

        if not self._closed:
            try:
                self.flush()
            finally:
                self._closed = True

    @property
    def closed(self) -> bool:
        """Return True iff the file has been closed."""

        return self._closed

    def _unsupported(self, name: str) -> None:
        """Raise UnsupportedOperation exception for unsupported
        operations.

        :raises UnsupportedOperation: When unsupported operation is
            called.

        """

        raise UnsupportedOperation(
            msg=f"{type(self).__name__}.{name}() not supported",
            valid=True,
        )

    def _check_closed(self) -> None:
        """Raise ValueError if the file is closed.

        :raises ValueError: When operation is called on a closed file.

        """

        if self.closed:
            raise ValueError("I/O operation on closed file")

    def _check_readable(self) -> None:
        """Check if the file is open in readable mode, else raise an
        error.

        """

        if not self._readable:
            raise UnsupportedOperation(
                msg="File not open in reading mode",
                valid=True,
            )

    def _check_writable(self) -> None:
        """Check if the file is open in writable mode, else raise an
        error.

        """

        if not self._writable:
            raise UnsupportedOperation(
                msg="File not open in writing mode",
                valid=True,
            )

    def read(self, size: int) -> None:
        """..."""

        self._unsupported("read")

    def readline(self, limit: int) -> None:
        """..."""

        self._unsupported("readline")

    def readlines(self, hint: int) -> None:
        """..."""

        self._unsupported("readlines")

    def write(self, *args: Any) -> None:
        """..."""

        self._unsupported("write")

    def writelines(self, lines: Iterable[Any]) -> None:
        """..."""

        self._unsupported("writelines")

    def rotate(self) -> None:
        """..."""

        self._unsupported("rotate")
