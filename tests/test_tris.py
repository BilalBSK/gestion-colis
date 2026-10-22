"""Tests de l'étape 3 : algorithmes de tri et tris de la collection."""

import os
import random
import sys
import unittest

RACINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(RACINE, "src"))

from colis import Colis  # noqa: E402
from gestion import GestionColis  # noqa: E402
from tris import tri_comptage, tri_fusion, tri_insertion  # noqa: E402

EXEMPLE = os.path.join(RACINE, "donnees", "colis_exemple.csv")
premier = lambda paire: paire[0]  # noqa: E731


def ids(colis):
    return [c.identifiant for c in colis]


class TestTriFusion(unittest.TestCase):
    def test_cas_limites(self):
        self.assertEqual(tri_fusion([]), [])
        self.assertEqual(tri_fusion([7]), [7])
        self.assertEqual(tri_fusion([2, 1]), [1, 2])
        self.assertEqual(tri_fusion([1, 2, 3]), [1, 2, 3])        # déjà trié
        self.assertEqual(tri_fusion([3, 2, 1]), [1, 2, 3])        # ordre inverse
        self.assertEqual(tri_fusion([4, 4, 4]), [4, 4, 4])        # tous égaux

    def test_identique_a_sorted_sur_listes_aleatoires(self):
        rng = random.Random(42)
        for n in list(range(50)) + [100, 1_000, 1_023, 1_024, 1_025, 5_000]:
            donnees = [rng.randint(-100, 100) for _ in range(n)]
            self.assertEqual(tri_fusion(donnees), sorted(donnees))
            self.assertEqual(tri_fusion(donnees, decroissant=True), sorted(donnees, reverse=True))

    def test_stabilite_dans_les_deux_sens(self):
        rng = random.Random(1)
        paires = [(rng.randint(0, 5), i) for i in range(2_000)]  # beaucoup d'égalités
        self.assertEqual(tri_fusion(paires, premier), sorted(paires, key=premier))
        self.assertEqual(tri_fusion(paires, premier, decroissant=True),
                         sorted(paires, key=premier, reverse=True))

    def test_entree_non_modifiee(self):
        donnees = [3, 1, 2]
        tri_fusion(donnees)
        self.assertEqual(donnees, [3, 1, 2])

    def test_cle_calculee_une_fois_par_element(self):
        appels = []
        tri_fusion(list(range(100, 0, -1)), lambda x: appels.append(x) or x)
        self.assertEqual(len(appels), 100)


class TestTriComptage(unittest.TestCase):
    def test_identique_a_sorted_et_stable(self):
        rng = random.Random(7)
        paires = [(rng.randint(1, 5), i) for i in range(2_000)]
        self.assertEqual(tri_comptage(paires, premier, 1, 5), sorted(paires, key=premier))
        self.assertEqual(tri_comptage(paires, premier, 1, 5, decroissant=True),
                         sorted(paires, key=premier, reverse=True))

    def test_liste_vide(self):
        self.assertEqual(tri_comptage([], premier, 1, 5), [])

    def test_cle_hors_intervalle(self):
        with self.assertRaises(ValueError):
            tri_comptage([(1, "a"), (9, "b")], premier, 1, 5)


class TestTriInsertion(unittest.TestCase):
    def test_identique_a_sorted_et_stable(self):
        rng = random.Random(3)
        paires = [(rng.randint(0, 9), i) for i in range(500)]
        self.assertEqual(tri_insertion(paires, premier), sorted(paires, key=premier))
        self.assertEqual(tri_insertion(paires, premier, decroissant=True),
                         sorted(paires, key=premier, reverse=True))


class TestTrisDeLaCollection(unittest.TestCase):
    def setUp(self):
        self.g = GestionColis.depuis_csv(EXEMPLE)

    def test_tri_par_poids(self):
        self.assertEqual(ids(self.g.trier("poids")), [105, 102, 104, 101, 103])
        self.assertEqual(ids(self.g.trier("poids", decroissant=True)), [103, 101, 104, 102, 105])

    def test_tri_par_valeur(self):
        self.assertEqual(ids(self.g.trier("valeur")), [102, 105, 101, 104, 103])
        self.assertEqual(ids(self.g.trier("valeur", decroissant=True)), [103, 104, 101, 105, 102])

    def test_tri_par_priorite(self):
        self.assertEqual(ids(self.g.trier("priorite")), [103, 101, 105, 104, 102])
        self.assertEqual(ids(self.g.trier("priorite", decroissant=True)), [102, 104, 105, 101, 103])

    def test_tri_priorite_puis_valeur(self):
        self.g.ajouter(Colis(106, 4, 30, 5, "Nice"))   # même priorité que 102, valeur plus forte
        self.assertEqual(ids(self.g.trier("priorite_valeur", decroissant=True)),
                         [106, 102, 104, 105, 101, 103])
        rng = random.Random(5)
        g = GestionColis(Colis(i, 1, rng.randint(0, 50), rng.randint(1, 5), "X") for i in range(1_000))
        attendu = sorted(g.lister(), key=lambda c: (-c.priorite, -c.valeur))
        self.assertEqual(g.trier("priorite_valeur", decroissant=True), attendu)

    def test_collection_non_modifiee(self):
        self.g.trier("valeur", decroissant=True)
        self.assertEqual(ids(self.g.lister()), [101, 102, 103, 104, 105])

    def test_critere_inconnu(self):
        with self.assertRaises(ValueError):
            self.g.trier("destination")

    def test_grande_collection_conforme_a_sorted(self):
        rng = random.Random(11)
        g = GestionColis(Colis(i, rng.randint(1, 30), rng.randint(0, 100), rng.randint(1, 5), "X")
                         for i in range(20_000))
        for critere in ("poids", "valeur", "priorite"):
            for sens in (False, True):
                attendu = sorted(g.lister(), key=lambda c: getattr(c, critere), reverse=sens)
                self.assertEqual(g.trier(critere, sens), attendu, f"{critere}, décroissant={sens}")


if __name__ == "__main__":
    unittest.main()
