"""Compare la mémoire occupée par 100 000 colis selon leur représentation.

Usage, depuis la racine du projet :  python3 outils/mesure_memoire_colis.py
"""

import os
import sys
import tracemalloc
from collections import namedtuple
from dataclasses import dataclass

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from colis import Colis  # noqa: E402

N = 100_000


@dataclass
class ColisSansSlots:
    identifiant: int
    poids: int
    valeur: int
    priorite: int
    destination: str


ColisTuple = namedtuple("ColisTuple", "identifiant poids valeur priorite destination")


def colis_dictionnaire(i, p, v, pr, d):
    return {"identifiant": i, "poids": p, "valeur": v, "priorite": pr, "destination": d}


def mesurer(fabrique):
    """Octets alloués pour créer N colis (identifiants > 256 : pas de petits entiers partagés)."""
    tracemalloc.start()
    avant = tracemalloc.get_traced_memory()[0]
    objets = [fabrique(1000 + i, 8, 20, 2, "Paris") for i in range(N)]
    apres = tracemalloc.get_traced_memory()[0]
    tracemalloc.stop()
    del objets
    return apres - avant


def main():
    representations = [
        ("Dictionnaire par colis", colis_dictionnaire),
        ("dataclass sans slots", ColisSansSlots),
        ("namedtuple (tuple nommé)", ColisTuple),
        ("dataclass avec slots (retenu)", Colis),
    ]
    print(f"Mémoire pour {N:,} colis (liste comprise)".replace(",", " "))
    print(f"{'Représentation':<32}{'Total':>11}{'Par colis':>11}")
    for nom, fabrique in representations:
        octets = mesurer(fabrique)
        print(f"{nom:<32}{octets / 1e6:>8.1f} Mo{octets / N:>9.0f} o")


if __name__ == "__main__":
    main()
