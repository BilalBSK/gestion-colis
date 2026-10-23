"""Affichage des colis en tableau.

Avec 100 000 colis, je n'affiche pas tout d'un coup : le menu montre une page
de 20 colis, et je ne mets en forme que les colis de cette page.
"""

LARGEURS = (8, 10, 8, 9)  # Id, Poids, Valeur, Priorité (la destination suit)

ENTETE = (f"{'Id':>{LARGEURS[0]}} | {'Poids (kg)':>{LARGEURS[1]}} | "
          f"{'Valeur':>{LARGEURS[2]}} | {'Priorité':>{LARGEURS[3]}} | Destination")
SEPARATEUR = "-" * (len(ENTETE) + 4)


def ligne(colis):
    return (f"{colis.identifiant:>{LARGEURS[0]}} | {colis.poids:>{LARGEURS[1]}} | "
            f"{colis.valeur:>{LARGEURS[2]}} | {colis.priorite:>{LARGEURS[3]}} | {colis.destination}")


def page(colis, numero, taille):
    """Lignes de la page numero (la première page est la page 0).

    Le coût dépend de la taille de la page, pas du nombre total de colis.
    """
    total = len(colis)
    debut = numero * taille
    fin = min(debut + taille, total)
    lignes = [ENTETE, SEPARATEUR]
    lignes.extend(ligne(colis[i]) for i in range(debut, fin))
    lignes.append(f"Colis {debut + 1} à {fin} sur {total}")
    return lignes
