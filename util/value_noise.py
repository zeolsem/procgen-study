from random import random, seed
from math import floor
from typing import Callable

import numpy as np
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

    def eval_batch(self, points: np.ndarray) -> np.ndarray:
        """
        Vectorized evaluation for 1D noise.
        
        Args:
            points: 1D numpy array of points to evaluate
            
        Returns:
            1D numpy array of noise values
        """
        points = np.asarray(points, dtype=np.float64)
        lower_indices = np.floor(points).astype(np.int32) % self.max_vertices
        higher_indices = np.where(
            lower_indices >= self.max_vertices - 1,
            0,
            lower_indices + 1
        )
        
        t = (points % self.max_vertices) - lower_indices
        t_remapped = np.vectorize(self.remap_function)(t)
        
        lower_vals = np.array([self.vertices[i] for i in lower_indices])
        higher_vals = np.array([self.vertices[i] for i in higher_indices])
        
        return lower_vals * (1 - t_remapped) + higher_vals * t_remapped


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
        self.vertices = np.array([
            [random() for _ in range(resolution)] for _ in range(resolution)
        ], dtype=np.float64)
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

    def eval_batch(self, x_points: np.ndarray, y_points: np.ndarray) -> np.ndarray:
        """
        Vectorized evaluation for 2D noise.
        
        Args:
            x_points: numpy array of x coordinates
            y_points: numpy array of y coordinates (same shape as x_points)
            
        Returns:
            numpy array of noise values (same shape as inputs)
        """
        x_points = np.asarray(x_points, dtype=np.float64)
        y_points = np.asarray(y_points, dtype=np.float64)
        
        original_shape = x_points.shape
        x_flat = x_points.ravel()
        y_flat = y_points.ravel()
        
        x_floor = np.floor(x_flat).astype(np.int32)
        y_floor = np.floor(y_flat).astype(np.int32)
        
        tx = x_flat - x_floor
        ty = y_flat - y_floor
        
        left = x_floor & self.resolution_mask
        right = (x_floor + 1) & self.resolution_mask
        top = y_floor & self.resolution_mask
        bottom = (y_floor + 1) & self.resolution_mask
        
        # Direct vertex lookup using numpy fancy indexing
        top_left = self.vertices[left, top]
        top_right = self.vertices[right, top]
        bottom_left = self.vertices[left, bottom]
        bottom_right = self.vertices[right, bottom]
        
        # Vectorized interpolation
        smooth_x = np.vectorize(self.remap_function)(tx)
        smooth_y = np.vectorize(self.remap_function)(ty)
        
        # Bilinear interpolation
        a = top_left * (1 - smooth_x) + top_right * smooth_x
        b = bottom_left * (1 - smooth_x) + bottom_right * smooth_x
        result = a * (1 - smooth_y) + b * smooth_y
        
        return result.reshape(original_shape)
