from random import random, seed
from math import floor
from typing import Callable


Point = float
RemapFunction = Callable[[float], float]


def lerp(low: float, high: float, t: float) -> float:
    return low * (1 - t) + high * t


class ValueNoise1D:
    def __init__(
        self,
        max_vertices: int = 10,
        seed_=0,
        remap_function: RemapFunction = lambda x: x,
    ) -> None:
        self.seed = seed(seed_)
        self.max_vertices = max_vertices
        self.vertices = [random() for _ in range(max_vertices)]
        self.interpolate_function = remap_function

    def eval(self, point: Point, offset: int = 0):
        lower_index = (floor(point) + offset) % self.max_vertices
        higher_index = 0 if lower_index >= self.max_vertices - 1 else lower_index + 1
        t = ((point + offset) % self.max_vertices) - lower_index

        t = self.interpolate_function(t)

        return lerp(
            self.vertices[lower_index],
            self.vertices[higher_index],
            t,
        )
