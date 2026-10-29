from matplotlib.patches import FancyArrowPatch
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
from .constants import DIAG_COLOR, ORTH_COLOR


def draw_base_points(ax, S, x_limit, y_limit):
    all_x = [x for x, _ in S]
    all_y = [y for _, y in S]
    ax.scatter(all_x, all_y, s=18, c="black", label="Grid points", zorder=2)
    xmin, xmax = -x_limit, x_limit
    ymin, ymax = -y_limit, y_limit
    ax.axvline(xmin, color="#888", lw=0.8, zorder=1)
    ax.axvline(xmax, color="#888", lw=0.8, zorder=1)
    ax.axhline(ymin, color="#888", lw=0.8, zorder=1)
    ax.axhline(ymax, color="#888", lw=0.8, zorder=1)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, which="both", linewidth=0.5, alpha=0.3, zorder=0)


def plot_path_with_arrows(fig, ax, S, path, x_limit, y_limit, title):
    ax.clear()
    draw_base_points(ax, S, x_limit, y_limit)

    for (x1, y1), (x2, y2) in zip(path, path[1:]):
        dx, dy = (x2 - x1), (y2 - y1)
        t0, t1 = 0.1, 0.9
        sx, sy = x1 + dx * t0, y1 + dy * t0
        ex, ey = x1 + dx * t1, y1 + dy * t1
        color = DIAG_COLOR if (dx != 0 and dy != 0) else ORTH_COLOR
        arrow = FancyArrowPatch(
            (sx, sy), (ex, ey),
            arrowstyle='-|>', mutation_scale=12,
            linewidth=1.8, color=color, zorder=4
        )
        ax.add_patch(arrow)

    if path:
        sx, sy = path[0]
        ex, ey = path[-1]
        ax.scatter([sx], [sy], s=90, marker="s", c="#2ca02c",
                   edgecolor="white", linewidths=1.2, zorder=5, label="Start")
        ax.annotate(
            "START", (sx, sy), textcoords="offset points", xytext=(8, 8),
            color="#2ca02c", fontsize=10, fontweight="bold", zorder=6,
            path_effects=[pe.withStroke(linewidth=2.5, foreground="white")]
        )
        ax.scatter([ex], [ey], s=90, marker="D", c="#ff7f0e",
                   edgecolor="white", linewidths=1.2, zorder=5, label="End")
        ax.annotate(
            "END", (ex, ey), textcoords="offset points", xytext=(8, -14),
            color="#ff7f0e", fontsize=10, fontweight="bold", zorder=6,
            path_effects=[pe.withStroke(linewidth=2.5, foreground="white")]
        )

    ax.set_title(title)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.legend(loc="upper right")
    fig.tight_layout()
