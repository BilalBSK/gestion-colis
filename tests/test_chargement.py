"""Tests de l'étape 6 : chargement optimal du camion (sac à dos 0/1)."""

import os
import random
import subprocess
import sys
import unittest

RACINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(RACINE, "src"))

from chargement import Chargement, force_brute, glouton, sac_a_dos_dp  # noqa: E402
from colis import Colis  # noqa: E402
from generateur import generer_colis  # noqa: E402
from stockage import lire_csv  # noqa: E402

# Colis A, B, C, D de la partie 5.2 du sujet (identifiants 1 à 4)
SUJET = lire_csv(os.path.join(RACINE, "donnees", "colis_camion.csv"))
A, B, C, D = SUJET


def noms(chargement):
    lettres = {1: "A", 2: "B", 3: "C", 4: "D"}
    return "".join(sorted(lettres[c.identifiant] for c in chargement.colis))


def aleatoires(rng, n, poids_max=15):
    return [Colis(i, rng.randint(1, poids_max), rng.randint(0, 60), rng.randint(1, 5), "X")
            for i in range(n)]


class TestExempleDuSujet(unittest.TestCase):
    def test_donnees(self):
        self.assertEqual([(c.poids, c.valeur) for c in SUJET], [(8, 20), (6, 25), (5, 18), (4, 14)])

    def test_capacite_50_tout_est_charge(self):
        ch = sac_a_dos_dp(SUJET, 50)        # 23 kg au total : tout tient
        self.assertEqual(noms(ch), "ABCD")
        self.assertEqual((ch.score, ch.poids_total), (77, 23))

    def test_capacite_14_glouton_se_trompe(self):
        dp, gl = sac_a_dos_dp(SUJET, 14), glouton(SUJET, 14)
        self.assertEqual((noms(dp), dp.score, dp.poids_total), ("AB", 45, 14))
        self.assertEqual((noms(gl), gl.score, gl.poids_total), ("BC", 43, 11))

    def test_capacite_15(self):
        ch = sac_a_dos_dp(SUJET, 15)
        self.assertEqual((noms(ch), ch.score), ("BCD", 57))

    def test_capacites_trop_petites(self):
        self.assertEqual(sac_a_dos_dp(SUJET, 0).colis, [])
        self.assertEqual(sac_a_dos_dp(SUJET, 3).colis, [])          # le plus léger pèse 4 kg
        self.assertEqual(noms(sac_a_dos_dp(SUJET, 4)), "D")

    def test_capacite_invalide(self):
        for capacite in (-1, 2.5, "10"):
            with self.assertRaises(ValueError):
                sac_a_dos_dp(SUJET, capacite)

    def test_colis_trop_lourd_ignore(self):
        lourd = Colis(9, 100, 1000, 1, "X")
        self.assertEqual(noms(sac_a_dos_dp(SUJET + [lourd], 14)), "AB")

    def test_resultat(self):
        ch = sac_a_dos_dp(SUJET, 14)
        self.assertIsInstance(ch, Chargement)
        self.assertEqual(ch.valeur_totale, 45)
        self.assertAlmostEqual(ch.taux_remplissage, 1.0)


class TestOptimalite(unittest.TestCase):
    """La programmation dynamique doit TOUJOURS trouver la même valeur que la force brute."""

    def test_dp_egale_force_brute_sur_500_cas(self):
        rng = random.Random(2026)
        for essai in range(500):
            colis = aleatoires(rng, rng.randint(0, 12))
            capacite = rng.randint(0, 60)
            attendu = force_brute(colis, capacite).score
            dp = sac_a_dos_dp(colis, capacite)
            message = f"essai {essai} : capacité {capacite}, {len(colis)} colis"
            self.assertEqual(dp.score, attendu, message)
            self.assertLessEqual(dp.poids_total, capacite, message)
            self.assertEqual(dp.valeur_totale, dp.score, message)            # sélection cohérente
            self.assertEqual(len({c.identifiant for c in dp.colis}), len(dp.colis), message)  # pas de doublon

    def test_glouton_valide_mais_jamais_meilleur(self):
        rng = random.Random(7)
        echecs = 0
        for _ in range(500):
            colis = aleatoires(rng, rng.randint(1, 12))
            capacite = rng.randint(1, 60)
            optimum = force_brute(colis, capacite).score
            gl = glouton(colis, capacite)
            self.assertLessEqual(gl.poids_total, capacite)
            self.assertLessEqual(gl.score, optimum)
            echecs += gl.score < optimum
        self.assertGreater(echecs, 0)    # le glouton se trompe réellement sur certains cas

    def test_grande_instance(self):
        colis = generer_colis(2_000, graine=1)
        dp, gl = sac_a_dos_dp(colis, 500), glouton(colis, 500)
        self.assertLessEqual(dp.poids_total, 500)
        self.assertGreaterEqual(dp.score, gl.score)

    def test_force_brute_limitee(self):
        with self.assertRaises(ValueError):
            force_brute(aleatoires(random.Random(1), 21), 10)


class TestMenuCamion(unittest.TestCase):
    """Options 5 et 6 du vrai programme."""

    def session(self, saisies):
        r = subprocess.run([sys.executable, os.path.join(RACINE, "src", "main.py")], input=saisies,
                           text=True, capture_output=True, timeout=60,
                           env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        return r.stdout + r.stderr

    def test_afficher_sans_camion(self):
        self.assertIn("utilisez d'abord l'option 5", self.session("6\n0\n"))

    def test_capacite_par_defaut_50_kg(self):
        sortie = self.session("5\n\n1\n0\n")                  # règle 1 : valeur seule
        self.assertIn("5 colis, 30 / 50 kg, valeur totale 110", sortie)

    def test_donnees_du_sujet_20_kg(self):
        sortie = self.session("5\n20\n1\n6\n0\n")
        self.assertIn("3 colis, 19 / 20 kg, valeur totale 80", sortie)
        self.assertIn("4 colis, 18 / 20 kg, valeur totale 70", sortie)          # glouton
        self.assertIn("moins bon que l'optimum", sortie)
        self.assertIn("remplissage 95.0 %", sortie)

    def test_colis_a_b_c_d_14_kg(self):
        sortie = self.session("9\n1\ndonnees/colis_camion.csv\n5\n14\n1\n6\n0\n")
        self.assertIn("2 colis, 14 / 14 kg, valeur totale 45", sortie)
        self.assertIn("2 colis, 11 / 14 kg, valeur totale 43", sortie)          # glouton

    def test_confirmation_pour_un_tres_gros_calcul(self):
        sortie = self.session("8\n4\n\n5\n1000\n1\nn\n6\n0\n")
        self.assertIn("Attention : 1 x 100000 colis x 1001 capacités", sortie)
        self.assertNotIn("Chargement optimal", sortie)
        self.assertIn("utilisez d'abord l'option 5", sortie)


if __name__ == "__main__":
    unittest.main()
