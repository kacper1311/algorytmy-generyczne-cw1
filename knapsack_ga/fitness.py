"""Funkcja przystosowania dla problemu plecakowego."""


def knapsack_fitness(chromosome, problem) -> float:
    """Wartość przedmiotów w plecaku, jeśli ich łączna waga nie przekracza
    pojemności; w przeciwnym razie 0 (zgodnie z punktem 3.3 instrukcji)."""
    value = 0
    weight = 0
    for item, gene in zip(problem.items, chromosome):
        if gene:
            value += item.value
            weight += item.weight
    return value if weight <= problem.capacity else 0
