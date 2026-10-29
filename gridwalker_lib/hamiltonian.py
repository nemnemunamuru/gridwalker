from typing import List, Tuple
import time
from .grid import build_grid
from .constants import STEP


def hamiltonian_with_seed(x_limit: int, y_limit: int, timeout_sec: float, start: Tuple[int, int], seed_path: List[Tuple[int, int]], logger=None):
    xs, ys, points, S = build_grid(x_limit, y_limit)
    N = len(points)

    offsets = [
        ( STEP, 0), (-STEP, 0), (0,  STEP), (0, -STEP),
        ( STEP,  STEP), ( STEP, -STEP), (-STEP,  STEP), (-STEP, -STEP)
    ]
    neighbors = {}
    for x, y in points:
        nbrs = []
        for dx, dy in offsets:
            nx, ny = x + dx, y + dy
            if (nx, ny) in S:
                nbrs.append((nx, ny))
        neighbors[(x, y)] = nbrs

    visited = set(seed_path)
    path = list(seed_path)
    start_time = time.perf_counter()
    remaining = N - len(seed_path)

    if x_limit > y_limit: long_axis = 'x'
    elif y_limit > x_limit: long_axis = 'y'
    else: long_axis = None

    nodes = 0
    backtracks = 0
    max_cand = 0
    timed_out = False

    def time_exceeded():
        nonlocal timed_out
        if (time.perf_counter() - start_time) > timeout_sec:
            timed_out = True
            return True
        return False

    def onward_degree(v):
        return sum(1 for w in neighbors[v] if w not in visited)

    def wing_bias(v):
        if long_axis == 'x': return abs(v[0])
        if long_axis == 'y': return abs(v[1])
        return 0

    def dfs_from(u, rem):
        nonlocal nodes, backtracks, max_cand
        if time_exceeded():
            return False
        if rem == 0:
            return True
        nodes += 1
        cand = [v for v in neighbors[u] if v not in visited]
        max_cand = max(max_cand, len(cand))
        cand.sort(key=lambda v: (onward_degree(v), -wing_bias(v)))

        if logger and nodes % 1000 == 0:
            logger.info(f"[dfs] nodes={nodes}, rem={rem}, max_cand={max_cand}")

        for v in cand:
            visited.add(v); path.append(v)
            if dfs_from(v, rem - 1):
                return True
            visited.remove(v); path.pop()
            backtracks += 1
        return False

    if logger:
        logger.section("Hamiltonian search")
        logger.info(f"start={start}, seed_len={len(seed_path)}, total_points={N}, timeout={timeout_sec}s")

    ok = dfs_from(start, remaining)

    if logger:
        elapsed = time.perf_counter() - start_time
        logger.info(f"done: ok={ok}, nodes={nodes}, backtracks={backtracks}, max_cand={max_cand}, "
                    f"elapsed={elapsed:.3f}s, timeout_hit={timed_out}")

    return path if ok else None
