from typing import List, Tuple, Set
from .constants import STEP


def build_grid(x_limit: int, y_limit: int):
    xs = list(range(-x_limit, x_limit + 1, STEP))
    ys = list(range(-y_limit, y_limit + 1, STEP))
    points = [(x, y) for x in xs for y in ys]
    return xs, ys, points, set(points)


def check_constraints(path: List[Tuple[int, int]]):
    """Each step must be STEP or STEP*sqrt(2) -> squared length in {STEP*STEP, 2*STEP*STEP}."""
    allowed = {STEP * STEP, 2 * STEP * STEP}
    bad = []
    for (x1, y1), (x2, y2) in zip(path, path[1:]):
        d2 = (x2 - x1) ** 2 + (y2 - y1) ** 2
        if d2 not in allowed:
            bad.append(((x1, y1), (x2, y2), d2))
    return bad
