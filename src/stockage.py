"""Lecture d'un fichier de colis au format CSV.

Une ligne d'en-tête puis un colis par ligne. J'ai pris « ; » comme séparateur
parce que c'est celui des tableurs en français :

    identifiant;poids;valeur;priorite;destination
    101;8;20;2;Paris

Lecture en O(n) pour n lignes.
"""

import csv

from colis import Colis

CHAMPS = ("identifiant", "poids", "valeur", "priorite", "destination")


def lire_csv(chemin):
    """Renvoie la liste des colis du fichier, dans l'ordre des lignes.

    Si une ligne est invalide, j'indique son numéro dans l'erreur pour qu'on
    puisse corriger le fichier facilement.
    """
    colis = []
    with open(chemin, newline="", encoding="utf-8") as fichier:
        lecteur = csv.DictReader(fichier, delimiter=";")
        if lecteur.fieldnames is None or tuple(lecteur.fieldnames) != CHAMPS:
            raise ValueError(f"{chemin} : en-tête attendu « {';'.join(CHAMPS)} »")
        for numero, ligne in enumerate(lecteur, start=2):   # la ligne 1 est l'en-tête
            try:
                colis.append(Colis(
                    identifiant=int(ligne["identifiant"]),
                    poids=int(ligne["poids"]),
                    valeur=int(ligne["valeur"]),
                    priorite=int(ligne["priorite"]),
                    destination=ligne["destination"] or "",
                ))
            except (TypeError, ValueError) as erreur:
                raise ValueError(f"{chemin}, ligne {numero} : {erreur}") from erreur
    return colis
