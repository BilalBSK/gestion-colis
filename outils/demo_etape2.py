"""Démonstration de l'étape 2 : ajouter, afficher et rechercher des colis.

Usage, depuis la racine du projet :  python3 outils/demo_etape2.py
"""

import os
import sys

RACINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(RACINE, "src"))

from affichage import tableau  # noqa: E402
from colis import Colis  # noqa: E402
from gestion import GestionColis  # noqa: E402


def main():
    gestion = GestionColis.depuis_csv(os.path.join(RACINE, "donnees", "colis_exemple.csv"))
    print(f"Chargement de donnees/colis_exemple.csv : {len(gestion)} colis\n")

    print(">>> Ajouter le colis 106 (4 kg, valeur 30, priorité 5, Nice)")
    gestion.ajouter(Colis(106, 4, 30, 5, "Nice"))
    print(f"Colis 106 ajouté : {len(gestion)} colis\n")

    print(">>> Ajouter un autre colis d'identifiant 101")
    try:
        gestion.ajouter(Colis(101, 1, 1, 1, "Lyon"))
    except ValueError as erreur:
        print(f"Refusé : {erreur}\n")

    print(">>> Afficher les colis")
    print("\n".join(tableau(gestion.lister())))

    print("\n>>> Rechercher le colis 103")
    print("\n".join(tableau([gestion.rechercher(103)])))

    print("\n>>> Rechercher le colis 999")
    resultat = gestion.rechercher(999)
    print("Aucun colis d'identifiant 999" if resultat is None else resultat)


if __name__ == "__main__":
    main()
