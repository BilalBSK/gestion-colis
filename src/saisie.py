"""Saisies au clavier.

Chaque fonction repose la question tant que la réponse n'est pas valide : je
ne voulais pas qu'une faute de frappe fasse planter le programme. Ctrl-D lève
Abandon, que le menu attrape pour se fermer proprement.
"""


class Abandon(Exception):
    """Levée quand l'entrée est fermée (Ctrl-D)."""


def lire_texte(message, defaut=None):
    """Lit une ligne. Si elle est vide : renvoie defaut s'il existe, sinon redemande."""
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
    """Lit un entier entre minimum et maximum (inclus)."""
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
    """Lit un nombre décimal, avec un point ou une virgule."""
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
    """Question oui / non ; Entrée seule donne la réponse par défaut."""
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
