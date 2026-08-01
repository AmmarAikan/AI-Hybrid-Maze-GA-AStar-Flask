from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple
import random


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


@dataclass(frozen=True)
class Genome:
    """
    Parameters that control maze generation (Hybrid project):
    - corridor_bias: prefer continuing straight while carving the maze (0..1)
    - goal_bias: prefer carving in the direction of the goal (0..1) -> usually makes it easier
    - loopiness: fraction of extra walls to remove after generating a perfect maze (0..0.25)
    - seed: RNG seed used to generate deterministic mazes for this genome
    """
    corridor_bias: float
    goal_bias: float
    loopiness: float
    seed: int

    @staticmethod
    def random(rng: random.Random) -> "Genome":
        return Genome(
            corridor_bias=rng.random(),
            goal_bias=rng.random(),
            loopiness=rng.random() * 0.25,
            seed=rng.randrange(0, 2**32 - 1),
        )

    def mutate(self, rng: random.Random,
               p_gene: float = 0.25,
               sigma: float = 0.15) -> "Genome":
        """
        Mutate each gene with probability p_gene.
        Float genes: add gaussian noise then clamp.
        Seed: either random reset or small random delta.
        """
        cb = self.corridor_bias
        gb = self.goal_bias
        lp = self.loopiness
        sd = self.seed

        if rng.random() < p_gene:
            cb = clamp(cb + rng.gauss(0.0, sigma), 0.0, 1.0)
        if rng.random() < p_gene:
            gb = clamp(gb + rng.gauss(0.0, sigma), 0.0, 1.0)
        if rng.random() < p_gene:
            lp = clamp(lp + rng.gauss(0.0, sigma * 0.5), 0.0, 0.25)

        if rng.random() < p_gene:
            # Sometimes reset seed entirely, otherwise small delta
            if rng.random() < 0.5:
                sd = rng.randrange(0, 2**32 - 1)
            else:
                sd = (sd + rng.randrange(-50000, 50001)) % (2**32 - 1)

        return Genome(cb, gb, lp, sd)


def crossover(a: Genome, b: Genome, rng: random.Random) -> Genome:
    """
    Uniform crossover: for each gene choose from parent a or b.
    """
    return Genome(
        corridor_bias=a.corridor_bias if rng.random() < 0.5 else b.corridor_bias,
        goal_bias=a.goal_bias if rng.random() < 0.5 else b.goal_bias,
        loopiness=a.loopiness if rng.random() < 0.5 else b.loopiness,
        seed=a.seed if rng.random() < 0.5 else b.seed,
    )
