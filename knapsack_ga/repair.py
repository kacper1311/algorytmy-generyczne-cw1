"""Naprawa chromosomów niedopuszczalnych.

Funkcja przystosowania przypisuje 0 rozwiązaniom przekraczającym pojemność.
Przy dużych instancjach większość potomków przekracza pojemność, co (zwłaszcza
w selekcji rankingowej i turniejowej) prowadzi do zapadnięcia się populacji.
Naprawa usuwa losowo wybrane przedmioty, dopóki plecak nie zmieści się
w limicie - jest losowa, aby nie zamieniać AG w algorytm zachłanny.
"""


def random_repair(chromosome, problem, rng):
    """Usuwa losowe przedmioty, aż łączna waga <= pojemność. Zwraca nowy chromosom."""
    chromosome = chromosome[:]
    weight = problem.total_weight(chromosome)
    if weight <= problem.capacity:
        return chromosome
    packed = [i for i, gene in enumerate(chromosome) if gene]
    rng.shuffle(packed)
    for i in packed:
        if weight <= problem.capacity:
            break
        chromosome[i] = 0
        weight -= problem.items[i].weight
    return chromosome
