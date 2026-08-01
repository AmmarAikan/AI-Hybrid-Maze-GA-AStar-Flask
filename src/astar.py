from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import heapq
import time


Coord = Tuple[int, int]


def manhattan(a: Coord, b: Coord) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


@dataclass
class AStarResult:
    path: Optional[List[Coord]]
    expanded_nodes: int
    runtime_ms: float


class AStarSolver:
    """
    Classic A* pathfinding on a grid.
    Grid convention:
        0 = free cell
        1 = wall
    """

    def __init__(self, allow_diagonal: bool = False):
        self.allow_diagonal = allow_diagonal

    def _neighbors(self, grid: List[List[int]], node: Coord) -> List[Coord]:
        r, c = node
        moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        if self.allow_diagonal:
            moves += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        out: List[Coord] = []
        n = len(grid)
        for dr, dc in moves:
            rr, cc = r + dr, c + dc
            if 0 <= rr < n and 0 <= cc < n and grid[rr][cc] == 0:
                out.append((rr, cc))
        return out

    def solve(self, grid: List[List[int]], start: Coord, goal: Coord) -> AStarResult:
        t0 = time.perf_counter()

        # Min-heap of (f, tie_breaker, node)
        open_heap: List[Tuple[int, int, Coord]] = []
        heapq.heappush(open_heap, (manhattan(start, goal), 0, start))

        came_from: Dict[Coord, Coord] = {}
        g_score: Dict[Coord, int] = {start: 0}
        closed: set[Coord] = set()

        expanded = 0
        tie = 0

        while open_heap:
            _, _, current = heapq.heappop(open_heap)

            if current in closed:
                continue

            expanded += 1

            if current == goal:
                path = self._reconstruct_path(came_from, current)
                t1 = time.perf_counter()
                return AStarResult(path=path, expanded_nodes=expanded, runtime_ms=(t1 - t0) * 1000.0)

            closed.add(current)

            for nb in self._neighbors(grid, current):
                if nb in closed:
                    continue

                tentative_g = g_score[current] + 1
                if tentative_g < g_score.get(nb, 10**9):
                    came_from[nb] = current
                    g_score[nb] = tentative_g
                    f = tentative_g + manhattan(nb, goal)
                    tie += 1
                    heapq.heappush(open_heap, (f, tie, nb))

        t1 = time.perf_counter()
        return AStarResult(path=None, expanded_nodes=expanded, runtime_ms=(t1 - t0) * 1000.0)

    @staticmethod
    def _reconstruct_path(came_from: Dict[Coord, Coord], current: Coord) -> List[Coord]:
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path
