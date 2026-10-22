"""Saisies clavier robustes pour l'interface.

Chaque fonction redemande la saisie tant qu'elle est invalide (texte au lieu
d'un nombre, valeur hors bornes...) : une erreur de frappe ne fait jamais
planter le programme. Si l'entrée standard est fermée (Ctrl-D), l'exception
Abandon est levée pour que l'interface se termine proprement.
"""


class Abandon(Exception):
    """L'utilisateur a fermé l'entrée standard (Ctrl-D) : on quitte proprement."""


def lire_texte(message, defaut=None):
    """Lit une ligne de texte. Une saisie vide renvoie ``defaut`` s'il est fourni,
    sinon la question est reposée."""
    while True:
        try:
            texte = input(message).strip()
        except EOFError:
            raise Abandon from None
        if texte:
            return texte
        if defaut is not None:
            return defaut
        print("  Saisie obligatoire.")


def lire_entier(message, minimum=None, maximum=None, defaut=None):
    """Lit un entier compris entre ``minimum`` et ``maximum`` (bornes incluses)."""
    while True:
        texte = lire_texte(message, defaut="" if defaut is not None else None)
        if texte == "":
            return defaut
        try:
            valeur = int(texte)
        except ValueError:
            print("  Veuillez saisir un nombre entier.")
            continue
        if minimum is not None and valeur < minimum:
            print(f"  La valeur doit être supérieure ou égale à {minimum}.")
        elif maximum is not None and valeur > maximum:
            print(f"  La valeur doit être inférieure ou égale à {maximum}.")
        else:
            return valeur


def lire_reel(message, minimum=None, defaut=None):
    """Lit un nombre décimal (le point ou la virgule sont acceptés)."""
    while True:
        texte = lire_texte(message, defaut="" if defaut is not None else None)
        if texte == "":
            return defaut
        try:
            valeur = float(texte.replace(",", "."))
        except ValueError:
            print("  Veuillez saisir un nombre (par exemple 1 ou 0,5).")
            continue
        if minimum is not None and valeur < minimum:
            print(f"  La valeur doit être supérieure ou égale à {minimum:g}.")
        else:
            return valeur


def lire_oui_non(message, defaut=False):
    """Pose une question fermée. Entrée seule : réponse par défaut."""
    suffixe = " [O/n] : " if defaut else " [o/N] : "
    while True:
        texte = lire_texte(message + suffixe, defaut="").lower()
        if texte == "":
            return defaut
        if texte in ("o", "oui"):
            return True
        if texte in ("n", "non"):
            return False
        print("  Répondre par o (oui) ou n (non).")
