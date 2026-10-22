"""Démonstration de l'étape 3 : tris par poids, valeur et priorité.

Usage, depuis la racine du projet :  python3 outils/demo_etape3.py
"""

import os
import sys

RACINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(RACINE, "src"))

from affichage import tableau  # noqa: E402
from colis import Colis  # noqa: E402
from gestion import GestionColis  # noqa: E402

DEMANDES = (
    ("Tri par poids croissant (tri fusion)", "poids", False),
    ("Tri par valeur décroissante (tri fusion)", "valeur", True),
    ("Tri par priorité décroissante (tri par comptage)", "priorite", True),
    ("Tri par priorité puis valeur, décroissant (fusion puis comptage stable)", "priorite_valeur", True),
)


def main():
    gestion = GestionColis.depuis_csv(os.path.join(RACINE, "donnees", "colis_exemple.csv"))
    gestion.ajouter(Colis(106, 4, 30, 5, "Nice"))  # même priorité que 102 : utile au tri combiné
    print("Colis du sujet + colis 106 (4 kg, valeur 30, priorité 5, Nice)")
    for titre, critere, decroissant in DEMANDES:
        print(f"\n>>> {titre}")
        print("\n".join(tableau(gestion.trier(critere, decroissant))))


if __name__ == "__main__":
    main()
