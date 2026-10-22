"""Lecture et écriture de colis au format CSV.

Format : une ligne d'en-tête, puis un colis par ligne, champs séparés par « ; »
(séparateur usuel des tableurs français, la virgule servant de séparateur décimal).

    identifiant;poids;valeur;priorite;destination
    101;8;20;2;Paris

Complexité : O(n) en temps pour n lignes, O(n) en mémoire pour la liste renvoyée.
"""

import csv

from colis import Colis

CHAMPS = ("identifiant", "poids", "valeur", "priorite", "destination")


def lire_csv(chemin):
    """Renvoie la liste des colis du fichier, dans l'ordre des lignes.

    Lève ValueError en précisant le numéro de ligne si une donnée est invalide.
    """
    colis = []
    with open(chemin, newline="", encoding="utf-8") as fichier:
        lecteur = csv.DictReader(fichier, delimiter=";")
        if lecteur.fieldnames is None or tuple(lecteur.fieldnames) != CHAMPS:
            raise ValueError(f"{chemin} : en-tête attendu « {';'.join(CHAMPS)} »")
        # La ligne 1 est l'en-tête : les données commencent à la ligne 2
        for numero, ligne in enumerate(lecteur, start=2):
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


def ecrire_csv(chemin, colis):
    """Écrit les colis dans le fichier (écrase son contenu)."""
    with open(chemin, "w", newline="", encoding="utf-8") as fichier:
        ecrivain = csv.writer(fichier, delimiter=";")
        ecrivain.writerow(CHAMPS)
        for c in colis:
            ecrivain.writerow((c.identifiant, c.poids, c.valeur, c.priorite, c.destination))
