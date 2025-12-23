from random import random, seed
from math import floor
from typing import Callable

from util.remap_functions import smoothstep
from util.timeit import time_it


Point1D = float
Point2D = tuple[float, float]

RemapFunction = Callable[[float], float]


def lerp(low: float, high: float, t: float) -> float:
    return low * (1 - t) + high * t


def bilinear_interpolation(
    top_left: float,
    top_right: float,
    bottom_left: float,
    bottom_right: float,
    tx: float,
    ty: float,
) -> float:
    a = lerp(top_left, top_right, tx)
    b = lerp(bottom_left, bottom_right, tx)
    return lerp(a, b, ty)


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
        self.remap_function = remap_function

    def eval(self, point: Point1D):
        lower_index = floor(point) % self.max_vertices
        higher_index = 0 if lower_index >= self.max_vertices - 1 else lower_index + 1
        t = (point % self.max_vertices) - lower_index

        t = self.remap_function(t)

        return lerp(
            self.vertices[lower_index],
            self.vertices[higher_index],
            t,
        )


class ValueNoise2D:
    def __init__(
        self,
        resolution: int = 16,
        seed_: int = 0,
        remap_function: RemapFunction = smoothstep,
    ) -> None:
        self.seed = seed(seed_)
        self.resolution = resolution
        self.resolution_mask = resolution - 1
        self.vertices = [
            [random() for _ in range(resolution)] for _ in range(resolution)
        ]
        self.remap_function = remap_function

    def eval(self, point: Point2D):
        x_floor = floor(point[0])
        y_floor = floor(point[1])

        tx = point[0] - x_floor
        ty = point[1] - y_floor

        left = x_floor & self.resolution_mask
        right = (x_floor + 1) & self.resolution_mask
        top = y_floor & self.resolution_mask
        bottom = (y_floor + 1) & self.resolution_mask

        bottom_left = self.vertices[left][bottom]
        bottom_right = self.vertices[right][bottom]
        top_left = self.vertices[left][top]
        top_right = self.vertices[right][top]

        smooth_x = self.remap_function(tx)
        smooth_y = self.remap_function(ty)

        return bilinear_interpolation(
            top_left, top_right, bottom_left, bottom_right, smooth_x, smooth_y
        )
