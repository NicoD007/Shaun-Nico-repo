# add shape to diagram
# add getShape method to diagram
# change size to int in diagram
# add makeShape method to diagram



import random


class Obstacles:
    "Represents an obstacle in the environment."

    def __init__(self, size: int, posX: int, posY: int, isMovable: bool, shape: list[list[int]] | None = None) -> None:
        self._size = size
        self._pos_x = posX
        self._pos_y = posY
        self._is_movable = isMovable
        self._shape = shape if shape is not None else self.makeShape()

    def makeShape(self) -> list[list[int]]:
        if self._size <= 1:
            return [[2]]
        if self._size <= 2:
            shapes = [
                [[2, 1],
                 [1, 2]],

                [[2, 2],
                 [2, 2]],

                [[1, 2],
                 [2, 1]],

                [[2, 1],
                 [2, 2]],

                [[1, 2],
                 [2, 2]],
            ]
            return random.choice(shapes)
        if self._size <= 3.0:
            shapes = [
                [[2, 1, 2],
                 [1, 1, 1],
                 [2, 1, 2]],
                 
                [[1, 1, 2],
                 [1, 2, 2],
                 [2, 2, 2]],

                [[2, 2, 2],
                 [1, 1, 1],
                 [2, 2, 2]],

                [[1, 1, 2],
                 [2, 2, 2],
                 [1, 1, 2]],

                [[1, 2, 2],
                 [1, 1, 2],
                 [2, 2, 2]],

                [[2, 2, 2],
                 [2, 2, 2],
                 [2, 2, 2]],
            ]
            return random.choice(shapes)
        # Larger obstacles use a simple filled square pattern
        side = int(self._size)
        return [[2 for _ in range(side)] for _ in range(side)]

    def getPosition(self) -> tuple:
        return (self._pos_x, self._pos_y)

    def getSize(self) -> float:
        return self._size

    def getShape(self) -> list[list[int]]:
        return self._shape

    def move(self, posX: int, posY: int) -> None:
        pass #will not be implemented doe to time frame