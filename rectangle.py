from collections.abc import Iterator


class Rectangle:
    def __init__(self, length: int, width: int):
        if type(length) is not int or type(width) is not int:
            raise TypeError("length and width must both be integers")

        self.length = length
        self.width = width

    def __iter__(self) -> Iterator[dict]:
        yield {"length": self.length}
        yield {"width": self.width}
