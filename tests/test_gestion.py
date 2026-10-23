"""Tests de la collection : ajout, affichage, recherche, tris et statistiques,
sur les colis d'exemple du sujet."""

import os
import random
import sys
import tempfile
import unittest

RACINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(RACINE, "src"))

from affichage import page  # noqa: E402
from colis import Colis  # noqa: E402
from gestion import GestionColis  # noqa: E402

EXEMPLE = os.path.join(RACINE, "donnees", "colis_exemple.csv")


def ids(colis):
    return [c.identifiant for c in colis]


class TestAjoutEtRecherche(unittest.TestCase):
    def setUp(self):
        self.g = GestionColis.depuis_csv(EXEMPLE)

    def test_ajout(self):
        nouveau = Colis(106, 4, 30, 5, "Nice")
        self.g.ajouter(nouveau)
        self.assertEqual(len(self.g), 6)
        self.assertIs(self.g.rechercher(106), nouveau)

    def test_doublon_refuse(self):
        with self.assertRaisesRegex(ValueError, "101"):
            self.g.ajouter(Colis(101, 1, 1, 1, "Nice"))
        self.assertEqual(len(self.g), 5)
        self.assertEqual(self.g.rechercher(101).destination, "Paris")   # l'ancien est gardé

    def test_doublon_dans_un_fichier(self):
        with tempfile.TemporaryDirectory() as d:
            chemin = os.path.join(d, "doublon.csv")
            with open(chemin, "w", encoding="utf-8") as f:
                f.write("identifiant;poids;valeur;priorite;destination\n1;3;10;2;Lyon\n1;4;12;3;Nice\n")
            with self.assertRaises(ValueError):
                GestionColis.depuis_csv(chemin)

    def test_prochain_identifiant(self):
        self.assertEqual(GestionColis().prochain_identifiant(), 1)
        self.assertEqual(self.g.prochain_identifiant(), 106)
        self.g.ajouter(Colis(500, 1, 1, 1, "Nice"))
        self.g.ajouter(Colis(200, 1, 1, 1, "Nice"))
        self.assertEqual(self.g.prochain_identifiant(), 501)

    def test_recherche(self):
        c = self.g.rechercher(103)
        self.assertEqual((c.poids, c.valeur, c.priorite, c.destination), (12, 40, 1, "Lyon"))
        self.assertIsNone(self.g.rechercher(999))

    def test_hachage_et_sequentielle_donnent_le_meme_resultat(self):
        rng = random.Random(1)
        identifiants = rng.sample(range(1, 100_000), 2_000)
        g = GestionColis(Colis(i, 1 + i % 30, i % 100, 1 + i % 5, "Paris") for i in identifiants)
        for cible in rng.sample(identifiants, 200) + [0, 100_001]:
            self.assertIs(g.rechercher(cible), g.rechercher_sequentielle(cible))


class TestAffichage(unittest.TestCase):
    def test_ordre_d_ajout_conserve(self):
        self.assertEqual(ids(GestionColis.depuis_csv(EXEMPLE).lister()), [101, 102, 103, 104, 105])

    def test_pages(self):
        colis = [Colis(i, 1, 1, 1, "X") for i in range(1, 46)]   # 45 colis
        self.assertEqual(len(page(colis, 0, 20)), 2 + 20 + 1)
        self.assertEqual(page(colis, 0, 20)[-1], "Colis 1 à 20 sur 45")
        self.assertEqual(page(colis, 2, 20)[-1], "Colis 41 à 45 sur 45")


class TestTrisDeLaCollection(unittest.TestCase):
    def setUp(self):
        self.g = GestionColis.depuis_csv(EXEMPLE)

    def test_ordres_attendus_sur_les_donnees_du_sujet(self):
        self.assertEqual(ids(self.g.trier("poids")), [105, 102, 104, 101, 103])
        self.assertEqual(ids(self.g.trier("valeur", decroissant=True)), [103, 104, 101, 105, 102])
        self.assertEqual(ids(self.g.trier("priorite", decroissant=True)), [102, 104, 105, 101, 103])

    def test_la_collection_n_est_pas_modifiee(self):
        self.g.trier("valeur", decroissant=True)
        self.assertEqual(ids(self.g.lister()), [101, 102, 103, 104, 105])

    def test_critere_inconnu(self):
        with self.assertRaises(ValueError):
            self.g.trier("destination")


class TestStatistiques(unittest.TestCase):
    def test_donnees_du_sujet(self):
        s = GestionColis.depuis_csv(EXEMPLE).statistiques()
        self.assertEqual((s["nombre"], s["poids_total"], s["valeur_totale"]), (5, 30, 110))
        self.assertAlmostEqual(s["poids_moyen"], 6.0)
        self.assertEqual((s["plus_lourd"].identifiant, s["plus_leger"].identifiant,
                          s["plus_precieux"].identifiant), (103, 105, 103))
        self.assertEqual(s["par_priorite"], {1: 1, 2: 1, 3: 1, 4: 1, 5: 1})
        self.assertEqual(s["par_destination"],
                         {"Lille": (2, 5, 25), "Lyon": (1, 12, 40), "Paris": (2, 13, 45)})

    def test_collection_vide(self):
        s = GestionColis().statistiques()
        self.assertEqual(s["nombre"], 0)
        self.assertIsNone(s["plus_lourd"])


if __name__ == "__main__":
    unittest.main()
