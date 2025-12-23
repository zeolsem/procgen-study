from util.timeit import time_it
from .value_noise import Point2D, ValueNoise1D, ValueNoise2D
import pygame
import numpy as np


def interpolate1D(
    noise: ValueNoise1D, samples: int = 200, offset: int = 0
) -> list[float]:
    indices = np.arange(samples, dtype=np.float64)
    points = (indices + offset) / samples * noise.max_vertices
    return noise.eval_batch(points).tolist()


def interpolate2D(
    noise: ValueNoise2D, substep: int = 10, offset: Point2D = (0, 0)
) -> list[list[float]]:
    samples = noise.resolution * substep
    
    x_indices = np.arange(samples, dtype=np.float64)
    y_indices = np.arange(samples, dtype=np.float64)
    x_grid, y_grid = np.meshgrid(x_indices, y_indices, indexing='ij')
    
    x_points = (x_grid + offset[0]) / samples * noise.resolution
    y_points = (y_grid + offset[1]) / samples * noise.resolution
    
    result = noise.eval_batch(x_points, y_points)
    return result.tolist()


def fractalise(
    octaves: list[ValueNoise1D], samples: int = 200, offset: int = 0
) -> list[float]:
    indices = np.arange(samples, dtype=np.float64)
    
    result = np.zeros(samples, dtype=np.float64)
    
    for octave_idx, octave in enumerate(octaves):
        points = (indices + offset) / samples * octave.max_vertices
        octave_values = octave.eval_batch(points)
        result += octave_values / (2 ** octave_idx)
    
    return result.tolist()


def fractalise2D(
    octaves: list[ValueNoise2D], substep: int = 10, offset: tuple[int, int] = (0, 0)
) -> list[list[float]]:
    samples = octaves[0].resolution * substep
    ox, oy = offset
    
    x_indices = np.arange(samples, dtype=np.float64)
    y_indices = np.arange(samples, dtype=np.float64)
    x_grid, y_grid = np.meshgrid(x_indices, y_indices, indexing='ij')
    
    x_grid = x_grid + ox
    y_grid = y_grid + oy
    
    result = np.zeros((samples, samples), dtype=np.float64)
    
    for octave_idx, octave in enumerate(octaves):
        scale = octave.resolution / samples
        amplitude = 1.0 / (2 ** octave_idx)
        
        x_scaled = x_grid * scale
        y_scaled = y_grid * scale
        
        octave_values = octave.eval_batch(x_scaled, y_scaled)
        result += octave_values * amplitude
    
    return result.tolist()


def plot_points(
    surface: pygame.Surface,
    points: list[float],
    offset=0.1,
    point_limit: int | None = None,
) -> None:
    screen_width, screen_height = surface.get_size()
    points = points[:point_limit] if point_limit else points

    previous_center = None
    for index, point in enumerate(points):
        center = (
            index / len(points) * screen_width,
            offset * screen_height + point * 40,
        )
        if previous_center:
            pygame.draw.line(surface, "#ff0000", previous_center, center)
            pygame.draw.circle(surface, "#ff0000", center, 2)
        previous_center = center


def plot_points2D(
    surface: pygame.Surface,
    points: list[list[float]],
    color: str = "#ddddff",
    scale: float = 40,
) -> None:
    screen_width, screen_height = surface.get_size()
    grid_height = len(points)
    grid_width = len(points[0]) if grid_height > 0 else 0
    
    if grid_height == 0 or grid_width == 0:
        return
    
    points_array = np.array(points, dtype=np.float64)
    
    x_screen = np.arange(grid_width) / grid_width * screen_width
    y_screen = np.arange(grid_height) / grid_height * screen_height
    
    x_grid, y_grid = np.meshgrid(x_screen, y_screen, indexing='ij')
    
    adjusted_y = y_grid + points_array.T * scale
    
    x_pixels = np.round(x_grid).astype(np.int32)
    y_pixels = np.round(adjusted_y).astype(np.int32)
    
    color_hex = color.lstrip('#')
    rgb = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
    color_obj = pygame.Color(*rgb)
    
    mask = (x_pixels >= 0) & (x_pixels < screen_width) & (y_pixels >= 0) & (y_pixels < screen_height)
    valid_coords = list(zip(x_pixels[mask].flat, y_pixels[mask].flat))
    
    for x, y in valid_coords:
        surface.set_at((int(x), int(y)), color_obj)
