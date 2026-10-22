"""Compare les temps de tri, pour n = 100 à 100 000 colis.

  - tri par insertion (O(n²))       : référence naïve, mesurée jusqu'à 10 000
  - tri fusion maison (O(n log n))  : retenu pour le poids et la valeur
  - sorted() natif (Timsort, en C)  : fonction native de Python
  - tri par comptage (O(n + k))     : retenu pour la priorité
  - tri fusion appliqué à la priorité, pour comparaison

Usage, depuis la racine du projet :  python3 outils/mesure_tris.py
"""

import os
import random
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from colis import Colis  # noqa: E402
from tris import tri_comptage, tri_fusion, tri_insertion  # noqa: E402

TAILLES = (100, 1_000, 10_000, 100_000)
INSERTION_MAX = 10_000   # au-delà, le tri par insertion prendrait plusieurs minutes


def chrono(fonction, repetitions):
    """Meilleur temps sur plusieurs exécutions, en secondes (limite le bruit de mesure)."""
    meilleur = float("inf")
    for _ in range(repetitions):
        debut = time.perf_counter()
        fonction()
        meilleur = min(meilleur, time.perf_counter() - debut)
    return meilleur


def fmt(s):
    if s is None:
        return "-"
    return f"{s * 1e6:.0f} µs" if s < 1e-3 else (f"{s * 1e3:.1f} ms" if s < 1 else f"{s:.2f} s")


def main():
    rng = random.Random(2026)
    poids = lambda c: c.poids        # noqa: E731
    priorite = lambda c: c.priorite  # noqa: E731
    entete = (f"{'n':>7} | {'insertion':>9} | {'fusion':>9} | {'sorted()':>9} || "
              f"{'comptage':>9} | {'fusion':>9}")
    print(f"{'':>7}   {'--- tri par poids ---':^33} || {'- tri par priorité -':^21}")
    print(entete)
    print("-" * len(entete))
    for n in TAILLES:
        colis = [Colis(i, rng.randint(1, 30), rng.randint(1, 100), rng.randint(1, 5), "Paris")
                 for i in range(n)]
        rep = 5 if n <= 10_000 else 3
        t_ins = chrono(lambda: tri_insertion(colis, poids), 1) if n <= INSERTION_MAX else None
        t_fus = chrono(lambda: tri_fusion(colis, poids), rep)
        t_nat = chrono(lambda: sorted(colis, key=poids), rep)
        t_cpt = chrono(lambda: tri_comptage(colis, priorite, 1, 5), rep)
        t_fpr = chrono(lambda: tri_fusion(colis, priorite), rep)
        print(f"{n:>7} | {fmt(t_ins):>9} | {fmt(t_fus):>9} | {fmt(t_nat):>9} || "
              f"{fmt(t_cpt):>9} | {fmt(t_fpr):>9}")


if __name__ == "__main__":
    main()
