"""Interface en ligne de commande : gestion des livraisons.

Lancement, depuis la racine du projet :  python3 src/main.py

Au démarrage, les colis d'exemple du sujet (donnees/colis_exemple.csv) sont
chargés pour pouvoir tester immédiatement toutes les fonctionnalités.
"""

import os
import time

from affichage import ENTETE, SEPARATEUR, ligne, page
from colis import PRIORITE_MAX, PRIORITE_MIN, Colis
from gestion import GestionColis
from saisie import Abandon, lire_entier, lire_texte

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FICHIER_EXEMPLE = os.path.join(RACINE, "donnees", "colis_exemple.csv")
TAILLE_PAGE = 20

MENU = """
===== GESTION DES LIVRAISONS =====

1. Afficher les colis
2. Ajouter un colis
3. Rechercher un colis
4. Organiser les colis
5. Préparer un camion
6. Afficher le chargement
7. Afficher les statistiques
0. Quitter
"""

# Option 4 : (libellé, critère passé à GestionColis.trier, algorithme utilisé)
TRIS = (
    ("Par poids", "poids", "tri fusion"),
    ("Par valeur", "valeur", "tri fusion"),
    ("Par priorité", "priorite", "tri par comptage"),
    ("Par priorité, puis par valeur", "priorite_valeur", "tri fusion puis tri par comptage stable"),
)


def formater_duree(secondes):
    """Durée lisible : en µs, ms ou s selon l'ordre de grandeur."""
    if secondes < 1e-3:
        return f"{secondes * 1e6:.1f} µs"
    if secondes < 1:
        return f"{secondes * 1e3:.1f} ms"
    return f"{secondes:.2f} s"


class Application:
    def __init__(self, gestion):
        self.gestion = gestion

    # ------------------------------------------------------------------ #
    # Boucle principale
    # ------------------------------------------------------------------ #
    def executer(self):
        actions = {
            1: self.afficher_colis,
            2: self.ajouter_colis,
            3: self.rechercher_colis,
            4: self.organiser_colis,
            5: self.preparer_camion,
            6: self.afficher_chargement,
            7: self.afficher_statistiques,
        }
        while True:
            print(MENU)
            try:
                choix = lire_entier("Choix : ", 0, len(actions))
                if choix == 0:
                    break
                print()
                actions[choix]()
            except Abandon:          # Ctrl-D : fin de l'entrée standard
                print()
                break
            except KeyboardInterrupt:  # Ctrl-C : on annule l'action en cours
                print("\n  Opération annulée.")
        print("Au revoir.")

    # ------------------------------------------------------------------ #
    # Affichage paginé (utilisé par les options 1 et 4)
    # ------------------------------------------------------------------ #
    def afficher_par_pages(self, colis):
        """Affiche les colis par pages de TAILLE_PAGE : O(TAILLE_PAGE) par page."""
        if not colis:
            print("  (aucun colis)")
            return
        nombre_pages = (len(colis) + TAILLE_PAGE - 1) // TAILLE_PAGE
        for numero in range(nombre_pages):
            print("\n".join(page(colis, numero, TAILLE_PAGE)))
            if numero + 1 < nombre_pages:
                reponse = lire_texte("Entrée : page suivante, q : retour au menu > ", defaut="")
                if reponse.lower() == "q":
                    return

    # ------------------------------------------------------------------ #
    # Options du menu
    # ------------------------------------------------------------------ #
    def afficher_colis(self):
        print(f"--- Colis enregistrés ({len(self.gestion)}) ---")
        self.afficher_par_pages(self.gestion.lister())

    def ajouter_colis(self):
        print("--- Ajouter un colis ---")
        propose = self.gestion.prochain_identifiant()
        identifiant = lire_entier(f"Identifiant [{propose}] : ", minimum=0, defaut=propose)
        # On vérifie l'unicité tout de suite, avant de demander le reste : O(1)
        if self.gestion.rechercher(identifiant) is not None:
            print(f"  Erreur : un colis d'identifiant {identifiant} existe déjà.")
            return
        poids = lire_entier("Poids (kg) : ", minimum=1)
        valeur = lire_entier("Valeur : ", minimum=0)
        priorite = lire_entier(f"Priorité ({PRIORITE_MIN} = faible ... {PRIORITE_MAX} = forte) : ",
                               PRIORITE_MIN, PRIORITE_MAX)
        destination = lire_texte("Destination : ")
        colis = Colis(identifiant, poids, valeur, priorite, destination)
        self.gestion.ajouter(colis)
        print(f"  Colis {identifiant} ajouté. La collection contient {len(self.gestion)} colis.")

    def rechercher_colis(self):
        print("--- Rechercher un colis ---")
        identifiant = lire_entier("Identifiant recherché : ", minimum=0)
        debut = time.perf_counter()
        colis = self.gestion.rechercher(identifiant)
        duree = time.perf_counter() - debut
        if colis is None:
            print(f"  Aucun colis d'identifiant {identifiant}.")
        else:
            print("\n".join((ENTETE, SEPARATEUR, ligne(colis))))
        print(f"  (recherche par table de hachage en {formater_duree(duree)})")

    def organiser_colis(self):
        print("--- Organiser les colis ---")
        for numero, (libelle, _, algorithme) in enumerate(TRIS, start=1):
            print(f"{numero}. {libelle} ({algorithme})")
        _, critere, algorithme = TRIS[lire_entier("Critère : ", 1, len(TRIS)) - 1]
        decroissant = lire_entier("Ordre : 1. croissant  2. décroissant : ", 1, 2) == 2
        debut = time.perf_counter()
        tries = self.gestion.trier(critere, decroissant)
        duree = time.perf_counter() - debut
        print(f"  {len(tries)} colis triés en {formater_duree(duree)} ({algorithme}).\n")
        self.afficher_par_pages(tries)

    def preparer_camion(self):
        print("  Cette fonctionnalité n'est pas encore disponible.")

    def afficher_chargement(self):
        print("  Cette fonctionnalité n'est pas encore disponible.")

    def afficher_statistiques(self):
        s = self.gestion.statistiques()
        print("--- Statistiques ---")
        if s["nombre"] == 0:
            print("  Aucun colis enregistré.")
            return
        print(f"{'Nombre de colis':<20}: {s['nombre']}")
        print(f"{'Poids total':<20}: {s['poids_total']} kg (moyenne {s['poids_moyen']:.2f} kg)")
        print(f"{'Valeur totale':<20}: {s['valeur_totale']} (moyenne {s['valeur_moyenne']:.2f})")
        print(f"{'Colis le plus lourd':<20}: n°{s['plus_lourd'].identifiant} ({s['plus_lourd'].poids} kg)")
        print(f"{'Colis le plus léger':<20}: n°{s['plus_leger'].identifiant} ({s['plus_leger'].poids} kg)")
        print(f"{'Colis le plus cher':<20}: n°{s['plus_precieux'].identifiant} (valeur {s['plus_precieux'].valeur})")
        print(f"{'Colis par priorité':<20}: " +
              ", ".join(f"p{p} : {nb}" for p, nb in s["par_priorite"].items()))
        print(f"{'Par destination':<20}:")
        for destination, (nombre, poids, valeur) in s["par_destination"].items():
            print(f"  {destination:<12} {nombre:>7} colis {poids:>9} kg   valeur {valeur:>9}")


def main():
    try:
        gestion = GestionColis.depuis_csv(FICHIER_EXEMPLE)
        print(f"{len(gestion)} colis chargés depuis donnees/colis_exemple.csv")
    except (OSError, ValueError) as erreur:
        print(f"Impossible de charger les colis d'exemple ({erreur}) : collection vide.")
        gestion = GestionColis()
    Application(gestion).executer()


if __name__ == "__main__":
    main()
