"""Mise en forme des colis sous forme de tableau texte.

L'affichage de n colis coûte O(n) : chaque colis doit être mis en forme.
Pour une grande collection, l'interface n'affiche qu'une page à la fois
(paramètre ``limite``) : afficher 100 000 lignes dans un terminal prendrait
plusieurs secondes et serait illisible.
"""

LARGEURS = (8, 10, 8, 9)  # Id, Poids, Valeur, Priorité (la destination suit)

ENTETE = (f"{'Id':>{LARGEURS[0]}} | {'Poids (kg)':>{LARGEURS[1]}} | "
          f"{'Valeur':>{LARGEURS[2]}} | {'Priorité':>{LARGEURS[3]}} | Destination")
SEPARATEUR = "-" * (len(ENTETE) + 4)


def ligne(colis):
    """Une ligne de tableau pour un colis. O(1)."""
    return (f"{colis.identifiant:>{LARGEURS[0]}} | {colis.poids:>{LARGEURS[1]}} | "
            f"{colis.valeur:>{LARGEURS[2]}} | {colis.priorite:>{LARGEURS[3]}} | {colis.destination}")


def tableau(colis, limite=None):
    """Lignes du tableau (en-tête compris) pour une séquence de colis.

    Si ``limite`` est donnée, seuls les ``limite`` premiers colis sont mis en
    forme, suivis d'une ligne indiquant combien de colis ne sont pas affichés :
    O(min(n, limite)) au lieu de O(n).
    """
    total = len(colis)
    if total == 0:
        return ["(aucun colis)"]
    nombre = total if limite is None else min(limite, total)
    lignes = [ENTETE, SEPARATEUR]
    lignes.extend(ligne(colis[i]) for i in range(nombre))
    if nombre < total:
        lignes.append(f"... {total - nombre} autre(s) colis non affiché(s) sur {total}")
    return lignes
