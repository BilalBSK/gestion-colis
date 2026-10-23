"""Mesures de performance pour 100, 1 000, 10 000 et 100 000 colis.

Pour chaque opération, je garde le meilleur temps sur plusieurs essais : ça
évite qu'un ralentissement passager du système fausse la mesure. Je mesure la
mémoire avec tracemalloc. Camion de 1 000 kg, priorité ignorée.

J'écris aussi les résultats dans docs/mesures/benchmark.json, que
outils/graphiques.py relit pour tracer les courbes.

Usage, depuis la racine du projet :  python3 outils/benchmark.py
"""

import json
import os
import platform
import random
import sys
import time
import tracemalloc

RACINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(RACINE, "src"))

from chargement import glouton, sac_a_dos_dp  # noqa: E402
from generateur import NIVEAUX, generer_colis  # noqa: E402
from gestion import GestionColis  # noqa: E402
from tris import tri_insertion  # noqa: E402

CAPACITE = 1_000
INSERTION_MAX = 10_000        # au-delà, le tri par insertion prendrait plusieurs minutes
SORTIE = os.path.join(RACINE, "docs", "mesures", "benchmark.json")

LIGNES = (  # (clé, libellé, complexité)
    ("construction", "Construction (n ajouts)", "O(n)"),
    ("recherche_hachage", "Recherche par hachage", "O(1)"),
    ("recherche_sequentielle", "Recherche séquentielle", "O(n)"),
    ("tri_insertion", "Tri par poids, insertion", "O(n²)"),
    ("tri_fusion", "Tri par poids, fusion", "O(n log n)"),
    ("tri_natif", "Tri par poids, sorted()", "O(n log n)"),
    ("tri_comptage", "Tri par priorité, comptage", "O(n)"),
    ("statistiques", "Statistiques", "O(n)"),
    ("dp_sans_elagage", "Camion, DP sans élagage", "O(n.W)"),
    ("dp_avec_elagage", "Camion, DP avec élagage", "O(n log n + n'.W)"),
    ("glouton", "Camion, glouton", "O(n log n)"),
)


def chrono(fonction, essais):
    meilleur = float("inf")
    for _ in range(essais):
        debut = time.perf_counter()
        fonction()
        meilleur = min(meilleur, time.perf_counter() - debut)
    return meilleur


def pic_memoire(fonction):
    tracemalloc.start()
    fonction()
    pic = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    return pic


def mesurer(n):
    rng = random.Random(n)
    colis = generer_colis(n)
    gestion = GestionColis(colis)
    essais = 5 if n <= 10_000 else 3
    t = {}
    t["construction"] = chrono(lambda: GestionColis(colis), essais)
    cibles = [rng.choice(colis).identifiant for _ in range(10_000)]
    t["recherche_hachage"] = chrono(lambda: [gestion.rechercher(i) for i in cibles], essais) / len(cibles)
    cibles_seq = cibles[:max(20, 1_000_000 // n)]
    t["recherche_sequentielle"] = chrono(
        lambda: [gestion.rechercher_sequentielle(i) for i in cibles_seq], 1) / len(cibles_seq)
    t["tri_insertion"] = (chrono(lambda: tri_insertion(colis, lambda c: c.poids), 1)
                          if n <= INSERTION_MAX else None)
    t["tri_fusion"] = chrono(lambda: gestion.trier("poids"), essais)
    t["tri_natif"] = chrono(lambda: sorted(colis, key=lambda c: c.poids), essais)
    t["tri_comptage"] = chrono(lambda: gestion.trier("priorite"), essais)
    t["statistiques"] = chrono(gestion.statistiques, essais)
    t["dp_sans_elagage"] = chrono(lambda: sac_a_dos_dp(colis, CAPACITE, avec_elagage=False),
                                  1 if n == 100_000 else 3)
    t["dp_avec_elagage"] = chrono(lambda: sac_a_dos_dp(colis, CAPACITE), 3)
    t["glouton"] = chrono(lambda: glouton(colis, CAPACITE), 3)

    sans = sac_a_dos_dp(colis, CAPACITE, avec_elagage=False)
    avec = sac_a_dos_dp(colis, CAPACITE)
    assert sans.score == avec.score, "l'élagage doit donner le même optimum"
    return {
        "temps": t,
        "memoire": {
            "collection": pic_memoire(lambda: GestionColis(generer_colis(n))),
            "dp_sans_elagage": pic_memoire(lambda: sac_a_dos_dp(colis, CAPACITE, avec_elagage=False)),
            "dp_avec_elagage": pic_memoire(lambda: sac_a_dos_dp(colis, CAPACITE)),
        },
        "candidats": avec.candidats,
        "glouton_sur_optimum": glouton(colis, CAPACITE).score / avec.score,
    }


def fmt(s):
    if s is None:
        return "-"
    if s < 1e-6:
        return f"{s * 1e9:.0f} ns"
    if s < 1e-3:
        return f"{s * 1e6:.1f} µs"
    return f"{s * 1e3:.1f} ms" if s < 1 else f"{s:.2f} s"


def main():
    resultats = {}
    for n in NIVEAUX.values():
        print(f"mesures pour n = {n} ...", file=sys.stderr, flush=True)
        resultats[n] = mesurer(n)
    tailles = list(resultats)

    print(f"Python {platform.python_version()}, camion de {CAPACITE} kg\n")
    entete = f"{'Opération':<28}{'complexité':>18}" + "".join(f"{'n = ' + str(n):>11}" for n in tailles)
    print(entete)
    print("-" * len(entete))
    for cle, libelle, complexite in LIGNES:
        print(f"{libelle:<28}{complexite:>18}" + "".join(f"{fmt(resultats[n]['temps'][cle]):>11}" for n in tailles))
    print("-" * len(entete))
    for cle, libelle in (("collection", "Mémoire de la collection"),
                         ("dp_sans_elagage", "Mémoire DP sans élagage"),
                         ("dp_avec_elagage", "Mémoire DP avec élagage")):
        print(f"{libelle:<46}" + "".join(f"{resultats[n]['memoire'][cle] / 1e6:>8.1f} Mo" for n in tailles))
    print(f"{'Colis gardés après élagage':<46}" + "".join(f"{resultats[n]['candidats']:>11}" for n in tailles))
    print(f"{'Valeur du glouton / optimum':<46}"
          + "".join(f"{100 * resultats[n]['glouton_sur_optimum']:>9.2f} %" for n in tailles))

    # Avec l'élagage, le nombre de colis gardés est proportionnel à W : le calcul croît comme W²
    print("\nEffet de la capacité, 100 000 colis, DP avec élagage")
    print(f"{'W (kg)':>8} | {'colis gardés':>12} | {'cases':>9} | {'temps':>8}")
    colis = generer_colis(100_000)
    effet_capacite = {}
    for capacite in (500, 1_000, 2_000, 5_000):
        debut = time.perf_counter()
        ch = sac_a_dos_dp(colis, capacite)
        duree = time.perf_counter() - debut
        effet_capacite[capacite] = {"temps": duree, "candidats": ch.candidats}
        print(f"{capacite:>8} | {ch.candidats:>12} | {ch.candidats * (capacite + 1) / 1e6:>7.1f} M | {fmt(duree):>8}")

    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    with open(SORTIE, "w", encoding="utf-8") as f:
        json.dump({"python": platform.python_version(), "capacite": CAPACITE,
                   "resultats": resultats, "effet_capacite": effet_capacite}, f, indent=1)
    print(f"\nRésultats enregistrés dans {os.path.relpath(SORTIE, RACINE)}")


if __name__ == "__main__":
    main()
