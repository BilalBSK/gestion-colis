"""Mesure le temps et la mémoire des opérations de gestion aux 4 niveaux du sujet.

Usage, depuis la racine du projet :  python3 outils/mesure_echelle.py
"""

import os
import random
import sys
import tempfile
import time
import tracemalloc

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from affichage import page, tableau  # noqa: E402
from generateur import NIVEAUX, generer_colis  # noqa: E402
from gestion import GestionColis  # noqa: E402
from stockage import ecrire_csv, lire_csv  # noqa: E402


def chrono(fonction, repetitions=3):
    """Meilleur temps sur plusieurs exécutions (limite le bruit de mesure), et dernier résultat."""
    meilleur, resultat = float("inf"), None
    for _ in range(repetitions):
        debut = time.perf_counter()
        resultat = fonction()
        meilleur = min(meilleur, time.perf_counter() - debut)
    return meilleur, resultat


def fmt_temps(s):
    if s < 1e-6:
        return f"{s * 1e9:.0f} ns"
    if s < 1e-3:
        return f"{s * 1e6:.1f} µs"
    return f"{s * 1e3:.1f} ms" if s < 1 else f"{s:.2f} s"


def fmt_octets(o):
    return f"{o / 1e3:.0f} Ko" if o < 1e6 else f"{o / 1e6:.1f} Mo"


def mesurer(n, dossier):
    r = {}
    rng = random.Random(n)
    r["génération des colis"], colis = chrono(lambda: generer_colis(n))
    r["construction (n ajouts)"], gestion = chrono(lambda: GestionColis(colis))

    tracemalloc.start()
    g = GestionColis(generer_colis(n))
    r["mémoire (colis + table)"] = tracemalloc.get_traced_memory()[0]
    tracemalloc.stop()
    del g

    chemin = os.path.join(dossier, f"colis_{n}.csv")
    r["écriture CSV"], _ = chrono(lambda: ecrire_csv(chemin, colis))
    r["taille du fichier CSV"] = os.path.getsize(chemin)
    r["lecture CSV + construction"], _ = chrono(lambda: GestionColis(lire_csv(chemin)))

    cibles = [rng.choice(colis).identifiant for _ in range(10_000)]
    t, _ = chrono(lambda: [gestion.rechercher(i) for i in cibles])
    r["recherche (1 colis)"] = t / len(cibles)
    r["tri par poids (fusion)"], _ = chrono(lambda: gestion.trier("poids"))
    r["tri par priorité (comptage)"], _ = chrono(lambda: gestion.trier("priorite"))
    r["statistiques"], _ = chrono(lambda: gestion.statistiques())
    liste = gestion.lister()
    r["affichage d'une page (20)"], _ = chrono(lambda: page(liste, 0, 20))
    r["mise en forme de tout"], _ = chrono(lambda: tableau(liste))
    return r


def main():
    with tempfile.TemporaryDirectory() as dossier:
        resultats = {n: mesurer(n, dossier) for n in NIVEAUX.values()}
    operations = list(next(iter(resultats.values())))
    entete = f"{'Opération':<29}" + "".join(f"{f'n = {n}':>12}" for n in resultats)
    print(entete)
    print("-" * len(entete))
    for op in operations:
        fmt = fmt_octets if op.startswith(("mémoire", "taille")) else fmt_temps
        print(f"{op:<29}" + "".join(f"{fmt(resultats[n][op]):>12}" for n in resultats))


if __name__ == "__main__":
    main()
