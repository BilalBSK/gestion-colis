"""Tests de l'étape 8 : élagage par dominance (optimisation exacte du chargement)."""

import os
import random
import sys
import unittest

RACINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(RACINE, "src"))

from chargement import (elaguer, fabrique_utilite, force_brute, nombre_candidats,  # noqa: E402
                        sac_a_dos_dp, utilite_valeur)
from colis import Colis  # noqa: E402
from generateur import generer_colis  # noqa: E402


def peu_de_poids_differents(rng, n):
    """Beaucoup de colis pour peu de poids différents : l'élagage a beaucoup à écarter."""
    return [Colis(i, rng.randint(1, 4), rng.randint(0, 30), rng.randint(1, 5), "X") for i in range(n)]


class TestElagage(unittest.TestCase):
    def test_garde_les_meilleurs_de_chaque_poids(self):
        colis = [Colis(i, 3, v, 1, "X") for i, v in enumerate([5, 9, 1, 7, 3])]   # 5 colis de 3 kg
        gardes = elaguer(colis, 7, utilite_valeur)                                 # 7 // 3 = 2 places
        self.assertEqual(sorted(c.valeur for c in gardes), [7, 9])

    def test_ecarte_trop_lourds_et_sans_valeur(self):
        colis = [Colis(1, 50, 100, 1, "X"), Colis(2, 1, 0, 1, "X"), Colis(3, 1, 4, 1, "X")]
        self.assertEqual([c.identifiant for c in elaguer(colis, 10, utilite_valeur)], [3])

    def test_borne_independante_de_n(self):
        borne = sum(100 // p for p in range(1, 31))
        for n in (1_000, 10_000, 100_000):
            gardes = elaguer(generer_colis(n), 100, utilite_valeur)
            self.assertLessEqual(len(gardes), borne)

    def test_nombre_candidats_sans_tri(self):
        for n, w in ((100, 50), (10_000, 1_000), (5_000, 37)):
            colis = generer_colis(n, graine=n)         # toutes les valeurs sont > 0
            self.assertEqual(nombre_candidats(colis, w), len(elaguer(colis, w, utilite_valeur)))


class TestOptimumConserve(unittest.TestCase):
    """L'élagage ne doit JAMAIS changer la valeur optimale."""

    def test_contre_force_brute_pour_les_trois_regles(self):
        rng = random.Random(11)
        for _ in range(300):
            colis = peu_de_poids_differents(rng, rng.randint(0, 12))
            capacite = rng.randint(0, 20)
            for regle in ("valeur", "ponderee", "stricte"):
                u = fabrique_utilite(regle, colis, alpha=1)
                attendu = force_brute(colis, capacite, u).score
                self.assertAlmostEqual(sac_a_dos_dp(colis, capacite, u, avec_elagage=True).score, attendu)
                self.assertAlmostEqual(sac_a_dos_dp(colis, capacite, u, avec_elagage=False).score, attendu)

    def test_avec_et_sans_elagage_sur_de_grandes_instances(self):
        rng = random.Random(3)
        for _ in range(10):
            colis = peu_de_poids_differents(rng, 3_000)
            capacite = rng.randint(10, 300)
            avec = sac_a_dos_dp(colis, capacite, avec_elagage=True)
            sans = sac_a_dos_dp(colis, capacite, avec_elagage=False)
            self.assertEqual(avec.score, sans.score)
            self.assertLessEqual(avec.poids_total, capacite)
            self.assertLess(avec.candidats, sans.candidats)

    def test_niveau_4_du_sujet(self):
        colis = generer_colis(100_000)
        avec = sac_a_dos_dp(colis, 300, avec_elagage=True)
        sans = sac_a_dos_dp(colis, 300, avec_elagage=False)
        self.assertEqual(avec.score, sans.score)
        self.assertLessEqual(avec.candidats, sum(300 // p for p in range(1, 31)))


if __name__ == "__main__":
    unittest.main()
