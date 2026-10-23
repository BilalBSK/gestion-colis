"""Tests du camion. Je vérifie que le chargement est optimal, avec et sans priorité,
et que l'élagage ne change pas le résultat."""

import os
import random
import sys
import unittest

RACINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(RACINE, "src"))

from chargement import (elaguer, force_brute, glouton, nombre_candidats,  # noqa: E402
                        preparer_camion, sac_a_dos_dp, utilite, utilite_valeur)
from colis import Colis  # noqa: E402
from generateur import generer_colis  # noqa: E402
from stockage import lire_csv  # noqa: E402

# Colis A, B, C, D du sujet (identifiants 1 à 4), avec les priorités de la partie 6.1
SUJET = lire_csv(os.path.join(RACINE, "donnees", "colis_camion.csv"))


def noms(chargement):
    return "".join(sorted("ABCD"[c.identifiant - 1] for c in chargement.colis))


def aleatoires(rng, n, poids_max=15):
    return [Colis(i, rng.randint(1, poids_max), rng.randint(0, 60), rng.randint(1, 5), "X")
            for i in range(n)]


class TestExempleDuSujet(unittest.TestCase):
    def test_capacite_50_tout_rentre(self):
        ch = sac_a_dos_dp(SUJET, 50)
        self.assertEqual((noms(ch), ch.score, ch.poids_total), ("ABCD", 77, 23))

    def test_capacite_14_le_glouton_se_trompe(self):
        dp, gl = sac_a_dos_dp(SUJET, 14), glouton(SUJET, 14)
        self.assertEqual((noms(dp), dp.score), ("AB", 45))
        self.assertEqual((noms(gl), gl.score), ("BC", 43))

    def test_autres_capacites(self):
        self.assertEqual(noms(sac_a_dos_dp(SUJET, 15)), "BCD")
        self.assertEqual(noms(sac_a_dos_dp(SUJET, 9)), "CD")
        self.assertEqual(sac_a_dos_dp(SUJET, 3).colis, [])      # le plus léger pèse 4 kg
        self.assertEqual(sac_a_dos_dp(SUJET, 0).colis, [])

    def test_capacite_invalide(self):
        for capacite in (-1, 2.5, "10"):
            with self.assertRaises(ValueError):
                sac_a_dos_dp(SUJET, capacite)


class TestOptimalite(unittest.TestCase):
    def test_dp_egale_force_brute(self):
        """Sur 500 petits cas tirés au hasard, la DP doit trouver la même valeur que la force brute."""
        rng = random.Random(2026)
        for essai in range(500):
            colis = aleatoires(rng, rng.randint(0, 12))
            capacite = rng.randint(0, 60)
            alpha = rng.choice([0, 0.5, 1, 3])
            u = utilite(alpha)
            attendu = force_brute(colis, capacite, u).score
            for avec_elagage in (True, False):
                dp = sac_a_dos_dp(colis, capacite, u, avec_elagage)
                msg = f"essai {essai}, capacité {capacite}, alpha {alpha}"
                self.assertAlmostEqual(dp.score, attendu, msg=msg)
                self.assertLessEqual(dp.poids_total, capacite, msg)
                self.assertEqual(len({c.identifiant for c in dp.colis}), len(dp.colis), msg)

    def test_glouton_valide_mais_parfois_moins_bon(self):
        rng = random.Random(7)
        moins_bon = 0
        for _ in range(500):
            colis = aleatoires(rng, rng.randint(1, 12))
            capacite = rng.randint(1, 60)
            optimum = force_brute(colis, capacite).score
            gl = glouton(colis, capacite)
            self.assertLessEqual(gl.poids_total, capacite)
            self.assertLessEqual(gl.score, optimum)
            moins_bon += gl.score < optimum
        self.assertGreater(moins_bon, 0)


class TestPriorite(unittest.TestCase):
    def test_utilites_du_sujet(self):
        u = utilite(1)
        self.assertEqual([u(c) for c in SUJET], [40, 25, 31.5, 21])

    def test_exemple_6_1_capacite_14(self):
        ch = preparer_camion(SUJET, 14, alpha=1)
        self.assertEqual(noms(ch), "AC")          # B (priorité 1) laisse sa place à C (priorité 4)
        self.assertEqual((ch.valeur_totale, ch.poids_total), (38, 13))
        self.assertAlmostEqual(ch.priorite_moyenne, 4.5)

    def test_role_de_alpha(self):
        # A+B vaut 45 + 20 alpha, A+C vaut 38 + 33,5 alpha : A+C gagne dès que alpha > 0,52
        self.assertEqual(noms(preparer_camion(SUJET, 14, alpha=0)), "AB")
        self.assertEqual(noms(preparer_camion(SUJET, 14, alpha=0.5)), "AB")
        self.assertEqual(noms(preparer_camion(SUJET, 14, alpha=0.6)), "AC")

    def test_alpha_negatif_refuse(self):
        with self.assertRaises(ValueError):
            utilite(-1)


class TestElagage(unittest.TestCase):
    def test_garde_les_meilleurs_de_chaque_poids(self):
        colis = [Colis(i, 3, v, 1, "X") for i, v in enumerate([5, 9, 1, 7, 3])]   # 5 colis de 3 kg
        gardes = elaguer(colis, 7, utilite_valeur)                                 # 7 // 3 = 2 places
        self.assertEqual(sorted(c.valeur for c in gardes), [7, 9])

    def test_retire_trop_lourds_et_sans_valeur(self):
        colis = [Colis(1, 50, 100, 1, "X"), Colis(2, 1, 0, 1, "X"), Colis(3, 1, 4, 1, "X")]
        self.assertEqual([c.identifiant for c in elaguer(colis, 10)], [3])

    def test_nombre_de_colis_gardes_borne_quel_que_soit_n(self):
        borne = sum(100 // p for p in range(1, 31))
        for n in (1_000, 100_000):
            colis = generer_colis(n)
            self.assertLessEqual(len(elaguer(colis, 100)), borne)
            self.assertEqual(nombre_candidats(colis, 100), len(elaguer(colis, 100)))

    def test_meme_optimum_avec_et_sans_elagage_sur_100000_colis(self):
        colis = generer_colis(100_000)
        avec = sac_a_dos_dp(colis, 300, avec_elagage=True)
        sans = sac_a_dos_dp(colis, 300, avec_elagage=False)
        self.assertEqual(avec.score, sans.score)
        self.assertLess(avec.candidats, sans.candidats)


if __name__ == "__main__":
    unittest.main()
