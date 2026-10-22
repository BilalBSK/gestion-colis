"""Génération de jeux de colis aléatoires pour les 4 niveaux du sujet.

Les données sont REPRODUCTIBLES : avec la même graine, on obtient exactement
les mêmes colis, ce qui permet de refaire une mesure ou un test à l'identique.

Coût : O(n) en temps et en mémoire.
"""

import random

from colis import PRIORITE_MAX, PRIORITE_MIN, Colis

NIVEAUX = {1: 100, 2: 1_000, 3: 10_000, 4: 100_000}
DESTINATIONS = ("Paris", "Lille", "Lyon", "Marseille", "Toulouse",
                "Bordeaux", "Nantes", "Strasbourg", "Nice", "Rennes")
POIDS_MIN, POIDS_MAX = 1, 30     # kg
GRAINE_PAR_DEFAUT = 2026


def generer_colis(n, graine=GRAINE_PAR_DEFAUT, identifiant_depart=1):
    """Renvoie une liste de ``n`` colis aléatoires aux identifiants uniques.

    - Identifiants : les entiers identifiant_depart, ..., identifiant_depart + n - 1,
      donc tous différents, puis MÉLANGÉS (mélange de Fisher-Yates, O(n)) pour
      que l'ordre de la collection ne soit pas celui des identifiants.
    - Poids : uniforme entre 1 et 30 kg.
    - Valeur : corrélée au poids (entre 1 et 4 fois le poids, plus 0 à 10).
      Un colis lourd vaut en général davantage, comme dans la réalité. Avec des
      valeurs indépendantes du poids, le meilleur chargement serait presque
      toujours « les colis les plus légers », ce qui rendrait le problème du
      camion artificiellement facile.
    - Priorité : uniforme entre 1 et 5. Destination : une des 10 villes.
    """
    rng = random.Random(graine)
    identifiants = list(range(identifiant_depart, identifiant_depart + n))
    rng.shuffle(identifiants)
    colis = []
    for identifiant in identifiants:
        poids = rng.randint(POIDS_MIN, POIDS_MAX)
        valeur = rng.randint(poids, 4 * poids) + rng.randint(0, 10)
        priorite = rng.randint(PRIORITE_MIN, PRIORITE_MAX)
        colis.append(Colis(identifiant, poids, valeur, priorite, rng.choice(DESTINATIONS)))
    return colis
