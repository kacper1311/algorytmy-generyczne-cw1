"""Operator mutacji."""


def bit_flip_mutation(chromosome, p_mutation, rng):
    """Mutacja binarna: dla każdego genu niezależnie z prawdopodobieństwem
    p_mutation zmieniamy bit na przeciwny. Zwraca nowy chromosom."""
    return [1 - gene if rng.random() < p_mutation else gene for gene in chromosome]
