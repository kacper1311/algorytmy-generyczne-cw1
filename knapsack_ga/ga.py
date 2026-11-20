"""Ogólny szkielet algorytmu genetycznego.

Wszystkie operatory (funkcja przystosowania, selekcja, krzyżowanie, mutacja)
są przekazywane jako parametry, więc ten sam kod może rozwiązywać różne
problemy i być uruchamiany z różnymi wariantami operatorów.
"""
import random
from dataclasses import dataclass, field
from typing import Callable, Optional

from .crossover import one_point_crossover
from .fitness import knapsack_fitness
from .mutation import bit_flip_mutation
from .selection import roulette_selection


@dataclass
class GAConfig:
    """Parametry algorytmu genetycznego."""
    population_size: int = 100
    iterations: int = 200
    fitness_fn: Callable = knapsack_fitness
    selection_fn: Callable = roulette_selection
    crossover_fn: Callable = one_point_crossover
    mutation_fn: Callable = bit_flip_mutation
    p_crossover: float = 0.8
    p_mutation: float = 0.01
    elitism: int = 1          # ilu najlepszych osobników przechodzi bez zmian
    feasible_init: bool = True  # populacja początkowa złożona z rozwiązań dopuszczalnych
    repair_fn: Optional[Callable] = None  # opcjonalna naprawa potomków, np. random_repair
    seed: Optional[int] = None


@dataclass
class GAResult:
    """Wynik ewolucji."""
    best_chromosome: list
    best_fitness: float
    history_best: list = field(default_factory=list)  # najlepszy osobnik w każdej iteracji
    history_mean: list = field(default_factory=list)  # średnie przystosowanie populacji


class GeneticAlgorithm:
    """Algorytm genetyczny realizujący kroki:
    1. wybór populacji początkowej,
    2. ocena przystosowania osobników,
    3. wyprowadzenie najlepszego osobnika,
    4. sprawdzenie warunku zatrzymania,
    5. selekcja chromosomów,
    6. zastosowanie operatorów genetycznych,
    7. utworzenie nowej populacji.
    """

    def __init__(self, problem, config: GAConfig):
        self.problem = problem
        self.config = config
        self.rng = random.Random(config.seed)

    # ---------- 1. populacja początkowa ----------
    def _random_chromosome(self):
        return [self.rng.randint(0, 1) for _ in range(self.problem.size)]

    def _random_feasible_chromosome(self):
        """Dodaje przedmioty w losowej kolejności, dopóki mieszczą się w plecaku.
        Wylosowany chromosom jest więc zawsze rozwiązaniem dopuszczalnym."""
        chromosome = [0] * self.problem.size
        order = list(range(self.problem.size))
        self.rng.shuffle(order)
        free = self.problem.capacity
        for i in order:
            weight = self.problem.items[i].weight
            if weight <= free:
                chromosome[i] = 1
                free -= weight
        return chromosome

    def initial_population(self):
        make = self._random_feasible_chromosome if self.config.feasible_init else self._random_chromosome
        return [make() for _ in range(self.config.population_size)]

    # ---------- 2. ocena ----------
    def evaluate(self, population):
        return [self.config.fitness_fn(ch, self.problem) for ch in population]

    # ---------- 5-7. selekcja, operatory, nowa populacja ----------
    def next_generation(self, population, fitnesses):
        cfg = self.config
        rng = self.rng

        # elitaryzm - najlepsze osobniki przechodzą bez zmian
        elite_idx = sorted(range(len(population)), key=lambda i: fitnesses[i], reverse=True)[:cfg.elitism]
        new_population = [population[i][:] for i in elite_idx]

        parents = cfg.selection_fn(population, fitnesses, rng)
        rng.shuffle(parents)

        i = 0
        while len(new_population) < cfg.population_size:
            parent1 = parents[i % len(parents)]
            parent2 = parents[(i + 1) % len(parents)]
            i += 2
            if rng.random() < cfg.p_crossover:
                child1, child2 = cfg.crossover_fn(parent1, parent2, rng)
            else:
                child1, child2 = parent1[:], parent2[:]
            for child in (child1, child2):
                if len(new_population) < cfg.population_size:
                    child = cfg.mutation_fn(child, cfg.p_mutation, rng)
                    if cfg.repair_fn is not None:
                        child = cfg.repair_fn(child, self.problem, rng)
                    new_population.append(child)
        return new_population

    # ---------- pętla główna ----------
    def run(self) -> GAResult:
        population = self.initial_population()                    # 1
        result = GAResult(best_chromosome=[], best_fitness=float("-inf"))

        for _ in range(self.config.iterations):                   # 4 (warunek stopu)
            fitnesses = self.evaluate(population)                 # 2
            best_idx = max(range(len(population)), key=lambda i: fitnesses[i])  # 3
            if fitnesses[best_idx] > result.best_fitness:
                result.best_fitness = fitnesses[best_idx]
                result.best_chromosome = population[best_idx][:]
            result.history_best.append(fitnesses[best_idx])
            result.history_mean.append(sum(fitnesses) / len(fitnesses))
            population = self.next_generation(population, fitnesses)  # 5, 6, 7
        return result
