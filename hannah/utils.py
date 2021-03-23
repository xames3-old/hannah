"""Utilities: Collection of utilities."""

from threading import Lock
from typing import Any
from typing import Dict

__all__ = ["SingletonMeta"]


class SingletonMeta(type):
    """Thread-safe implementation of singleton design pattern.

    It ensures only a ``single instance`` of the class is available
    at runtime. See singletons_ in python and their implementations_.

    .. code-block:: python

        class Foo(metaclass=SingletonMeta):

            def __init__(self):
                pass

    .. _singletons: https://refactoring.guru/design-patterns/singleton/python/example
    .. _implementations: https://stackoverflow.com/q/6760685

    """

    instances: Dict["SingletonMeta", type] = {}
    lock = Lock()

    def __call__(cls, *args: Any, **kwargs: Any) -> type:
        """Callable singleton instance."""
        with cls.lock:
            if cls not in cls.instances:
                cls.instances[cls] = super().__call__(*args, **kwargs)
        return cls.instances[cls]
