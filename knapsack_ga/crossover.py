"""Operatory krzyżowania.

Sygnatura: crossover(parent1, parent2, rng) -> (child1, child2).
"""


def one_point_crossover(parent1, parent2, rng):
    """Krzyżowanie jednopunktowe: losujemy punkt cięcia i wymieniamy
    końcowe fragmenty chromosomów."""
    n = len(parent1)
    if n < 2:
        return parent1[:], parent2[:]
    point = rng.randint(1, n - 1)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    return child1, child2


def two_point_crossover(parent1, parent2, rng):
    """Krzyżowanie dwupunktowe: losujemy dwa punkty cięcia i wymieniamy
    fragment chromosomu leżący między nimi."""
    n = len(parent1)
    if n < 3:
        return one_point_crossover(parent1, parent2, rng)
    a, b = sorted(rng.sample(range(1, n), 2))
    child1 = parent1[:a] + parent2[a:b] + parent1[b:]
    child2 = parent2[:a] + parent1[a:b] + parent2[b:]
    return child1, child2
