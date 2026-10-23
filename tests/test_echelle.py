"""Tests du générateur, puis des opérations aux 4 tailles du sujet (100 à 100 000 colis)."""

import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from colis import PRIORITE_MAX, PRIORITE_MIN  # noqa: E402
from generateur import DESTINATIONS, NIVEAUX, POIDS_MAX, POIDS_MIN, generer_colis  # noqa: E402
from gestion import GestionColis  # noqa: E402


class TestGenerateur(unittest.TestCase):
    def test_identifiants_uniques_et_melanges(self):
        identifiants = [c.identifiant for c in generer_colis(1_000, graine=1)]
        self.assertEqual(sorted(identifiants), list(range(1, 1_001)))
        self.assertNotEqual(identifiants, sorted(identifiants))

    def test_reproductible(self):
        self.assertEqual(generer_colis(200, graine=7), generer_colis(200, graine=7))
        self.assertNotEqual(generer_colis(200, graine=7), generer_colis(200, graine=8))

    def test_valeurs_dans_les_bornes(self):
        for c in generer_colis(5_000, graine=3):
            self.assertTrue(POIDS_MIN <= c.poids <= POIDS_MAX)
            self.assertTrue(c.poids <= c.valeur <= 4 * c.poids)
            self.assertTrue(PRIORITE_MIN <= c.priorite <= PRIORITE_MAX)
            self.assertIn(c.destination, DESTINATIONS)


class TestQuatreTailles(unittest.TestCase):
    def test_operations_a_chaque_taille(self):
        rng = random.Random(0)
        for niveau, n in NIVEAUX.items():
            with self.subTest(n=n):
                colis = generer_colis(n, graine=niveau)
                g = GestionColis(colis)
                self.assertEqual(len(g), n)
                for c in rng.sample(colis, min(200, n)):
                    self.assertIs(g.rechercher(c.identifiant), c)
                self.assertIsNone(g.rechercher(n + 1))
                for critere in ("poids", "valeur", "priorite"):
                    attendu = sorted(colis, key=lambda c: getattr(c, critere), reverse=True)
                    self.assertEqual(g.trier(critere, decroissant=True), attendu)
                s = g.statistiques()
                self.assertEqual(s["poids_total"], sum(c.poids for c in colis))
                self.assertEqual(sum(s["par_priorite"].values()), n)


if __name__ == "__main__":
    unittest.main()
