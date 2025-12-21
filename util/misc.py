from .value_noise import ValueNoise1D
import pygame


def interpolate(
    noise: ValueNoise1D, samples: int = 200, offset: int = 0
) -> list[float]:
    return [
        noise.eval((i + offset) / (samples) * (noise.max_vertices))
        for i in range(samples)
    ]


def fractalise(
    octaves: list[ValueNoise1D], samples: int = 200, offset: int = 0
) -> list[float]:
    points = []
    for i in range(samples):
        v = 0
        for index, octave in enumerate(octaves):
            dv = octave.eval((i + offset) / (samples) * (octave.max_vertices)) / max(
                1, index
            )
            v += dv
        points.append(v)
    return points


def plot_points(surface: pygame.Surface, points: list[float], offset=0.1) -> None:
    screen_width, screen_height = surface.get_size()
    points = points[:64]

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
