# Algorytm genetyczny – problem plecakowy 0/1

Implementacja algorytmu genetycznego (czysty Python, bez bibliotek GA) dla dyskretnego
problemu plecakowego, wraz z eksperymentami i sprawozdaniem (zakres na ocenę 5.0).

## Struktura
| Plik | Zawartość |
|---|---|
| `knapsack_ga/problem.py` | `KnapsackProblem`, import danych `load_problem()`, `load_optimum()` |
| `knapsack_ga/fitness.py` | funkcja przystosowania (wartość lub 0 przy przekroczeniu pojemności) |
| `knapsack_ga/selection.py` | selekcja ruletkowa, rankingowa, turniejowa |
| `knapsack_ga/crossover.py` | krzyżowanie jedno- i dwupunktowe |
| `knapsack_ga/mutation.py` | mutacja bit-flip |
| `knapsack_ga/repair.py` | losowa naprawa chromosomów przekraczających pojemność |
| `knapsack_ga/ga.py` | `GAConfig` + ogólny `GeneticAlgorithm` (operatory jako parametry) |
| `experiments.py` | wszystkie eksperymenty → `results/` (wykresy PNG, summary.json/csv) |
| `plots.py` | wykresy (jedyne miejsce z matplotlib) |
| `make_report.py` | generuje `Sprawozdanie.docx` |

## Uruchomienie
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python experiments.py   # ok. 4 min
.venv/bin/python make_report.py
```

## Przykład użycia
```python
from knapsack_ga import *
problem = load_problem("dane AG/low-dimensional/f1_l-d_kp_10_269")
config = GAConfig(population_size=50, iterations=100,
                  selection_fn=rank_selection, crossover_fn=two_point_crossover,
                  p_crossover=0.8, p_mutation=0.05, repair_fn=random_repair, seed=1)
result = GeneticAlgorithm(problem, config).run()
print(result.best_fitness, problem.selected_items(result.best_chromosome))
```
