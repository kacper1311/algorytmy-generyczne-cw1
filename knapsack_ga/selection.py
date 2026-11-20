"""Metody selekcji.

Każda funkcja ma sygnaturę: selection(population, fitnesses, rng) -> lista
rodziców o długości równej rozmiarowi populacji. Dany osobnik może zostać
wybrany więcej niż raz.
"""
from bisect import bisect_left
from itertools import accumulate


def _select_proportional(population, weights, rng):
    """Losowanie ze zwracaniem z prawdopodobieństwem proporcjonalnym do wag
    (wirtualne koło ruletki zbudowane z sum skumulowanych)."""
    total = sum(weights)
    if total <= 0:  # wszystkie wagi zerowe -> każdy ma równe szanse
        return [rng.choice(population) for _ in population]
    cumulative = list(accumulate(weights))
    selected = []
    for _ in population:
        pointer = rng.random() * total
        index = min(bisect_left(cumulative, pointer), len(population) - 1)
        selected.append(population[index])
    return selected


def roulette_selection(population, fitnesses, rng):
    """Selekcja koła ruletki: p(ch_i) = f(ch_i) / sum_j f(ch_j)."""
    return _select_proportional(population, fitnesses, rng)


def rank_selection(population, fitnesses, rng):
    """Selekcja rankingowa (liniowa).

    Osobniki są sortowane od najlepszego do najgorszego. Osobnik o randze r
    (r = 1 dla najlepszego) dostaje wagę N - r + 1, czyli oczekiwana liczba
    jego kopii maleje liniowo wraz z rangą (rysunek w punkcie 3.4.3).
    Wynik zależy tylko od kolejności osobników, a nie od samych wartości fitness.
    """
    n = len(population)
    order = sorted(range(n), key=lambda i: fitnesses[i], reverse=True)
    ranked = [population[i] for i in order]
    weights = [n - rank for rank in range(n)]  # n, n-1, ..., 1
    return _select_proportional(ranked, weights, rng)


def tournament_selection(population, fitnesses, rng, k=3):
    """Selekcja turniejowa: losujemy k osobników i wybieramy najlepszego.
    Operację powtarzamy tyle razy, ile jest osobników w populacji."""
    n = len(population)
    selected = []
    for _ in range(n):
        contestants = rng.sample(range(n), min(k, n))
        winner = max(contestants, key=lambda i: fitnesses[i])
        selected.append(population[winner])
    return selected


def make_tournament_selection(k):
    """Tworzy funkcję selekcji turniejowej z ustalonym rozmiarem turnieju k."""
    def selection(population, fitnesses, rng):
        return tournament_selection(population, fitnesses, rng, k=k)
    selection.__name__ = f"tournament_selection_k{k}"
    return selection
