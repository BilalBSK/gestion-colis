"""Tests des tris. Je compare mes résultats à ceux de sorted(), qui me sert de référence."""

import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from tris import tri_comptage, tri_fusion, tri_insertion  # noqa: E402

premier = lambda paire: paire[0]  # noqa: E731


class TestTriFusion(unittest.TestCase):
    def test_cas_limites(self):
        for liste in ([], [7], [2, 1], [1, 2, 3], [3, 2, 1], [4, 4, 4]):
            self.assertEqual(tri_fusion(liste), sorted(liste))

    def test_comme_sorted_sur_des_listes_aleatoires(self):
        rng = random.Random(42)
        for n in list(range(50)) + [1_000, 1_023, 1_024, 1_025, 5_000]:
            donnees = [rng.randint(-100, 100) for _ in range(n)]
            self.assertEqual(tri_fusion(donnees), sorted(donnees))
            self.assertEqual(tri_fusion(donnees, decroissant=True), sorted(donnees, reverse=True))

    def test_stable_dans_les_deux_sens(self):
        rng = random.Random(1)
        paires = [(rng.randint(0, 5), i) for i in range(2_000)]   # beaucoup d'égalités
        self.assertEqual(tri_fusion(paires, premier), sorted(paires, key=premier))
        self.assertEqual(tri_fusion(paires, premier, decroissant=True),
                         sorted(paires, key=premier, reverse=True))

    def test_liste_de_depart_intacte(self):
        donnees = [3, 1, 2]
        tri_fusion(donnees)
        self.assertEqual(donnees, [3, 1, 2])


class TestTriComptage(unittest.TestCase):
    def test_comme_sorted_et_stable(self):
        rng = random.Random(7)
        paires = [(rng.randint(1, 5), i) for i in range(2_000)]
        self.assertEqual(tri_comptage(paires, premier, 1, 5), sorted(paires, key=premier))
        self.assertEqual(tri_comptage(paires, premier, 1, 5, decroissant=True),
                         sorted(paires, key=premier, reverse=True))

    def test_cle_hors_intervalle(self):
        with self.assertRaises(ValueError):
            tri_comptage([(1, "a"), (9, "b")], premier, 1, 5)


class TestTriInsertion(unittest.TestCase):
    def test_comme_sorted_et_stable(self):
        rng = random.Random(3)
        paires = [(rng.randint(0, 9), i) for i in range(500)]
        self.assertEqual(tri_insertion(paires, premier), sorted(paires, key=premier))


if __name__ == "__main__":
    unittest.main()
