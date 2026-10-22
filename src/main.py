"""Interface en ligne de commande : gestion des livraisons.

Lancement, depuis la racine du projet :  python3 src/main.py

Au démarrage, les colis d'exemple du sujet (donnees/colis_exemple.csv) sont
chargés pour pouvoir tester immédiatement toutes les fonctionnalités.
"""

import os
import time

from affichage import ENTETE, SEPARATEUR, ligne, page
from chargement import glouton, sac_a_dos_dp
from colis import PRIORITE_MAX, PRIORITE_MIN, Colis
from generateur import NIVEAUX, generer_colis
from gestion import GestionColis
from saisie import Abandon, lire_entier, lire_oui_non, lire_texte
from stockage import ecrire_csv

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FICHIER_EXEMPLE = os.path.join(RACINE, "donnees", "colis_exemple.csv")
FICHIER_SAUVEGARDE = os.path.join(RACINE, "donnees", "sauvegarde.csv")
TAILLE_PAGE = 20
CAPACITE_PAR_DEFAUT = 50          # exemple du sujet : camion de 50 kg
CASES_AVANT_CONFIRMATION = 50_000_000   # au-delà, le calcul exact prend plusieurs secondes

MENU = """
===== GESTION DES LIVRAISONS =====

1. Afficher les colis
2. Ajouter un colis
3. Rechercher un colis
4. Organiser les colis
5. Préparer un camion
6. Afficher le chargement
7. Afficher les statistiques
8. Générer des colis (100 à 100 000)
9. Charger / enregistrer un fichier CSV
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
        self.chargement = None       # dernier chargement calculé (option 6)

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
            8: self.generer_colis,
            9: self.gerer_fichier,
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
        print("--- Préparer un camion ---")
        if len(self.gestion) == 0:
            print("  Aucun colis à charger.")
            return
        capacite = lire_entier(f"Capacité du camion en kg [{CAPACITE_PAR_DEFAUT}] : ",
                               minimum=0, defaut=CAPACITE_PAR_DEFAUT)
        colis = self.gestion.lister()
        # Coût de la programmation dynamique : (nombre de colis) x (capacité + 1) cases
        cases = len(colis) * (capacite + 1)
        if cases > CASES_AVANT_CONFIRMATION:
            print(f"  Attention : {len(colis)} colis x {capacite + 1} capacités = {cases:,} cases "
                  f"(environ {cases / 1e6:.0f} Mo).".replace(",", " "))
            if not lire_oui_non("  Le calcul exact peut prendre plusieurs secondes. Continuer ?"):
                return
        debut = time.perf_counter()
        optimal = sac_a_dos_dp(colis, capacite)
        duree_dp = time.perf_counter() - debut
        debut = time.perf_counter()
        approche = glouton(colis, capacite)
        duree_glouton = time.perf_counter() - debut

        self.chargement = optimal
        print(f"\n  Chargement optimal (programmation dynamique, {formater_duree(duree_dp)}) :")
        print(f"    {len(optimal.colis)} colis, {optimal.poids_total} / {capacite} kg, "
              f"valeur totale {optimal.valeur_totale}")
        ecart = optimal.score - approche.score
        print(f"  Pour comparaison, glouton ({formater_duree(duree_glouton)}) : "
              f"{len(approche.colis)} colis, {approche.poids_total} kg, valeur {approche.valeur_totale}"
              + (f"  -> {ecart} de moins que l'optimum" if ecart else "  -> identique ici"))
        print("  Option 6 : afficher le détail du chargement.")

    def afficher_chargement(self):
        print("--- Chargement du camion ---")
        ch = self.chargement
        if ch is None:
            print("  Aucun camion préparé : utilisez d'abord l'option 5.")
            return
        print(f"Méthode            : {ch.methode}")
        print(f"Colis chargés      : {len(ch.colis)}")
        print(f"Poids total        : {ch.poids_total} / {ch.capacite} kg "
              f"(remplissage {100 * ch.taux_remplissage:.1f} %)")
        print(f"Valeur totale      : {ch.valeur_totale}\n")
        self.afficher_par_pages(ch.colis)

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

    def generer_colis(self):
        print("--- Générer des colis ---")
        for niveau, n in NIVEAUX.items():
            print(f"{niveau}. Niveau {niveau} : {n:>7} colis")
        n = NIVEAUX[lire_entier("Niveau : ", 1, len(NIVEAUX))]
        remplacer = lire_oui_non("Remplacer la collection actuelle ?", defaut=True)
        if remplacer:
            self.gestion = GestionColis()
            self.chargement = None
        # Les nouveaux identifiants commencent après le plus grand existant : aucun doublon
        debut = time.perf_counter()
        for colis in generer_colis(n, identifiant_depart=self.gestion.prochain_identifiant()):
            self.gestion.ajouter(colis)
        duree = time.perf_counter() - debut
        print(f"  {n} colis générés et ajoutés en {formater_duree(duree)}. "
              f"La collection contient {len(self.gestion)} colis.")

    def gerer_fichier(self):
        print("--- Fichier CSV ---")
        choix = lire_entier("1. Charger un fichier  2. Enregistrer la collection : ", 1, 2)
        if choix == 1:
            chemin = lire_texte(f"Fichier à charger [{os.path.relpath(FICHIER_EXEMPLE, RACINE)}] : ",
                                defaut=FICHIER_EXEMPLE)
            try:
                debut = time.perf_counter()
                nouvelle = GestionColis.depuis_csv(os.path.join(RACINE, chemin))
            except FileNotFoundError:
                print(f"  Erreur : fichier introuvable ({chemin}). La collection n'est pas modifiée.")
                return
            except (OSError, ValueError) as erreur:
                # Un fichier invalide ne modifie pas la collection actuelle
                print(f"  Erreur : {erreur}. La collection n'est pas modifiée.")
                return
            self.gestion = nouvelle
            self.chargement = None       # l'ancien chargement ne correspond plus à la collection
            print(f"  {len(nouvelle)} colis chargés en {formater_duree(time.perf_counter() - debut)}.")
        else:
            chemin = lire_texte(f"Fichier de destination [{os.path.relpath(FICHIER_SAUVEGARDE, RACINE)}] : ",
                                defaut=FICHIER_SAUVEGARDE)
            try:
                debut = time.perf_counter()
                ecrire_csv(os.path.join(RACINE, chemin), self.gestion)
            except OSError as erreur:
                print(f"  Erreur : {erreur}")
                return
            print(f"  {len(self.gestion)} colis enregistrés en {formater_duree(time.perf_counter() - debut)}.")


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
