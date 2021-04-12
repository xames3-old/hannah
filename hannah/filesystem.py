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


class IOHelper(object):
    """A helper class to assist with the underlying metadata of the
    file.

    IOHelper provides with the metadata like the file name, stem,
    suffix (extension), parent directory, etc. This can be used in APIs
    as a Mixin with IOBase's subclasses.

    :param filename: Absolute path of the file whose information needs
        to be extracted.

    """

    def __init__(self, filename: str) -> None:
        """Construct file object."""

        self.filename = filename

    @property
    def parent(self) -> str:
        """Return parent directory of the file."""

        return os.path.dirname(self.filename)

    @property
    def basename(self) -> str:
        """Return only name-part of the file with extension."""

        return os.path.basename(self.filename)

    name = basename

    @property
    def suffix(self) -> str:
        """Return extension of the file."""

        return os.path.splitext(self.filename)[-1]

    @property
    def stem(self) -> str:
        """Return only name-part of the file without extension."""

        return os.path.splitext(os.path.basename(self.filename))[0]

    @property
    def size(self) -> int:
        """Return size of the file in bytes."""

        return os.stat(self.filename).st_size

    @property
    def siblings(self) -> List[str]:
        """Return list of matching files in the parent directory."""

        return sorted(
            fnmatch.filter(os.listdir(self.parent), f"{self.name}*.?")
        ) + [self.basename]

    @property
    def index(self) -> int:
        """Return count of files with same name."""

        return len(self.siblings)

    @property
    def lines(self) -> int:
        """Return count of files with same name."""

        return sum(1 for _ in open(self.filename))


class IOWriter(IOBase, IOHelper):
    """..."""

    def __init__(
        self,
        filename: str,
        mode: str = "w",
        encoding: Optional[str] = None,
        **kwargs: Dict[str, Any],
    ) -> None:
        super().__init__(filename)
        if not isinstance(mode, str):
            raise TypeError(f"Invalid mode: {mode}")
        if not set(mode) <= set("xrwabt+"):
            raise ValueError(f"Invalid mode: {mode}")
        if "x" in mode or "w" in mode or "a" in mode:
            self._writable = True
            self._readable = False
        elif "r" in mode:
            self._check_readable()
        elif "+" in mode:
            self._readable = True
            self._writable = True
        self.maxbytes = kwargs.get("maxbytes", -1)
        self.maxlines = kwargs.get("maxlines", -1)
        self.ignore_linebreak = kwargs.get("ignore_linebreak", True)
        if self.ignore_linebreak:
            self.maxlines -= 1  # type: ignore
        if self.maxbytes > 0 or self.maxlines > 0:  # type: ignore
            mode = "a"
        self.mode = mode
        if encoding is None:
            encoding = os.device_encoding(0)
        self.encoding = encoding
        self._closed = False
        self.idx = self.index
        self.open()

    def __repr__(self) -> str:
        """Return string representation of the class."""

        klass = f"{type(self).__module__}.{type(self).__qualname__}"
        if self.closed:
            return f"<{klass}>"
        return f"<{klass} filename={self.name!r}>"

    def __enter__(self) -> "IOWriter":
        """Context management protocol. Return self."""

        self._check_closed()
        return self

    def open(self) -> None:
        """Open file for the I/O operations."""

        self.fd = open(self.filename, self.mode, encoding=self.encoding)
        self._closed = False

    def close(self) -> None:
        """Close the file.

        A closed file cannot be used for further I/O operations. The
        close() may be called more than once without error.

        """

        if not self._closed:
            self.fd.close()
        self._closed = True

    def flush(self) -> None:
        """Flush write buffers, if applicable.

        This is not implemented for read-only and non-blocking streams.
        Flushing stream ensures that the data has been cleared from the
        internal buffer without any guarantee on whether its written to
        the local disk.

        This means that the data would survive an application crash but
        not necessarily an OS crash.

        """

        self._check_closed()
        self._check_writable()
        self.fd.flush()

    def write(self, *args: Any, **kwargs: Any) -> None:
        """Write data to the file.

        This is done after clearing the contents of the file on first
        write and then appending on subsequent calls. This method also
        rotates the file if provided with correct argument.

        """

        self._check_closed()
        self._check_writable()
        sep, end = kwargs.get("sep", " "), kwargs.get("end", "\n")
        self.fd.write(
            sep.join(list(map(lambda x: "" if x is None else str(x), args)))
            + end
        )
        self.flush()
        self.rotate()

    def rotate(self) -> None:
        """..."""

        rollover = False
        if self.maxbytes and self.maxbytes > 0:  # type: ignore
            if self.size > self.maxbytes:  # type: ignore
                rollover = True
        if self.maxlines and self.maxlines > 0:  # type: ignore
            if self.lines > self.maxlines:  # type: ignore
                rollover = True
        if rollover:
            self._check_closed()
            self.close()
            if os.path.exists(self.filename):
                os.rename(self.filename, f"{self.filename}.{self.idx}")
                self.idx += 1
            else:
                raise FileNotFoundError
            self.open()
