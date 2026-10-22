"""Mesure le coût du chargement optimal (programmation dynamique) selon n et W.

Version de base SANS élagage (partie 8 du rapport) ; l'élagage et son gain sont
étudiés dans la partie 10 (outils/benchmark.py).

  1. n varie (100 à 100 000 colis), capacité fixe W = 1 000 kg ;
  2. W varie (100 à 10 000 kg), nombre de colis fixe n = 10 000.
Le glouton est mesuré à titre de comparaison (temps et valeur obtenue).

Usage, depuis la racine du projet :  python3 outils/mesure_chargement.py
"""

import os
import sys
import time
import tracemalloc

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from chargement import glouton, sac_a_dos_dp  # noqa: E402
from generateur import NIVEAUX, generer_colis  # noqa: E402


def fmt_temps(s):
    return f"{s * 1e3:.1f} ms" if s < 1 else f"{s:.2f} s"


def mesurer(colis, capacite):
    debut = time.perf_counter()
    dp = sac_a_dos_dp(colis, capacite, avec_elagage=False)
    t_dp = time.perf_counter() - debut
    debut = time.perf_counter()
    gl = glouton(colis, capacite)
    t_gl = time.perf_counter() - debut
    tracemalloc.start()
    sac_a_dos_dp(colis, capacite, avec_elagage=False)
    pic = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    cases = len(colis) * (capacite + 1)
    return (f"{cases / 1e6:>9.1f} M | {fmt_temps(t_dp):>9} | {pic / 1e6:>8.1f} Mo | "
            f"{fmt_temps(t_gl):>9} | {dp.score:>7} | {gl.score:>7} ({100 * gl.score / dp.score:.2f} %)")


def main():
    entete = (f"{'n':>7} | {'W (kg)':>6} | {'cases n.W':>11} | {'DP temps':>9} | {'DP mémoire':>11} | "
              f"{'glouton':>9} | {'val. DP':>7} | {'val. glouton':>7}")
    print(entete)
    print("-" * len(entete))
    for n in NIVEAUX.values():
        print(f"{n:>7} | {1000:>6} | " + mesurer(generer_colis(n), 1000))
    print("-" * len(entete))
    colis = generer_colis(10_000)
    for capacite in (100, 1_000, 10_000):
        print(f"{10_000:>7} | {capacite:>6} | " + mesurer(colis, capacite))


if __name__ == "__main__":
    main()
