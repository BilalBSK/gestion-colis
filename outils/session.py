"""Exécute un script Python interactif en affichant les saisies lues au clavier.

Quand l'entrée standard est redirigée (fichier, tube), le terminal n'affiche
pas ce qui est « tapé ». Ce lanceur remplace input() par une version qui
réécrit chaque saisie après la question, entre deux marqueurs que
outils/capture.py met en gras. Le programme lui-même n'est pas modifié.

Usage :  python3 outils/session.py src/main.py < saisies.txt
"""

import builtins
import os
import runpy
import sys

DEBUT_SAISIE, FIN_SAISIE = "\x02", "\x03"


def input_avec_echo(message=""):
    print(message, end="", flush=True)
    ligne = sys.stdin.readline()
    if not ligne:                      # fin de l'entrée : comme un Ctrl-D
        print(f"{DEBUT_SAISIE}^D{FIN_SAISIE}")
        raise EOFError
    saisie = ligne.rstrip("\n")
    affiche = saisie if saisie else "(Entrée)"   # rend visible une validation sans texte
    print(f"{DEBUT_SAISIE}{affiche}{FIN_SAISIE}")
    return saisie


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    script = sys.argv[1]
    sys.argv = sys.argv[1:]
    sys.path.insert(0, os.path.dirname(os.path.abspath(script)))
    builtins.input = input_avec_echo
    runpy.run_path(script, run_name="__main__")


if __name__ == "__main__":
    main()
