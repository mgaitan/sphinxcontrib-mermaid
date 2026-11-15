from collections import OrderedDict  # noqa: F401


class Shape:
    pass


class Round(Shape):
    pass


class Square(Shape):
    pass


class Squircle(Round, Square):
    pass


class Lonely:
    pass


class ShapeError(Exception):
    pass
