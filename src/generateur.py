"""Génération de colis aléatoires pour les 4 tailles du sujet.

Avec la même graine, j'obtiens toujours les mêmes colis : je peux donc refaire
une mesure à l'identique. O(n).
"""

import random

from colis import PRIORITE_MAX, PRIORITE_MIN, Colis

NIVEAUX = {1: 100, 2: 1_000, 3: 10_000, 4: 100_000}
DESTINATIONS = ("Paris", "Lille", "Lyon", "Marseille", "Toulouse",
                "Bordeaux", "Nantes", "Strasbourg", "Nice", "Rennes")
POIDS_MIN, POIDS_MAX = 1, 30     # kg
GRAINE_PAR_DEFAUT = 2026


def generer_colis(n, graine=GRAINE_PAR_DEFAUT, identifiant_depart=1):
    """n colis aléatoires, avec des identifiants tous différents.

    Je prends des identifiants qui se suivent puis je les mélange, pour que
    l'ordre de la collection ne soit pas celui des identifiants.
    La valeur est comprise entre 1 et 4 fois le poids. Au début j'ajoutais un
    petit bonus fixe à chaque valeur, mais les colis de 1 kg devenaient alors
    bien plus rentables au kilo et le camion ne se remplissait plus qu'avec eux.
    """
    rng = random.Random(graine)
    identifiants = list(range(identifiant_depart, identifiant_depart + n))
    rng.shuffle(identifiants)
    colis = []
    for identifiant in identifiants:
        poids = rng.randint(POIDS_MIN, POIDS_MAX)
        valeur = rng.randint(poids, 4 * poids)
        priorite = rng.randint(PRIORITE_MIN, PRIORITE_MAX)
        colis.append(Colis(identifiant, poids, valeur, priorite, rng.choice(DESTINATIONS)))
    return colis
