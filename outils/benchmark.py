"""Étude des performances (partie 7 du sujet) : principales opérations, 100 à 100 000 colis.

Mesure le temps de chaque opération (meilleur de plusieurs exécutions) et, pour
le chargement, le pic de mémoire. Camion de 1 000 kg. Les résultats sont
affichés et enregistrés dans docs/mesures/benchmark.json (utilisé par
outils/graphiques.py pour tracer les courbes).

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

CAPACITE = 1_000
SORTIE = os.path.join(RACINE, "docs", "mesures", "benchmark.json")

OPERATIONS = (  # (clé, libellé, complexité)
    ("construction", "Construction (n ajouts)", "O(n)"),
    ("recherche_hachage", "Recherche - table de hachage", "O(1)"),
    ("recherche_sequentielle", "Recherche - séquentielle", "O(n)"),
    ("tri_fusion", "Tri par poids - tri fusion", "O(n log n)"),
    ("tri_natif", "Tri par poids - sorted()", "O(n log n)"),
    ("tri_comptage", "Tri par priorité - comptage", "O(n)"),
    ("statistiques", "Statistiques", "O(n)"),
    ("dp_sans_elagage", "Chargement - DP sans élagage", "O(n.W)"),
    ("dp_avec_elagage", "Chargement - DP avec élagage", "O(n log n + n'.W)"),
    ("glouton", "Chargement - glouton", "O(n log n)"),
)


def chrono(fonction, repetitions):
    meilleur = float("inf")
    for _ in range(repetitions):
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
    rep = 5 if n <= 10_000 else 3
    t = {}
    t["construction"] = chrono(lambda: GestionColis(colis), rep)
    cibles = [rng.choice(colis).identifiant for _ in range(10_000)]
    t["recherche_hachage"] = chrono(lambda: [gestion.rechercher(i) for i in cibles], rep) / len(cibles)
    cibles_seq = cibles[:max(20, 1_000_000 // n)]
    t["recherche_sequentielle"] = chrono(
        lambda: [gestion.rechercher_sequentielle(i) for i in cibles_seq], 1) / len(cibles_seq)
    t["tri_fusion"] = chrono(lambda: gestion.trier("poids"), rep)
    t["tri_natif"] = chrono(lambda: sorted(colis, key=lambda c: c.poids), rep)
    t["tri_comptage"] = chrono(lambda: gestion.trier("priorite"), rep)
    t["statistiques"] = chrono(gestion.statistiques, rep)
    t["dp_sans_elagage"] = chrono(lambda: sac_a_dos_dp(colis, CAPACITE, avec_elagage=False), 1 if n == 100_000 else 3)
    t["dp_avec_elagage"] = chrono(lambda: sac_a_dos_dp(colis, CAPACITE, avec_elagage=True), 3)
    t["glouton"] = chrono(lambda: glouton(colis, CAPACITE), 3)

    sans = sac_a_dos_dp(colis, CAPACITE, avec_elagage=False)
    avec = sac_a_dos_dp(colis, CAPACITE, avec_elagage=True)
    assert sans.score == avec.score, "l'élagage doit conserver l'optimum"
    m = {
        "dp_sans_elagage": pic_memoire(lambda: sac_a_dos_dp(colis, CAPACITE, avec_elagage=False)),
        "dp_avec_elagage": pic_memoire(lambda: sac_a_dos_dp(colis, CAPACITE, avec_elagage=True)),
    }
    autres = {"candidats_sans": sans.candidats, "candidats_avec": avec.candidats,
              "valeur_optimale": avec.score, "valeur_glouton": glouton(colis, CAPACITE).score}
    return {"temps": t, "memoire": m, **autres}


def fmt(s):
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
    entete = f"{'Opération':<31}{'complexité':>18}" + "".join(f"{f'n = {n}':>11}" for n in tailles)
    print(entete)
    print("-" * len(entete))
    for cle, libelle, complexite in OPERATIONS:
        print(f"{libelle:<31}{complexite:>18}" + "".join(f"{fmt(resultats[n]['temps'][cle]):>11}" for n in tailles))
    print("-" * len(entete))
    for cle, libelle in (("dp_sans_elagage", "Mémoire DP sans élagage"), ("dp_avec_elagage", "Mémoire DP avec élagage")):
        print(f"{libelle:<49}" + "".join(f"{resultats[n]['memoire'][cle] / 1e6:>8.1f} Mo" for n in tailles))
    print(f"{"Colis candidats après élagage (n')":<49}"
          + "".join(f"{resultats[n]['candidats_avec']:>11}" for n in tailles))
    print(f"{'Valeur glouton / optimum':<49}"
          + "".join(f"{resultats[n]['valeur_glouton'] / resultats[n]['valeur_optimale'] * 100:>9.2f} %" for n in tailles))

    # Effet de la capacité : avec l'élagage, n' ~ W ln(30), donc le coût n' x W croît comme W²
    print(f"\nEffet de la capacité, n = 100 000 colis (DP avec élagage)")
    print(f"{'W (kg)':>8} | {"candidats n'":>12} | {"cases n' x W":>13} | {'temps':>8} | {'cases sans élagage':>18}")
    colis = generer_colis(100_000)
    effet_w = {}
    for capacite in (500, 1_000, 2_000, 5_000):
        debut = time.perf_counter()
        ch = sac_a_dos_dp(colis, capacite)
        duree = time.perf_counter() - debut
        effet_w[capacite] = {"temps": duree, "candidats": ch.candidats}
        print(f"{capacite:>8} | {ch.candidats:>12} | {ch.candidats * (capacite + 1) / 1e6:>11.1f} M | "
              f"{fmt(duree):>8} | {100_000 * (capacite + 1) / 1e6:>16.0f} M")

    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    with open(SORTIE, "w", encoding="utf-8") as f:
        json.dump({"python": platform.python_version(), "capacite": CAPACITE, "resultats": resultats,
                   "effet_capacite": effet_w}, f, indent=1)
    print(f"\nRésultats enregistrés dans {os.path.relpath(SORTIE, RACINE)}")


if __name__ == "__main__":
    main()
