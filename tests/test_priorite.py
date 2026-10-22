"""Tests de l'étape 7 : prise en compte de la priorité dans le chargement."""

import itertools
import os
import random
import subprocess
import sys
import unittest

RACINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(RACINE, "src"))

from chargement import fabrique_utilite, force_brute, glouton, preparer_camion, sac_a_dos_dp  # noqa: E402
from colis import Colis  # noqa: E402
from stockage import lire_csv  # noqa: E402

# Colis A, B, C, D de la partie 6.1 du sujet (identifiants 1 à 4) : priorités 5, 1, 4, 3
SUJET = lire_csv(os.path.join(RACINE, "donnees", "colis_camion.csv"))
A, B, C, D = SUJET


def noms(chargement):
    return "".join(sorted("ABCD"[c.identifiant - 1] for c in chargement.colis))


def aleatoires(rng, n):
    return [Colis(i, rng.randint(1, 15), rng.randint(0, 60), rng.randint(1, 5), "X") for i in range(n)]


class TestReglePonderee(unittest.TestCase):
    def test_utilites_du_sujet(self):
        u = fabrique_utilite("ponderee", alpha=1)
        self.assertEqual([u(c) for c in SUJET], [40, 25, 31.5, 21])   # A x 2, B x 1, C x 1,75, D x 1,5

    def test_exemple_6_1_capacite_14(self):
        ch = preparer_camion(SUJET, 14, "ponderee", alpha=1)
        self.assertEqual(noms(ch), "AC")                 # B (priorité 1) est écarté au profit de C (priorité 4)
        self.assertAlmostEqual(ch.score, 71.5)
        self.assertEqual((ch.valeur_totale, ch.poids_total), (38, 13))
        self.assertAlmostEqual(ch.priorite_moyenne, 4.5)

    def test_alpha_nul_redonne_la_regle_valeur(self):
        self.assertEqual(noms(preparer_camion(SUJET, 14, "ponderee", alpha=0)), "AB")

    def test_seuil_de_bascule_de_alpha(self):
        # A+B vaut 45 + 20 alpha, A+C vaut 38 + 33,5 alpha : bascule pour alpha = 7 / 13,5 ~ 0,52
        self.assertEqual(noms(preparer_camion(SUJET, 14, "ponderee", alpha=0.5)), "AB")
        self.assertEqual(noms(preparer_camion(SUJET, 14, "ponderee", alpha=0.6)), "AC")

    def test_alpha_negatif_refuse(self):
        with self.assertRaises(ValueError):
            fabrique_utilite("ponderee", alpha=-1)


class TestRegleStricte(unittest.TestCase):
    def test_exemple_6_1_capacite_14(self):
        self.assertEqual(noms(preparer_camion(SUJET, 14, "stricte")), "AC")

    def test_un_colis_prioritaire_passe_avant_des_colis_de_valeur(self):
        colis = [Colis(1, 10, 1, 5, "X"), Colis(2, 5, 100, 1, "X"), Colis(3, 5, 100, 1, "X")]
        self.assertEqual([c.identifiant for c in preparer_camion(colis, 10, "stricte").colis], [1])
        self.assertEqual([c.identifiant for c in preparer_camion(colis, 10, "ponderee").colis], [2, 3])
        self.assertEqual([c.identifiant for c in preparer_camion(colis, 10, "valeur").colis], [2, 3])

    def test_ordre_lexicographique_verifie_par_enumeration(self):
        """Définition directe, sans passer par la formule : parmi les chargements possibles, on
        compare les vecteurs (somme des valeur+1 en priorité 5, ..., en priorité 1)."""
        rng = random.Random(4)
        for _ in range(150):
            colis = aleatoires(rng, rng.randint(1, 9))
            capacite = rng.randint(0, 40)

            def vecteur(selection):
                return tuple(sum(c.valeur + 1 for c in selection if c.priorite == p) for p in (5, 4, 3, 2, 1))

            meilleur = max(vecteur(s) for k in range(len(colis) + 1)
                           for s in itertools.combinations(colis, k)
                           if sum(c.poids for c in s) <= capacite)
            self.assertEqual(vecteur(preparer_camion(colis, capacite, "stricte").colis), meilleur)


class TestOptimaliteAvecPriorite(unittest.TestCase):
    def test_dp_egale_force_brute_pour_toutes_les_regles(self):
        rng = random.Random(2026)
        for _ in range(300):
            colis = aleatoires(rng, rng.randint(0, 11))
            capacite = rng.randint(0, 50)
            for regle in ("valeur", "ponderee", "stricte"):
                u = fabrique_utilite(regle, colis, alpha=rng.choice([0, 0.5, 1, 2, 5]))
                attendu = force_brute(colis, capacite, u).score
                dp = sac_a_dos_dp(colis, capacite, u)
                self.assertAlmostEqual(dp.score, attendu, places=6)
                self.assertLessEqual(dp.poids_total, capacite)
                self.assertLessEqual(glouton(colis, capacite, u).score, attendu + 1e-9)

    def test_plus_alpha_est_grand_plus_la_priorite_moyenne_augmente(self):
        colis = aleatoires(random.Random(8), 300)
        moyennes = [preparer_camion(colis, 200, "ponderee", alpha=a).priorite_moyenne for a in (0, 1, 3, 10)]
        self.assertEqual(moyennes, sorted(moyennes))

    def test_regle_et_methode_inconnues(self):
        with self.assertRaises(ValueError):
            fabrique_utilite("hasard")
        with self.assertRaises(ValueError):
            preparer_camion(SUJET, 10, methode="magie")

    def test_description_et_repartition(self):
        ch = preparer_camion(SUJET, 14, "ponderee", alpha=1)
        self.assertEqual(ch.regle, "valeur pondérée par la priorité (alpha = 1)")
        self.assertEqual(ch.par_priorite, {5: 1, 4: 1, 3: 0, 2: 0, 1: 0})


class TestMenuPriorite(unittest.TestCase):
    def session(self, saisies):
        r = subprocess.run([sys.executable, os.path.join(RACINE, "src", "main.py")], input=saisies,
                           text=True, capture_output=True, timeout=60,
                           env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        return r.stdout + r.stderr

    def test_regle_ponderee_par_defaut(self):
        sortie = self.session("9\n1\ndonnees/colis_camion.csv\n5\n14\n\n\n6\n0\n")
        self.assertIn("Règle : valeur pondérée par la priorité (alpha = 1)", sortie)
        self.assertIn("2 colis, 13 / 14 kg, valeur totale 38, priorité moyenne 4.50", sortie)
        self.assertIn("la priorité coûte 7 de valeur et fait passer la priorité moyenne de 3.00 à 4.50", sortie)
        self.assertIn("p5 : 1, p4 : 1, p3 : 0, p2 : 0, p1 : 0", sortie)

    def test_alpha_avec_virgule_et_saisie_invalide(self):
        sortie = self.session("9\n1\ndonnees/colis_camion.csv\n5\n14\n2\nbeaucoup\n-1\n0,5\n0\n")
        self.assertIn("Veuillez saisir un nombre", sortie)
        self.assertIn("La valeur doit être supérieure ou égale à 0.", sortie)
        self.assertIn("(alpha = 0.5)", sortie)
        self.assertIn("la priorité ne change pas le chargement ici", sortie)

    def test_regle_stricte(self):
        sortie = self.session("9\n1\ndonnees/colis_camion.csv\n5\n14\n3\n0\n")
        self.assertIn("Règle : priorité stricte", sortie)
        self.assertIn("valeur totale 38", sortie)


if __name__ == "__main__":
    unittest.main()
