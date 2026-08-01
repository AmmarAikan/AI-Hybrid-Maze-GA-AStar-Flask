from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Dict, Any, Optional, Callable
import random
import statistics

from .genome import Genome, crossover
from .maze_generator import MazeGenerator, Maze
from .astar import AStarSolver
from .metrics import wall_ratio, count_dead_ends, count_junctions

Coord = Tuple[int, int]


@dataclass
class Individual:
    genome: Genome
    fitness: float
    stats: Dict[str, Any]


class GeneticAlgorithm:
    def __init__(
        self,
        size: int,
        population_size: int = 40,
        generations: int = 50,
        tournament_k: int = 3,
        elite: int = 2,
        p_mut_gene: float = 0.25,
        seed: int = 1234,
        allow_diagonal: bool = False,
    ):
        self.size = size
        self.population_size = population_size
        self.generations = generations
        self.tournament_k = tournament_k
        self.elite = elite
        self.p_mut_gene = p_mut_gene
        self.rng = random.Random(seed)

        self.generator = MazeGenerator(size=size)
        self.solver = AStarSolver(allow_diagonal=allow_diagonal)

    def run(
        self,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> Tuple[Individual, Maze, List[Dict[str, Any]]]:
        pop = [Genome.random(self.rng) for _ in range(self.population_size)]
        history: List[Dict[str, Any]] = []

        best_overall: Optional[Individual] = None
        best_overall_maze: Optional[Maze] = None

        for gen in range(self.generations):
            evaluated: List[Tuple[Individual, Maze]] = []
            for g in pop:
                maze = self.generator.generate(g)
                ind = self._evaluate(g, maze)
                evaluated.append((ind, maze))

            evaluated.sort(key=lambda x: x[0].fitness, reverse=True)

            best_ind, best_maze = evaluated[0]
            avg_fit = statistics.mean(ind.fitness for ind, _ in evaluated)

            snapshot = {
                "generation": gen,
                "best_fitness": best_ind.fitness,
                "avg_fitness": avg_fit,
                **{f"best_{k}": v for k, v in best_ind.stats.items()},
            }
            history.append(snapshot)

            if progress_callback is not None:
                try:
                    progress_callback(snapshot)
                except Exception:
                    # Progress callback should never break the algorithm
                    pass

            if best_overall is None or best_ind.fitness > best_overall.fitness:
                best_overall = best_ind
                best_overall_maze = best_maze

            # --- Create next generation
            next_pop: List[Genome] = []

            # Elitism
            elites = [ind.genome for ind, _ in evaluated[: self.elite]]
            next_pop.extend(elites)

            while len(next_pop) < self.population_size:
                p1 = self._tournament([ind for ind, _ in evaluated])
                p2 = self._tournament([ind for ind, _ in evaluated])
                child = crossover(p1.genome, p2.genome, self.rng)
                child = child.mutate(self.rng, p_gene=self.p_mut_gene)
                next_pop.append(child)

            pop = next_pop

        assert best_overall is not None and best_overall_maze is not None
        return best_overall, best_overall_maze, history

    def _tournament(self, inds: List[Individual]) -> Individual:
        contestants = self.rng.sample(inds, k=self.tournament_k)
        contestants.sort(key=lambda x: x.fitness, reverse=True)
        return contestants[0]

    def _evaluate(self, genome: Genome, maze: Maze) -> Individual:
        res = self.solver.solve(maze.grid, maze.start, maze.goal)

        if res.path is None:
            fitness = -1e9
            stats = {
                "path_len": None,
                "expanded": res.expanded_nodes,
                "dead_ends": None,
                "junctions": None,
                "wall_ratio": wall_ratio(maze.grid),
                "runtime_ms": res.runtime_ms,
            }
            return Individual(genome=genome, fitness=fitness, stats=stats)

        path_len = len(res.path) - 1
        dead_ends = count_dead_ends(maze.grid, maze.start, maze.goal)
        junctions = count_junctions(maze.grid, maze.start, maze.goal)
        wr = wall_ratio(maze.grid)

        # ---- Fitness (tuneable)
        n = len(maze.grid)
        area = n * n
        L = path_len / area
        E = res.expanded_nodes / area
        D = dead_ends / area

        target_wr = 0.60
        penalty = abs(wr - target_wr)

        fitness = 100.0 * (0.45 * L + 0.45 * E + 0.20 * D - 0.30 * penalty)

        stats = {
            "path_len": path_len,
            "expanded": res.expanded_nodes,
            "dead_ends": dead_ends,
            "junctions": junctions,
            "wall_ratio": wr,
            "runtime_ms": res.runtime_ms,
        }

        return Individual(genome=genome, fitness=fitness, stats=stats)
