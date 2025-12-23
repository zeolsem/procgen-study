from util.timeit import time_it
from .value_noise import Point2D, ValueNoise1D, ValueNoise2D
import pygame


def interpolate1D(
    noise: ValueNoise1D, samples: int = 200, offset: int = 0
) -> list[float]:
    return [
        noise.eval((i + offset) / (samples) * (noise.max_vertices))
        for i in range(samples)
    ]


def interpolate2D(
    noise: ValueNoise2D, substep: int = 10, offset: Point2D = (0, 0)
) -> list[list[float]]:
    samples = noise.resolution * substep
    return [
        [
            noise.eval(
                (
                    (x + offset[0]) / samples * noise.resolution,
                    (y + offset[1]) / samples * noise.resolution,
                )
            )
            for x in range(samples)
        ]
        for y in range(samples)
    ]


def fractalise(
    octaves: list[ValueNoise1D], samples: int = 200, offset: int = 0
) -> list[float]:
    points = []
    for i in range(samples):
        v = 0
        for index, octave in enumerate(octaves):
            dv = (
                octave.eval((i + offset) / (samples) * (octave.max_vertices)) / 2**index
            )
            v += dv
        points.append(v)
    return points


@time_it
def fractalise2D(
    octaves: list[ValueNoise2D], substep: int = 10, offset: tuple[int, int] = (0, 0)
) -> list[list[float]]:
    samples = octaves[0].resolution * substep

    octave_data = [
        (
            octave.eval,
            octave.resolution / samples,
            1.0 / (2**i),
        )
        for i, octave in enumerate(octaves)
    ]

    ox, oy = offset
    points = []

    for x in range(samples):
        row = []
        fx = x + ox
        for y in range(samples):
            fy = y + oy
            value = 0.0

            for eval_fn, scale, amp in octave_data:
                value += eval_fn((fx * scale, fy * scale)) * amp

            row.append(value)
        points.append(row)

    return points


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


@time_it
def plot_points2D(
    surface: pygame.Surface,
    points: list[list[float]],
    color: str = "#ddddff",
    scale: float = 40,
) -> None:
    """
    Plot a 2D list of points to the entire screen.

    Args:
        surface: The pygame surface to draw on
        points: 2D list of float values (output from interpolate2D)
        color: Color to draw the points in
        scale: Scaling factor for point values
    """
    screen_width, screen_height = surface.get_size()
    grid_height = len(points)
    grid_width = len(points[0]) if grid_height > 0 else 0

    for y, row in enumerate(points):
        for x, point in enumerate(row):
            # Map grid coordinates to screen coordinates
            screen_x = x / grid_width * screen_width if grid_width > 0 else 0
            screen_y = y / grid_height * screen_height if grid_height > 0 else 0

            # Adjust height by point value
            adjusted_y = screen_y + point * scale

            center = (screen_x, adjusted_y)
            pygame.draw.circle(surface, color, center, 1)
