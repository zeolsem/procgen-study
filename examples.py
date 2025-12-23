from random import randint
import pygame
from util import (
    ValueNoise1D,
    cosine,
    smoothstep,
    perlin_smoothstep,
    fractalise,
    plot_points,
    interpolate1D,
    fractalise2D,
    plot_points2D,
)
from util.value_noise import ValueNoise2D


def value_noise_1d_example():
    pygame.init()
    screen = pygame.display.set_mode((640, 640))
    clock = pygame.time.Clock()
    running = True
    time_flow = True

    SEED = 69
    VERTS = 256

    noise1 = ValueNoise1D(max_vertices=VERTS, seed_=SEED)
    noise2 = ValueNoise1D(max_vertices=VERTS, seed_=SEED, remap_function=cosine)
    noise3 = ValueNoise1D(max_vertices=VERTS, seed_=SEED, remap_function=smoothstep)
    noise4 = ValueNoise1D(
        max_vertices=VERTS, seed_=SEED, remap_function=perlin_smoothstep
    )

    timestamp = 0
    while running:
        if time_flow:
            timestamp += 0.2
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    time_flow = not time_flow
            if event.type == pygame.QUIT:
                running = False

        screen.fill("#000000")

        _timestamp = int(timestamp)
        plot_points(screen, noise1.vertices, offset=0.1, point_limit=64)
        plot_points(
            screen,
            interpolate1D(noise1, offset=_timestamp, samples=2560),
            offset=0.3,
            point_limit=64,
        )
        plot_points(
            screen,
            interpolate1D(noise2, offset=_timestamp, samples=2560),
            offset=0.5,
            point_limit=64,
        )
        plot_points(
            screen,
            interpolate1D(noise3, offset=_timestamp, samples=2560),
            offset=0.7,
            point_limit=64,
        )
        plot_points(
            screen,
            interpolate1D(noise4, offset=_timestamp, samples=2560),
            offset=0.9,
            point_limit=64,
        )

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()


def fractal_value_noise_1d_example():
    pygame.init()
    screen = pygame.display.set_mode((640, 640))
    clock = pygame.time.Clock()
    running = True
    time_flow = True

    octaves1 = [ValueNoise1D(16 * (i + 1), randint(0, 32565)) for i in range(8)]
    octaves2 = [ValueNoise1D(16 * (i + 1), randint(0, 32565), cosine) for i in range(8)]
    octaves3 = [
        ValueNoise1D(16 * (i + 1), randint(0, 32565), perlin_smoothstep)
        for i in range(8)
    ]
    octaves4 = [
        ValueNoise1D(16 * (i + 1), randint(0, 32565), perlin_smoothstep)
        for i in range(16)
    ]

    timestamp = 0
    while running:
        if time_flow:
            timestamp += 0.5
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    time_flow = not time_flow
            if event.type == pygame.QUIT:
                running = False

        screen.fill("#000000")

        _timestamp = int(timestamp)
        plot_points(screen, fractalise(octaves1, offset=_timestamp), offset=0.2)
        plot_points(screen, fractalise(octaves2, offset=_timestamp), offset=0.4)
        plot_points(screen, fractalise(octaves3, offset=_timestamp), offset=0.6)
        plot_points(screen, fractalise(octaves4, offset=_timestamp), offset=0.8)

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()


def example_template():
    pygame.init()
    screen = pygame.display.set_mode((640, 640))
    clock = pygame.time.Clock()
    running = True
    time_flow = True

    timestamp = 0
    while running:
        if time_flow:
            timestamp += 0.5
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    time_flow = not time_flow
            if event.type == pygame.QUIT:
                running = False

        screen.fill("#000000")
        pygame.display.flip()

        clock.tick(60)

    pygame.quit()


def value_noise_2d_example():
    pygame.init()
    screen = pygame.display.set_mode((640, 640))
    clock = pygame.time.Clock()
    running = True
    time_flow = True

    octaves = [ValueNoise2D(seed_=randint(0, 32565)) for _ in range(8)]
    scale = 0
    
    # FPS and timing tracking
    font = pygame.font.Font(None, 28)
    frame_count = 0

    timestamp = 0
    while running:
        if time_flow:
            timestamp += 0.5
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    time_flow = not time_flow
                if event.key == pygame.K_d:
                    scale += 1
                if event.key == pygame.K_a:
                    scale -= 1
            if event.type == pygame.QUIT:
                running = False

        screen.fill("#000000")
        
        fractal_data = fractalise2D(octaves, offset=(int(timestamp), int(timestamp)))
        plot_points2D(screen, fractal_data, scale=scale)
        
        pygame.display.flip()
        clock.tick(60)

        if frame_count % 60 == 0:
            print(clock.get_fps())
        frame_count += 1

    pygame.quit()
