"""Reprezentacja problemu plecakowego oraz import danych z pliku tekstowego."""
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Item:
    """Pojedynczy przedmiot: wartość i waga."""
    value: float
    weight: float


@dataclass
class KnapsackProblem:
    """Instancja problemu plecakowego."""
    name: str
    capacity: float
    items: list

    @property
    def size(self) -> int:
        """Liczba przedmiotów = długość chromosomu."""
        return len(self.items)

    def total_value(self, chromosome) -> float:
        return sum(item.value for item, gene in zip(self.items, chromosome) if gene)

    def total_weight(self, chromosome) -> float:
        return sum(item.weight for item, gene in zip(self.items, chromosome) if gene)

    def is_feasible(self, chromosome) -> bool:
        return self.total_weight(chromosome) <= self.capacity

    def selected_items(self, chromosome) -> list:
        """Numery (od 1) przedmiotów zapakowanych do plecaka."""
        return [i + 1 for i, gene in enumerate(chromosome) if gene]


def _parse_number(text: str):
    """Zwraca int, jeśli liczba jest całkowita, w przeciwnym razie float."""
    number = float(text)
    return int(number) if number.is_integer() else number


def load_problem(path) -> KnapsackProblem:
    """Importuje dane problemu plecakowego z pliku tekstowego.

    Format pliku:
        liczba_przedmiotów pojemność
        wartość_1 waga_1
        ...
        wartość_n waga_n
    Wczytywane jest dokładnie n niepustych wierszy (niektóre pliki mają
    na końcu puste linie lub dodatkowe informacje).
    """
    path = Path(path)
    lines = [line.split() for line in path.read_text().splitlines() if line.strip()]
    if not lines:
        raise ValueError(f"Pusty plik: {path}")

    n = int(float(lines[0][0]))
    capacity = _parse_number(lines[0][1])
    if len(lines) - 1 < n:
        raise ValueError(f"{path}: oczekiwano {n} przedmiotów, znaleziono {len(lines) - 1}")

    items = [Item(_parse_number(v), _parse_number(w)) for v, w, *_ in lines[1:n + 1]]
    return KnapsackProblem(name=path.name, capacity=capacity, items=items)


def load_optimum(path) -> float:
    """Wczytuje znane optimum (pierwsza liczba w pliku)."""
    return _parse_number(Path(path).read_text().split()[0])
