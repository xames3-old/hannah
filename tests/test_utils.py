from hannah.utils import SingletonMeta


class Foo(metaclass=SingletonMeta):
    pass


def test_singleton_instances() -> None:
    x1 = Foo()
    x2 = Foo()
    assert x1 == x2
    assert x1 is x2
