from typing import List, Tuple, Optional
from .constants import STEP


def spiral_seed_square(spiral_half: int, start_dir: int = 0, clockwise: bool = True) -> List[Tuple[int, int]]:
    if spiral_half <= 0:
        return [(0, 0)]

    xs = list(range(-spiral_half, spiral_half + 1, STEP))
    ys = list(range(-spiral_half, spiral_half + 1, STEP))
    target = set((x, y) for x in xs for y in ys)

    if clockwise:
        base = [(STEP, 0), (0, STEP), (-STEP, 0), (0, -STEP)]
    else:
        base = [(0, STEP), (STEP, 0), (0, -STEP), (-STEP, 0)]

    dirs = base[start_dir:] + base[:start_dir]

    path = [(0, 0)]
    visited_target = {(0, 0)} if (0, 0) in target else set()
    cur = (0, 0)
    seg_len = 1

    while len(visited_target) < len(target):
        for i in range(4):
            dx, dy = dirs[i]
            for _ in range(seg_len):
                cur = (cur[0] + dx, cur[1] + dy)
                path.append(cur)
                if cur in target:
                    visited_target.add(cur)
                if len(visited_target) >= len(target):
                    break
            if len(visited_target) >= len(target):
                break
            if i % 2 == 1:
                seg_len += 1
    return path


def choose_best_spiral_seed(spiral_half: int, x_limit: int, y_limit: int, logger=None) -> List[Tuple[int, int]]:
    if spiral_half <= 0:
        return [(0, 0)]

    if x_limit > y_limit:
        long_axis = 'x'
    elif y_limit > x_limit:
        long_axis = 'y'
    else:
        long_axis = 'x'

    best_seed = None
    best_score = -1
    if logger:
        logger.section("Spiral orientation scoring")
        logger.info(f"long_axis={long_axis}, spiral_half={spiral_half}")

    for cw in (True, False):
        for start_dir in range(4):
            seed = spiral_seed_square(spiral_half, start_dir=start_dir, clockwise=cw)
            ex, ey = seed[-1]
            score = abs(ex) if long_axis == 'x' else abs(ey)
            if logger:
                logger.info(f"try seed cw={cw}, start_dir={start_dir}, end=({ex},{ey}), score={score}")
            if score > best_score:
                best_score = score
                best_seed = seed

    if logger:
        ex, ey = best_seed[-1]
        logger.info(f"SELECTED seed end=({ex},{ey}), best_score={best_score}")
    return best_seed
