"""Część eksperymentalna: ewolucja AG dla wybranych zbiorów danych.

Dla każdego zbioru tworzone są osobne wykresy (najlepszy osobnik po każdej
iteracji, uśrednione po RUNS niezależnych uruchomieniach):
  1. różne prawdopodobieństwa mutacji,
  2. różne prawdopodobieństwa krzyżowania,
  3. selekcja ruletkowa vs rankingowa vs turniejowa,
  4. krzyżowanie jednopunktowe vs dwupunktowe,
  5. (dodatkowo) selekcje bez naprawy chromosomów.
Wyniki liczbowe zapisywane są w results/summary.json i results/summary.csv.

Uruchomienie:  .venv/bin/python experiments.py
"""
import csv
import json
import time
from dataclasses import replace
from pathlib import Path

from knapsack_ga import (GAConfig, GeneticAlgorithm, bit_flip_mutation, knapsack_fitness,
                         load_optimum, load_problem, one_point_crossover, random_repair,
                         rank_selection, roulette_selection, two_point_crossover)
from knapsack_ga.selection import make_tournament_selection
from plots import plot_series

DATA_DIR = Path("dane AG")
RESULTS_DIR = Path("results")
RUNS = 10  # liczba niezależnych uruchomień uśrednianych dla każdej serii

# (katalog z danymi, katalog z optimum, nazwa pliku)
DATASETS = [
    ("low-dimensional", "low-dimensional-optimum", "f2_l-d_kp_20_878"),
    ("low-dimensional", "low-dimensional-optimum", "f5_l-d_kp_15_375"),
    ("low-dimensional", "low-dimensional-optimum", "f8_l-d_kp_23_10000"),
    ("low-dimensional", "low-dimensional-optimum", "f10_l-d_kp_20_879"),
    ("large_scale", "large_scale-optimum", "knapPI_1_100_1000_1"),
    ("large_scale", "large_scale-optimum", "knapPI_1_200_1000_1"),
]

SELECTIONS = {
    "ruletkowa": roulette_selection,
    "rankingowa": rank_selection,
    "turniejowa (k=3)": make_tournament_selection(3),
}
CROSSOVERS = {
    "jednopunktowe": one_point_crossover,
    "dwupunktowe": two_point_crossover,
}
MUTATION_RATES = [0.001, 0.005, 0.01, 0.05, 0.1]
CROSSOVER_RATES = [0.5, 0.7, 0.9, 1.0]


def base_config(problem) -> GAConfig:
    """Konfiguracja bazowa; w każdym eksperymencie zmieniany jest jeden parametr."""
    large = problem.size > 50
    return GAConfig(
        population_size=100 if large else 30,
        iterations=500 if large else 100,
        fitness_fn=knapsack_fitness,
        selection_fn=roulette_selection,
        crossover_fn=one_point_crossover,
        mutation_fn=bit_flip_mutation,
        p_crossover=0.8,
        p_mutation=0.005 if large else 0.05,
        elitism=1,
        repair_fn=random_repair,
    )


def run_series(problem, config):
    """Uruchamia AG RUNS razy (różne ziarna) i zwraca uśrednioną historię oraz statystyki."""
    histories, finals, times = [], [], []
    for run in range(RUNS):
        start = time.perf_counter()
        result = GeneticAlgorithm(problem, replace(config, seed=1000 + run)).run()
        times.append(time.perf_counter() - start)
        assert result.best_fitness == 0 or problem.is_feasible(result.best_chromosome)
        histories.append(result.history_best)
        finals.append(result.best_fitness)
    mean_history = [sum(values) / RUNS for values in zip(*histories)]
    return mean_history, {
        "best": max(finals),
        "mean": sum(finals) / RUNS,
        "worst": min(finals),
        "time_s": sum(times) / RUNS,
        "finals": finals,
    }


def experiments_for(problem):
    """Zwraca listę eksperymentów: (id, tytuł, {etykieta serii: konfiguracja})."""
    base = base_config(problem)
    exps = [
        ("mutacja", f"Wpływ prawdopodobieństwa mutacji (p_k = {base.p_crossover})",
         {f"p_m = {p}": replace(base, p_mutation=p) for p in MUTATION_RATES}),
        ("krzyzowanie", f"Wpływ prawdopodobieństwa krzyżowania (p_m = {base.p_mutation})",
         {f"p_k = {p}": replace(base, p_crossover=p) for p in CROSSOVER_RATES}),
        ("selekcja", "Porównanie metod selekcji",
         {name: replace(base, selection_fn=fn) for name, fn in SELECTIONS.items()}),
        ("typ_krzyzowania", "Krzyżowanie jednopunktowe vs dwupunktowe",
         {name: replace(base, crossover_fn=fn) for name, fn in CROSSOVERS.items()}),
    ]
    if problem.size > 50:
        exps.append(("selekcja_bez_naprawy", "Metody selekcji bez naprawy chromosomów",
                     {name: replace(base, selection_fn=fn, repair_fn=None)
                      for name, fn in SELECTIONS.items()}))
    return exps


def main():
    RESULTS_DIR.mkdir(exist_ok=True)
    summary = []
    for data_dir, opt_dir, name in DATASETS:
        problem = load_problem(DATA_DIR / data_dir / name)
        optimum = load_optimum(DATA_DIR / opt_dir / name)
        base = base_config(problem)
        print(f"\n=== {name}: n={problem.size}, C={problem.capacity}, optimum={optimum} ===")
        dataset_entry = {
            "dataset": name, "group": data_dir, "n": problem.size,
            "capacity": problem.capacity, "optimum": optimum,
            "population_size": base.population_size, "iterations": base.iterations,
            "p_crossover": base.p_crossover, "p_mutation": base.p_mutation,
            "experiments": [],
        }
        for exp_id, title, configs in experiments_for(problem):
            series, stats = {}, {}
            for label, cfg in configs.items():
                series[label], stats[label] = run_series(problem, cfg)
                s = stats[label]
                print(f"  [{exp_id}] {label:<18} best={s['best']:<10g} mean={s['mean']:<10.1f} "
                      f"({100 * s['mean'] / optimum:5.1f}% opt), {s['time_s']:.2f}s/run")
            png = RESULTS_DIR / name / f"{exp_id}.png"
            plot_series(series, optimum,
                        f"{name} (n={problem.size}) – {title}\nśrednia z {RUNS} uruchomień", png)
            dataset_entry["experiments"].append(
                {"id": exp_id, "title": title, "plot": str(png), "stats": stats})
        summary.append(dataset_entry)

    (RESULTS_DIR / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    with open(RESULTS_DIR / "summary.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["zbior", "optimum", "eksperyment", "seria", "najlepszy", "sredni",
                         "najgorszy", "sredni_%_optimum", "czas_s"])
        for d in summary:
            for e in d["experiments"]:
                for label, s in e["stats"].items():
                    writer.writerow([d["dataset"], d["optimum"], e["id"], label, s["best"],
                                     round(s["mean"], 2), s["worst"],
                                     round(100 * s["mean"] / d["optimum"], 2), round(s["time_s"], 3)])
    print(f"\nWyniki zapisano w {RESULTS_DIR}/")


if __name__ == "__main__":
    main()
