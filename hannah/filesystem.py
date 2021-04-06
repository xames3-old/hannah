"""Filesystem: Utility for reading-writing files."""

import fnmatch
import os
from typing import List

from hannah import SingletonMeta

READABLE_MODES = ("r", "r+", "w+", "a+", "rb", "rb+", "rt")
WRITABLE_MODES = ("w", "w+", "a", "a+", "r+", "wb", "wb+", "wt")
SUPPORTED_FILEMODES = (
    "r",
    "w",
    "a",
    "r+",
    "w+",
    "a+",
    "t",
    "x",
    "rb",
    "wb",
    "rt",
    "wt",
    "rb+",
    "wb+",
)


class BaseFile(object, metaclass=SingletonMeta):
    """..."""

    def __init__(self, filename: str) -> None:
        """Initialize file."""

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
        )

    @property
    def index(self) -> int:
        """Return count of files with same name."""

        return len(self.siblings) + 1

    @property
    def lines(self) -> int:
        """Return count of files with same name."""

        return sum(1 for _ in open(self.filename))
