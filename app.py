from __future__ import annotations

import os
import csv
import secrets
import time
import uuid
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Important for servers / Flask (matplotlib without display)
os.environ.setdefault("MPLBACKEND", "Agg")

from flask import Flask, flash, redirect, render_template, request, send_from_directory, url_for

from src.astar import AStarSolver
from src.ga import GeneticAlgorithm
from src.genome import Genome, clamp
from src.maze_generator import MazeGenerator
from src.metrics import count_dead_ends, count_junctions, wall_ratio
from src.visualize import plot_history, plot_maze, save_json


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_ROOT = BASE_DIR / "web_outputs"
OUTPUT_ROOT.mkdir(exist_ok=True)


def _safe_run_id(prefix: str) -> str:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    token = uuid.uuid4().hex[:10]
    return f"{prefix}_{stamp}_{token}"


def _int(form: Dict[str, Any], key: str, default: int, lo: Optional[int] = None, hi: Optional[int] = None) -> int:
    try:
        v = int(str(form.get(key, default)).strip())
    except Exception:
        v = default
    if lo is not None:
        v = max(lo, v)
    if hi is not None:
        v = min(hi, v)
    return v


def _float(form: Dict[str, Any], key: str, default: float, lo: Optional[float] = None, hi: Optional[float] = None) -> float:
    try:
        v = float(str(form.get(key, default)).strip())
    except Exception:
        v = default
    if lo is not None:
        v = max(lo, v)
    if hi is not None:
        v = min(hi, v)
    return v


app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)


@app.get("/")
def index():
    defaults = {
        # GA defaults (balanced)
        "size": 31,
        "population_size": 40,
        "generations": 50,
        "seed": 1234,
        "tournament_k": 3,
        "elite": 2,
        "p_mut_gene": 0.25,
        "allow_diagonal": False,
        # Manual genome defaults
        "corridor_bias": 0.65,
        "goal_bias": 0.20,
        "loopiness": 0.08,
        "genome_seed": 1234,
    }
    return render_template("index.html", defaults=defaults)


@app.post("/run-ga")
def run_ga():
    form = request.form

    size = _int(form, "size", 31, lo=7, hi=151)
    if size % 2 == 0:
        size += 1  # enforce odd size

    pop = _int(form, "population_size", 40, lo=5, hi=500)
    gens = _int(form, "generations", 50, lo=1, hi=500)
    seed = _int(form, "seed", 1234, lo=0, hi=2**31 - 1)

    tournament_k = _int(form, "tournament_k", 3, lo=2, hi=20)
    elite = _int(form, "elite", 2, lo=0, hi=max(0, pop - 1))
    p_mut_gene = _float(form, "p_mut_gene", 0.25, lo=0.0, hi=1.0)

    allow_diagonal = bool(form.get("allow_diagonal"))

    # Basic sanity note
    if elite >= pop:
        elite = max(0, pop - 1)

    run_id = _safe_run_id("ga")
    out_dir = OUTPUT_ROOT / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()

    try:
        ga = GeneticAlgorithm(
            size=size,
            population_size=pop,
            generations=gens,
            tournament_k=tournament_k,
            elite=elite,
            p_mut_gene=p_mut_gene,
            seed=seed,
            allow_diagonal=allow_diagonal,
        )

        best_ind, best_maze, history = ga.run()

        # Solve best maze again (for path visualization)
        solver = AStarSolver(allow_diagonal=allow_diagonal)
        res = solver.solve(best_maze.grid, best_maze.start, best_maze.goal)

        # Save images
        plot_maze(
            best_maze.grid,
            None,
            str(out_dir / "best_maze.png"),
            title="Best Maze (walls/free)",
            start=best_maze.start,
            goal=best_maze.goal,
        )
        plot_maze(
            best_maze.grid,
            res.path,
            str(out_dir / "best_maze_solution.png"),
            title="Best Maze + A* Path",
            start=best_maze.start,
            goal=best_maze.goal,
        )
        plot_history(history, str(out_dir / "fitness_curve.png"))

        # Save JSON/CSV
        save_json(asdict(best_ind.genome), str(out_dir / "best_genome.json"))
        save_json(best_ind.stats, str(out_dir / "best_stats.json"))
        save_json(history, str(out_dir / "history.json"))
        with open(out_dir / "history.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=history[0].keys())
            writer.writeheader()
            writer.writerows(history)

        t1 = time.perf_counter()

        summary = {
            "run_id": run_id,
            "mode": "ga",
            "params": {
                "size": size,
                "population_size": pop,
                "generations": gens,
                "seed": seed,
                "tournament_k": tournament_k,
                "elite": elite,
                "p_mut_gene": p_mut_gene,
                "allow_diagonal": allow_diagonal,
            },
            "best": {
                "fitness": best_ind.fitness,
                "genome": asdict(best_ind.genome),
                "stats": best_ind.stats,
                "a_star": {
                    "path_found": res.path is not None,
                    "path_len": (len(res.path) - 1) if res.path else None,
                    "expanded_nodes": res.expanded_nodes,
                    "runtime_ms": res.runtime_ms,
                },
            },
            "runtime_sec": round(t1 - t0, 3),
            "outputs": [
                "best_maze.png",
                "best_maze_solution.png",
                "fitness_curve.png",
                "best_genome.json",
                "best_stats.json",
                "history.json",
                "history.csv",
            ],
        }
        save_json(summary, str(out_dir / "run_summary.json"))

        return render_template(
            "result.html",
            title="نتيجة تشغيل GA",
            run_id=run_id,
            mode="ga",
            summary=summary,
        )

    except Exception as e:
        # Clean the directory on failure to avoid confusion
        try:
            for p in out_dir.glob("*"):
                p.unlink(missing_ok=True)
            out_dir.rmdir()
        except Exception:
            pass

        flash(f"حدث خطأ أثناء التشغيل: {e}")
        return redirect(url_for("index"))


@app.post("/generate-one")
def generate_one():
    form = request.form

    size = _int(form, "size_single", 31, lo=7, hi=151)
    if size % 2 == 0:
        size += 1

    corridor_bias = _float(form, "corridor_bias", 0.65, lo=0.0, hi=1.0)
    goal_bias = _float(form, "goal_bias", 0.20, lo=0.0, hi=1.0)
    loopiness = _float(form, "loopiness", 0.08, lo=0.0, hi=0.25)
    seed = _int(form, "genome_seed", 1234, lo=0, hi=2**31 - 1)

    allow_diagonal = bool(form.get("allow_diagonal_single"))

    # Ensure clamped (extra safety)
    corridor_bias = clamp(corridor_bias, 0.0, 1.0)
    goal_bias = clamp(goal_bias, 0.0, 1.0)
    loopiness = clamp(loopiness, 0.0, 0.25)

    run_id = _safe_run_id("single")
    out_dir = OUTPUT_ROOT / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()

    try:
        genome = Genome(
            corridor_bias=corridor_bias,
            goal_bias=goal_bias,
            loopiness=loopiness,
            seed=seed,
        )

        generator = MazeGenerator(size=size)
        maze = generator.generate(genome)

        solver = AStarSolver(allow_diagonal=allow_diagonal)
        res = solver.solve(maze.grid, maze.start, maze.goal)

        # Metrics
        wr = wall_ratio(maze.grid)
        de = count_dead_ends(maze.grid, maze.start, maze.goal)
        jn = count_junctions(maze.grid, maze.start, maze.goal)

        plot_maze(
            maze.grid,
            None,
            str(out_dir / "maze.png"),
            title="Maze (manual genome)",
            start=maze.start,
            goal=maze.goal,
        )
        plot_maze(
            maze.grid,
            res.path,
            str(out_dir / "maze_solution.png"),
            title="Maze + A* Path (manual genome)",
            start=maze.start,
            goal=maze.goal,
        )

        t1 = time.perf_counter()

        summary = {
            "run_id": run_id,
            "mode": "single",
            "params": {
                "size": size,
                "allow_diagonal": allow_diagonal,
            },
            "genome": asdict(genome),
            "a_star": {
                "path_found": res.path is not None,
                "path_len": (len(res.path) - 1) if res.path else None,
                "expanded_nodes": res.expanded_nodes,
                "runtime_ms": res.runtime_ms,
            },
            "maze_metrics": {
                "wall_ratio": wr,
                "dead_ends": de,
                "junctions": jn,
            },
            "runtime_sec": round(t1 - t0, 3),
            "outputs": [
                "maze.png",
                "maze_solution.png",
                "run_summary.json",
            ],
        }
        save_json(summary, str(out_dir / "run_summary.json"))

        return render_template(
            "result.html",
            title="نتيجة توليد متاهة واحدة",
            run_id=run_id,
            mode="single",
            summary=summary,
        )

    except Exception as e:
        try:
            for p in out_dir.glob("*"):
                p.unlink(missing_ok=True)
            out_dir.rmdir()
        except Exception:
            pass

        flash(f"حدث خطأ أثناء التوليد: {e}")
        return redirect(url_for("index"))


@app.get("/outputs/<run_id>/<path:filename>")
def output_file(run_id: str, filename: str):
    # Simple safety: only allow run_id with expected chars
    if not all(ch.isalnum() or ch in {"_", "-"} for ch in run_id):
        flash("Run ID غير صالح.")
        return redirect(url_for("index"))

    run_dir = OUTPUT_ROOT / run_id
    if not run_dir.exists():
        flash("لا يوجد مخرجات لهذا الـ Run ID.")
        return redirect(url_for("index"))

    return send_from_directory(run_dir, filename)


if __name__ == "__main__":
    # Run: python app.py
    # ثم افتح: http://127.0.0.1:5000
    debug_enabled = os.environ.get("FLASK_DEBUG", "").lower() in {"1", "true", "yes"}
    app.run(host="127.0.0.1", port=5000, debug=debug_enabled)
