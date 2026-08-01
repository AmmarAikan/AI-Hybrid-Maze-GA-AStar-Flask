from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Optional
import random
import math

from .genome import Genome

Coord = Tuple[int, int]


@dataclass
class Maze:
    grid: List[List[int]]  # 0 free, 1 wall
    start: Coord
    goal: Coord


class MazeGenerator:
    """
    Generate a maze (perfect maze) using DFS carving on a grid (odd size recommended),
    then optionally remove extra walls to add loops (controlled by genome.loopiness).

    This makes the project a Hybrid:
        GA evolves (corridor_bias, goal_bias, loopiness, seed) -> controls the maze generator
        A* solves the generated maze and provides metrics for fitness.
    """

    def __init__(self, size: int):
        if size < 7:
            raise ValueError("Maze size must be >= 7")
        if size % 2 == 0:
            raise ValueError("Maze size must be odd (e.g., 21, 25, 31...)")
        self.size = size

    def generate(self, genome: Genome) -> Maze:
        rng = random.Random(genome.seed)

        n = self.size
        grid = [[1 for _ in range(n)] for _ in range(n)]

        start = (1, 1)
        goal = (n - 2, n - 2)

        # Carve cells at odd coordinates
        stack: List[Tuple[Coord, Optional[Coord]]] = [(start, None)]
        visited = {start}
        grid[start[0]][start[1]] = 0

        def neighbors(cell: Coord) -> List[Tuple[Coord, Coord]]:
            r, c = cell
            dirs = [(-2, 0), (2, 0), (0, -2), (0, 2)]
            out: List[Tuple[Coord, Coord]] = []
            for dr, dc in dirs:
                rr, cc = r + dr, c + dc
                if 1 <= rr < n - 1 and 1 <= cc < n - 1:
                    nb = (rr, cc)
                    if nb not in visited:
                        out.append((nb, (dr, dc)))
            return out

        def dist_to_goal(cell: Coord) -> int:
            return abs(cell[0] - goal[0]) + abs(cell[1] - goal[1])

        while stack:
            cell, prev_dir = stack[-1]
            cands = neighbors(cell)

            if not cands:
                stack.pop()
                continue

            # Weighted choice among candidates
            weights: List[float] = []
            for nb, d in cands:
                w = 1.0

                # Prefer continuing straight
                if prev_dir is not None and d == prev_dir:
                    w *= 1.0 + 3.0 * genome.corridor_bias

                # Prefer moving "toward" the goal (usually makes mazes easier)
                if dist_to_goal(nb) < dist_to_goal(cell):
                    w *= 1.0 + 2.0 * genome.goal_bias
                else:
                    w *= 1.0 + 0.25 * (1.0 - genome.goal_bias)

                weights.append(w)

            nb, d = rng.choices(cands, weights=weights, k=1)[0]

            # Carve wall between cell and nb
            wall = (cell[0] + d[0] // 2, cell[1] + d[1] // 2)
            grid[wall[0]][wall[1]] = 0
            grid[nb[0]][nb[1]] = 0

            visited.add(nb)
            stack.append((nb, d))

        # Ensure goal is open (it should be in a perfect maze)
        grid[goal[0]][goal[1]] = 0

        # Add loops by removing random "candidate walls"
        self._add_loops(grid, genome, rng)

        return Maze(grid=grid, start=start, goal=goal)

    def _add_loops(self, grid: List[List[int]], genome: Genome, rng: random.Random) -> None:
        n = self.size

        candidates: List[Coord] = []
        for r in range(1, n - 1):
            for c in range(1, n - 1):
                if grid[r][c] != 1:
                    continue

                # Wall between left/right open cells
                if r % 2 == 1 and c % 2 == 0:
                    if grid[r][c - 1] == 0 and grid[r][c + 1] == 0:
                        candidates.append((r, c))

                # Wall between up/down open cells
                if r % 2 == 0 and c % 2 == 1:
                    if grid[r - 1][c] == 0 and grid[r + 1][c] == 0:
                        candidates.append((r, c))

        if not candidates:
            return

        k = int(round(genome.loopiness * len(candidates)))
        k = max(0, min(k, len(candidates)))
        if k == 0:
            return

        for (r, c) in rng.sample(candidates, k=k):
            grid[r][c] = 0
