"""Programme principal : menu de gestion des livraisons.

Lancement depuis la racine du projet :  python3 src/main.py

Je charge les 5 colis d'exemple du sujet (donnees/colis_exemple.csv) au
démarrage, pour pouvoir tester chaque option tout de suite.
"""

import os
import time

from affichage import ENTETE, SEPARATEUR, ligne, page
from chargement import ALPHA_PAR_DEFAUT, description_regle, nombre_candidats
from chargement import preparer_camion as calculer_chargement
from colis import PRIORITE_MAX, PRIORITE_MIN, Colis
from generateur import NIVEAUX, generer_colis
from gestion import GestionColis
from saisie import Abandon, lire_entier, lire_oui_non, lire_reel, lire_texte

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FICHIER_EXEMPLE = os.path.join(RACINE, "donnees", "colis_exemple.csv")
TAILLE_PAGE = 20
CAPACITE_PAR_DEFAUT = 50                 # l'exemple du sujet
CASES_AVANT_CONFIRMATION = 50_000_000    # au-delà, le calcul prend plusieurs secondes

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
9. Charger un fichier de colis
0. Quitter
"""

# Option 4 : (libellé, critère de GestionColis.trier, algorithme utilisé)
TRIS = (
    ("Par poids", "poids", "tri fusion"),
    ("Par valeur", "valeur", "tri fusion"),
    ("Par priorité", "priorite", "tri par comptage"),
)


def formater_duree(secondes):
    if secondes < 1e-3:
        return f"{secondes * 1e6:.1f} µs"
    if secondes < 1:
        return f"{secondes * 1e3:.1f} ms"
    return f"{secondes:.2f} s"


def resume(chargement):
    return (f"{len(chargement.colis)} colis, {chargement.poids_total} / {chargement.capacite} kg, "
            f"valeur totale {chargement.valeur_totale}, priorité moyenne {chargement.priorite_moyenne:.2f}")


class Application:
    def __init__(self, gestion):
        self.gestion = gestion
        self.chargement = None       # dernier camion préparé, affiché par l'option 6

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
            9: self.charger_fichier,
        }
        while True:
            print(MENU)
            try:
                choix = lire_entier("Choix : ", 0, len(actions))
                if choix == 0:
                    break
                print()
                actions[choix]()
            except Abandon:              # Ctrl-D
                print()
                break
            except KeyboardInterrupt:    # Ctrl-C : j'annule seulement l'action en cours
                print("\n  Opération annulée.")
        print("Au revoir.")

    def afficher_par_pages(self, colis):
        """Affiche 20 colis à la fois : le coût d'une page ne dépend pas du nombre total."""
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

    def afficher_colis(self):
        print(f"--- Colis enregistrés ({len(self.gestion)}) ---")
        self.afficher_par_pages(self.gestion.lister())

    def ajouter_colis(self):
        print("--- Ajouter un colis ---")
        propose = self.gestion.prochain_identifiant()
        identifiant = lire_entier(f"Identifiant [{propose}] : ", minimum=0, defaut=propose)
        # je vérifie tout de suite que l'identifiant est libre, pour ne pas faire tout saisir pour rien
        if self.gestion.rechercher(identifiant) is not None:
            print(f"  Erreur : un colis d'identifiant {identifiant} existe déjà.")
            return
        poids = lire_entier("Poids (kg) : ", minimum=1)
        valeur = lire_entier("Valeur : ", minimum=0)
        priorite = lire_entier(f"Priorité ({PRIORITE_MIN} = faible ... {PRIORITE_MAX} = forte) : ",
                               PRIORITE_MIN, PRIORITE_MAX)
        destination = lire_texte("Destination : ")
        self.gestion.ajouter(Colis(identifiant, poids, valeur, priorite, destination))
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
        print(f"  (recherche en {formater_duree(duree)})")

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
        alpha = lire_reel("Importance de la priorité (0 = valeur seule, 1 = une priorité 5 compte double) [1] : ",
                          minimum=0, defaut=ALPHA_PAR_DEFAUT)
        colis = self.gestion.lister()

        # J'estime la taille du calcul avant de le lancer : colis gardés x (capacité + 1)
        # cases, deux fois si je calcule aussi le chargement sans priorité pour comparer
        calculs = 1 if alpha == 0 else 2
        candidats = nombre_candidats(colis, capacite)
        cases = candidats * (capacite + 1) * calculs
        if cases > CASES_AVANT_CONFIRMATION:
            print(f"  Attention : {calculs} x {candidats} colis x {capacite + 1} capacités = "
                  f"{cases:,} cases (environ {cases / calculs / 1e6:.0f} Mo).".replace(",", " "))
            if not lire_oui_non("  Le calcul peut prendre plusieurs secondes. Continuer ?"):
                return

        debut = time.perf_counter()
        optimal = calculer_chargement(colis, capacite, alpha, "dp")
        duree_dp = time.perf_counter() - debut
        debut = time.perf_counter()
        approche = calculer_chargement(colis, capacite, alpha, "glouton")
        duree_glouton = time.perf_counter() - debut
        self.chargement = optimal

        print(f"\n  Règle : {description_regle(alpha)}")
        print(f"  Chargement optimal ({optimal.methode}, {formater_duree(duree_dp)}, "
              f"{optimal.candidats} colis gardés sur {len(colis)}) :")
        print(f"    {resume(optimal)}")
        if alpha > 0:
            # j'affiche ce que la priorité a coûté par rapport au chargement « valeur seule »
            reference = calculer_chargement(colis, capacite, 0, "dp")
            print(f"  Sans tenir compte de la priorité :\n    {resume(reference)}")
            cout = reference.valeur_totale - optimal.valeur_totale
            if cout == 0 and optimal.priorite_moyenne == reference.priorite_moyenne:
                print("    -> même chargement, la priorité ne change rien ici")
            else:
                print(f"    -> la priorité coûte {cout} de valeur, la priorité moyenne passe "
                      f"de {reference.priorite_moyenne:.2f} à {optimal.priorite_moyenne:.2f}")
        verdict = "même résultat" if approche.score == optimal.score else "moins bien que l'optimum"
        print(f"  Glouton ({formater_duree(duree_glouton)}) :\n    {resume(approche)}  -> {verdict}")
        print("  Option 6 pour voir le détail du chargement.")

    def afficher_chargement(self):
        print("--- Chargement du camion ---")
        ch = self.chargement
        if ch is None:
            print("  Aucun camion préparé : utilisez d'abord l'option 5.")
            return
        print(f"{'Règle':<19}: {description_regle(ch.alpha)}")
        print(f"{'Colis chargés':<19}: {len(ch.colis)}")
        print(f"{'Poids total':<19}: {ch.poids_total} / {ch.capacite} kg "
              f"(remplissage {100 * ch.taux_remplissage:.1f} %)")
        print(f"{'Valeur totale':<19}: {ch.valeur_totale}")
        print(f"{'Priorité moyenne':<19}: {ch.priorite_moyenne:.2f}")
        print(f"{'Colis par priorité':<19}: "
              + ", ".join(f"p{p} : {nb}" for p, nb in ch.par_priorite.items()) + "\n")
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
        print(f"{'Colis par priorité':<20}: "
              + ", ".join(f"p{p} : {nb}" for p, nb in s["par_priorite"].items()))
        print(f"{'Par destination':<20}:")
        for destination, (nombre, poids, valeur) in s["par_destination"].items():
            print(f"  {destination:<12} {nombre:>7} colis {poids:>9} kg   valeur {valeur:>9}")
        if self.chargement is not None:
            ch = self.chargement
            print(f"{'Dernier camion':<20}: {len(ch.colis)} colis, {ch.poids_total} / {ch.capacite} kg, "
                  f"valeur {ch.valeur_totale}")

    def generer_colis(self):
        print("--- Générer des colis ---")
        for niveau, n in NIVEAUX.items():
            print(f"{niveau}. Niveau {niveau} : {n:>7} colis")
        n = NIVEAUX[lire_entier("Niveau : ", 1, len(NIVEAUX))]
        if lire_oui_non("Remplacer la collection actuelle ?", defaut=True):
            self.gestion = GestionColis()
            self.chargement = None
        # les identifiants générés commencent après le plus grand existant : pas de doublon
        debut = time.perf_counter()
        for colis in generer_colis(n, identifiant_depart=self.gestion.prochain_identifiant()):
            self.gestion.ajouter(colis)
        duree = time.perf_counter() - debut
        print(f"  {n} colis générés en {formater_duree(duree)}. "
              f"La collection contient {len(self.gestion)} colis.")

    def charger_fichier(self):
        print("--- Charger un fichier de colis ---")
        defaut = os.path.relpath(FICHIER_EXEMPLE, RACINE)
        chemin = lire_texte(f"Fichier CSV [{defaut}] : ", defaut=defaut)
        try:
            nouvelle = GestionColis.depuis_csv(os.path.join(RACINE, chemin))
        except FileNotFoundError:
            print(f"  Erreur : fichier introuvable ({chemin}). La collection n'est pas modifiée.")
            return
        except (OSError, ValueError) as erreur:
            print(f"  Erreur : {erreur}. La collection n'est pas modifiée.")
            return
        self.gestion = nouvelle
        self.chargement = None       # l'ancien camion ne correspond plus à ces colis
        print(f"  {len(nouvelle)} colis chargés depuis {chemin}.")


def main():
    try:
        gestion = GestionColis.depuis_csv(FICHIER_EXEMPLE)
        print(f"{len(gestion)} colis chargés depuis donnees/colis_exemple.csv")
    except (OSError, ValueError) as erreur:
        print(f"Impossible de charger les colis d'exemple ({erreur}), collection vide.")
        gestion = GestionColis()
    Application(gestion).executer()


if __name__ == "__main__":
    main()
