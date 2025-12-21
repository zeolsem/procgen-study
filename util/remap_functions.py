from math import cos, pi


def cosine(t: float) -> float:
    try:
        return (1 - cos(t * pi)) * 0.5
    except ValueError as e:
        raise e


def smoothstep(t: float) -> float:
    return t * t * (3 - 2 * t)


def perlin_smoothstep(t: float) -> float:
    return 6 * t**5 - 15 * t**4 + 10 * t**3
