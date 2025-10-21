from cmath import sqrt


def solve_quadratic(a: float, b: float, c: float) -> tuple[float, float]:
    """
    Find x where ax^2 + bx + c = 0
    >>> solve_quadratic(20.6, -10.3, 8.7)
    (0.25, 0.25)
    >>> solve_quadratic(2.5, 25.0, 20.0)
    (-9.12310562561766, -0.8768943743823392)
    """
    squirt = sqrt(b**2 - 4 * a * c)
    left, right = (-b - squirt.real) / (2 * a), (-b + squirt.real) / (2 * a)
    return (left, right) if left < right else (right, left)
