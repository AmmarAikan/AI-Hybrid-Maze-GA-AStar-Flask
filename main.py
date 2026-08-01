from __future__ import annotations

import argparse
import os
import csv

from src.ga import GeneticAlgorithm
from src.astar import AStarSolver
from src.visualize import plot_maze, plot_history, save_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Hybrid Project: GA evolves maze parameters + A* solves the maze.")
    parser.add_argument("--size", type=int, default=31, help="Odd maze size (e.g., 21, 25, 31...)")
    parser.add_argument("--pop", type=int, default=40, help="Population size")
    parser.add_argument("--gens", type=int, default=50, help="Number of generations")
    parser.add_argument("--seed", type=int, default=1234, help="GA RNG seed")
    parser.add_argument("--out", type=str, default="outputs", help="Output folder")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)

    ga = GeneticAlgorithm(
        size=args.size,
        population_size=args.pop,
        generations=args.gens,
        seed=args.seed,
    )

    best_ind, best_maze, history = ga.run()

    # Solve best maze again to get the path for visualization
    solver = AStarSolver()
    res = solver.solve(best_maze.grid, best_maze.start, best_maze.goal)

    # Save outputs
    plot_maze(best_maze.grid, None, os.path.join(args.out, "best_maze.png"), title="Best Maze (walls/free)", start=best_maze.start, goal=best_maze.goal)
    plot_maze(best_maze.grid, res.path, os.path.join(args.out, "best_maze_solution.png"), title="Best Maze + A* Path", start=best_maze.start, goal=best_maze.goal)
    plot_history(history, os.path.join(args.out, "fitness_curve.png"))

    save_json(best_ind.genome.__dict__, os.path.join(args.out, "best_genome.json"))
    save_json(best_ind.stats, os.path.join(args.out, "best_stats.json"))
    save_json(history, os.path.join(args.out, "history.json"))

    # Also save a CSV (useful for report graphs)
    with open(os.path.join(args.out, "history.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=history[0].keys())
        writer.writeheader()
        writer.writerows(history)

    print("=== DONE ===")
    print("Best fitness:", best_ind.fitness)
    print("Best genome:", best_ind.genome)
    print("Best stats:", best_ind.stats)
    print(f"Outputs saved to: {args.out}/")


if __name__ == "__main__":
    main()
