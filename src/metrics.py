from __future__ import annotations

from typing import List, Tuple

Coord = Tuple[int, int]


def wall_ratio(grid: List[List[int]]) -> float:
    n = len(grid)
    total = n * n
    walls = sum(1 for r in range(n) for c in range(n) if grid[r][c] == 1)
    return walls / total


def degree_4(grid: List[List[int]], cell: Coord) -> int:
    r, c = cell
    n = len(grid)
    deg = 0
    for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        rr, cc = r + dr, c + dc
        if 0 <= rr < n and 0 <= cc < n and grid[rr][cc] == 0:
            deg += 1
    return deg


def count_dead_ends(grid: List[List[int]], start: Coord, goal: Coord) -> int:
    n = len(grid)
    d = 0
    for r in range(n):
        for c in range(n):
            if grid[r][c] != 0:
                continue
            cell = (r, c)
            if cell == start or cell == goal:
                continue
            if degree_4(grid, cell) == 1:
                d += 1
    return d


def count_junctions(grid: List[List[int]], start: Coord, goal: Coord) -> int:
    n = len(grid)
    j = 0
    for r in range(n):
        for c in range(n):
            if grid[r][c] != 0:
                continue
            cell = (r, c)
            if cell == start or cell == goal:
                continue
            if degree_4(grid, cell) >= 3:
                j += 1
    return j
