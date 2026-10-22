"""Étude des règles de prise en compte de la priorité (partie 6 du sujet).

  exemple : colis A, B, C, D de la partie 6.1, capacités de 8 à 23 kg,
            chargement obtenu par chaque règle.
  echelle : 10 000 colis générés, camion de 1 000 kg : compromis entre la
            valeur transportée et la priorité des colis chargés, selon la règle.

Usage, depuis la racine du projet :
    python3 outils/etude_priorite.py exemple
    python3 outils/etude_priorite.py echelle
"""

import os
import sys
import time

RACINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(RACINE, "src"))

from chargement import preparer_camion  # noqa: E402
from generateur import generer_colis  # noqa: E402
from stockage import lire_csv  # noqa: E402

REGLES = (("valeur seule", "valeur", 0), ("pondérée a=0,5", "ponderee", 0.5),
          ("pondérée a=1", "ponderee", 1), ("pondérée a=2", "ponderee", 2), ("stricte", "stricte", 0))


def exemple():
    colis = lire_csv(os.path.join(RACINE, "donnees", "colis_camion.csv"))
    print("Colis : A (8 kg, 20, p5)  B (6 kg, 25, p1)  C (5 kg, 18, p4)  D (4 kg, 14, p3)\n")
    print(f"{'W':>3} | " + " | ".join(f"{titre:<14}" for titre, _, _ in REGLES))
    print("-" * (6 + 17 * len(REGLES)))
    for capacite in range(8, 24):
        cellules = []
        for _, regle, alpha in REGLES:
            ch = preparer_camion(colis, capacite, regle, alpha)
            lettres = "+".join(sorted("ABCD"[c.identifiant - 1] for c in ch.colis))
            cellules.append(f"{lettres:<8}{ch.valeur_totale:>6}")
        print(f"{capacite:>3} | " + " | ".join(cellules))


def echelle():
    colis = generer_colis(10_000)
    capacite = 1_000
    regles = (("valeur seule", "valeur", 0),) + tuple(
        (f"pondérée alpha = {a:g}", "ponderee", a) for a in (0.25, 0.5, 1, 2, 5)) + (("stricte", "stricte", 0),)
    total_p5 = sum(c.priorite == 5 for c in colis)
    print(f"10 000 colis ({total_p5} de priorité 5), camion de {capacite} kg\n")
    print(f"{'Règle':<22} | {'valeur':>7} | {'% du max':>9} | {'prio. moy.':>10} | "
          f"{'colis p5':>8} | {'colis p1':>8} | {'temps DP':>8}")
    print("-" * 90)
    maximum = None
    for titre, regle, alpha in regles:
        debut = time.perf_counter()
        ch = preparer_camion(colis, capacite, regle, alpha)
        duree = time.perf_counter() - debut
        maximum = maximum or ch.valeur_totale     # la première règle donne la valeur maximale
        rep = ch.par_priorite
        print(f"{titre:<22} | {ch.valeur_totale:>7} | {100 * ch.valeur_totale / maximum:>7.1f} % | "
              f"{ch.priorite_moyenne:>10.2f} | {rep[5]:>8} | {rep[1]:>8} | {duree * 1e3:>5.0f} ms")


if __name__ == "__main__":
    actions = {"exemple": exemple, "echelle": echelle}
    if len(sys.argv) != 2 or sys.argv[1] not in actions:
        sys.exit(__doc__)
    actions[sys.argv[1]]()
