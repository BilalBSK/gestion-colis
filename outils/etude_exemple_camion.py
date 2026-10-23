"""L'exemple A, B, C, D du sujet (partie 5.2).

  tableau [W]  : affiche le tableau complet de la programmation dynamique
                 (une ligne par colis ajouté, une colonne par capacité).
  comparaison  : pour chaque capacité de 0 à 23 kg, compare la programmation
                 dynamique, le glouton et la force brute.

Usage, depuis la racine du projet :
    python3 outils/etude_exemple_camion.py tableau 14
    python3 outils/etude_exemple_camion.py comparaison
"""

import os
import sys

RACINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(RACINE, "src"))

from chargement import force_brute, glouton, sac_a_dos_dp  # noqa: E402
from stockage import lire_csv  # noqa: E402

COLIS = lire_csv(os.path.join(RACINE, "donnees", "colis_camion.csv"))
LETTRE = {1: "A", 2: "B", 3: "C", 4: "D"}


def noms(chargement):
    return "+".join(sorted(LETTRE[c.identifiant] for c in chargement.colis)) or "-"


def tableau(capacite):
    """Même récurrence que sac_a_dos_dp, mais je garde tout le tableau
    T[i][w] = max(T[i-1][w], T[i-1][w - p_i] + v_i) pour pouvoir l'afficher."""
    T = [[0] * (capacite + 1)]
    for c in COLIS:
        precedent = T[-1]
        T.append([max(precedent[w], precedent[w - c.poids] + c.valeur) if w >= c.poids else precedent[w]
                  for w in range(capacite + 1)])
    titres = ["aucun colis"] + [f"+ {LETTRE[c.identifiant]} ({c.poids} kg, {c.valeur})" for c in COLIS]
    print("w (kg)".ljust(20) + "".join(f"{w:>4}" for w in range(capacite + 1)))
    print("-" * (20 + 4 * (capacite + 1)))
    for titre, rangee in zip(titres, T):
        print(titre.ljust(20) + "".join(f"{v:>4}" for v in rangee))
    # remontée : si T[i][w] != T[i-1][w], c'est que le colis i a été pris
    w, pris = capacite, []
    for i in range(len(COLIS), 0, -1):
        if T[i][w] != T[i - 1][w]:
            pris.append(f"{LETTRE[COLIS[i - 1].identifiant]} (w = {w} -> {w - COLIS[i - 1].poids})")
            w -= COLIS[i - 1].poids
    print(f"\nValeur optimale pour {capacite} kg : T[4][{capacite}] = {T[-1][capacite]}")
    print("Remontée des décisions : " + ", ".join(pris))
    print(f"Vérification avec sac_a_dos_dp : {noms(sac_a_dos_dp(COLIS, capacite))}")


def comparaison():
    print(f"{'W (kg)':>6} | {'prog. dynamique':<18} | {'glouton':<18} | {'force brute':<12} | écart")
    print("-" * 74)
    for w in range(0, 24):
        dp, gl, fb = sac_a_dos_dp(COLIS, w), glouton(COLIS, w), force_brute(COLIS, w)
        assert dp.score == fb.score
        ecart = f"glouton -{dp.score - gl.score}" if gl.score < dp.score else ""
        print(f"{w:>6} | {noms(dp):<9}{dp.score:>9} | {noms(gl):<9}{gl.score:>9} | {fb.score:>12} | {ecart}")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "tableau":
        tableau(int(sys.argv[2]) if len(sys.argv) > 2 else 14)
    elif len(sys.argv) == 2 and sys.argv[1] == "comparaison":
        comparaison()
    else:
        sys.exit(__doc__)
