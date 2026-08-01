from __future__ import annotations

from typing import List, Optional, Tuple, Dict, Any
import json
import os

# Ensure a non-interactive backend (important for servers / Flask)
import matplotlib
if os.environ.get("MPLBACKEND") is None:
    matplotlib.use("Agg")  # safe default for headless environments

import matplotlib.pyplot as plt

Coord = Tuple[int, int]


def plot_maze(
    grid: List[List[int]],
    path: Optional[List[Coord]],
    out_path: str,
    title: str = "",
    start: Optional[Coord] = None,
    goal: Optional[Coord] = None,
) -> None:
    """
    Save a maze image (optionally with the solution path).
    Grid convention:
        0 = free
        1 = wall
    """
    import numpy as np

    arr = np.array(grid, dtype=int)

    plt.figure(figsize=(6, 6))
    plt.imshow(arr, cmap="gray", interpolation="nearest")  # 1=wall (dark), 0=free (light)

    if path:
        ys = [p[0] for p in path]
        xs = [p[1] for p in path]
        plt.plot(xs, ys, linewidth=2, label="A* Path")

    # Optional markers
    if start is not None:
        plt.scatter([start[1]], [start[0]], s=60, marker="o", label="Start")
    if goal is not None:
        plt.scatter([goal[1]], [goal[0]], s=60, marker="X", label="Goal")

    plt.xticks([])
    plt.yticks([])
    if title:
        plt.title(title)

    # Only show legend if we actually plotted something besides the maze
    if path or start is not None or goal is not None:
        plt.legend(loc="upper right", fontsize=8, frameon=True)

    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()


def plot_history(history: List[Dict[str, Any]], out_path: str) -> None:
    gens = [h["generation"] for h in history]
    best = [h["best_fitness"] for h in history]
    avg = [h["avg_fitness"] for h in history]

    plt.figure(figsize=(7, 4))
    plt.plot(gens, best, label="Best fitness")
    plt.plot(gens, avg, label="Average fitness")
    plt.xlabel("Generation")
    plt.ylabel("Fitness")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()


def save_json(obj: Any, out_path: str) -> None:
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
