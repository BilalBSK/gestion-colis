"""Compare trois façons de rechercher un colis par identifiant, pour n = 100 à 100 000.

  - table de hachage (dict)              : méthode retenue, O(1) en moyenne
  - recherche séquentielle (liste)       : O(n)
  - recherche dichotomique (liste triée) : O(log n), mais insertion en O(n)

Usage, depuis la racine du projet :  python3 outils/mesure_recherche.py
"""

import os
import random
import sys
import time
import tracemalloc

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from colis import Colis  # noqa: E402
from gestion import GestionColis  # noqa: E402

TAILLES = (100, 1_000, 10_000, 100_000)


def recherche_dichotomique(ids_tries, colis_tries, identifiant):
    """Recherche dans une liste triée par identifiant : O(log n).

    On compare l'identifiant cherché à celui du milieu de l'intervalle, puis on
    ne garde que la moitié qui peut le contenir. L'intervalle est divisé par 2
    à chaque tour : au plus log2(n) + 1 tours.
    """
    debut, fin = 0, len(ids_tries) - 1
    while debut <= fin:
        milieu = (debut + fin) // 2
        if ids_tries[milieu] == identifiant:
            return colis_tries[milieu]
        if ids_tries[milieu] < identifiant:
            debut = milieu + 1
        else:
            fin = milieu - 1
    return None


def temps_moyen(fonction, cibles):
    """Temps moyen d'une recherche, en microsecondes."""
    debut = time.perf_counter()
    for cible in cibles:
        fonction(cible)
    return (time.perf_counter() - debut) / len(cibles) * 1e6


def fmt(us):
    return f"{us * 1000:.0f} ns" if us < 1 else f"{us:.1f} µs"


def main():
    rng = random.Random(2026)
    entete = (f"{'n':>8} | {'hachage':>9} | {'dichotomie':>10} | {'séquentielle':>12} | "
              f"{'séq. (absent)':>13} | {'mémoire dict':>12}")
    print(entete)
    print("-" * len(entete))
    for n in TAILLES:
        ids = rng.sample(range(1, 10 * n), n)  # identifiants uniques, dans le désordre
        colis = [Colis(i, 1 + i % 30, i % 100, 1 + i % 5, "Paris") for i in ids]

        tracemalloc.start()
        gestion = GestionColis(colis)
        memoire = tracemalloc.get_traced_memory()[0]
        tracemalloc.stop()

        colis_tries = sorted(colis, key=lambda c: c.identifiant)  # préparation de la dichotomie
        ids_tries = [c.identifiant for c in colis_tries]

        cibles = [rng.choice(ids) for _ in range(20_000)]
        cibles_seq = cibles[:max(20, 2_000_000 // n)]  # moins d'essais : la séquentielle est lente
        absents = [0] * len(cibles_seq)                # identifiant absent : pire cas

        t_hash = temps_moyen(gestion.rechercher, cibles)
        t_dicho = temps_moyen(lambda i: recherche_dichotomique(ids_tries, colis_tries, i), cibles)
        t_seq = temps_moyen(gestion.rechercher_sequentielle, cibles_seq)
        t_abs = temps_moyen(gestion.rechercher_sequentielle, absents)
        print(f"{n:>8} | {fmt(t_hash):>9} | {fmt(t_dicho):>10} | {fmt(t_seq):>12} | {fmt(t_abs):>13} | "
              f"{memoire / 1e3:>9.0f} Ko")


if __name__ == "__main__":
    main()
