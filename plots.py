"""Rysowanie wykresów (jedyny moduł korzystający z matplotlib)."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot_series(series, optimum, title, path, ylabel="Wartość funkcji przystosowania"):
    """series: dict {etykieta: lista wartości najlepszego osobnika w kolejnych iteracjach}."""
    fig, ax = plt.subplots(figsize=(9, 5.2), dpi=130)
    for label, values in series.items():
        ax.plot(range(1, len(values) + 1), values, label=label, linewidth=1.6)
    if optimum is not None:
        ax.axhline(optimum, color="black", linestyle="--", linewidth=1.1, label=f"optimum = {optimum:g}")
    ax.set_title(title)
    ax.set_xlabel("Iteracja")
    ax.set_ylabel(ylabel)
    ax.grid(alpha=0.3)
    ax.legend(loc="lower right", fontsize=9)
    fig.tight_layout()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)
