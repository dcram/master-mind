from enum import Enum
from typing import List

class Color(Enum):
    blue: int = 0
    green: int = 1
    orange: int = 2
    pink: int = 3
    purple: int = 4
    red: int = 5
    # white: int = 6
    # yellow: int = 7

    @staticmethod
    def values() -> List["Color"]:
        return [e.value for e in Color]

    @staticmethod
    def from_int(code: int) -> "Color":
        return next(c for c in Color.values() if c == code)
    @staticmethod
    def random() -> List["Color"]:
        import random
        values = Color.values()
        idx = random.randint(0, len(values) - 1)
        return values[idx]
