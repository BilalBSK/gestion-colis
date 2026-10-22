"""Tests de l'étape 2 : ajouter, afficher et rechercher des colis."""

import os
import random
import sys
import tempfile
import unittest

RACINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(RACINE, "src"))

from affichage import ENTETE, ligne, tableau  # noqa: E402
from colis import Colis  # noqa: E402
from gestion import GestionColis  # noqa: E402

EXEMPLE = os.path.join(RACINE, "donnees", "colis_exemple.csv")


def collection_du_sujet():
    return GestionColis.depuis_csv(EXEMPLE)


class TestAjout(unittest.TestCase):
    def test_collection_vide(self):
        g = GestionColis()
        self.assertEqual(len(g), 0)
        self.assertEqual(g.lister(), [])

    def test_chargement_du_sujet(self):
        self.assertEqual(len(collection_du_sujet()), 5)

    def test_ajout(self):
        g = collection_du_sujet()
        nouveau = Colis(106, 4, 30, 5, "Nice")
        g.ajouter(nouveau)
        self.assertEqual(len(g), 6)
        self.assertIs(g.rechercher(106), nouveau)

    def test_doublon_refuse_et_collection_inchangee(self):
        g = collection_du_sujet()
        with self.assertRaisesRegex(ValueError, "101"):
            g.ajouter(Colis(101, 1, 1, 1, "Nice"))
        self.assertEqual(len(g), 5)
        self.assertEqual(g.rechercher(101).destination, "Paris")  # l'ancien est conservé

    def test_doublon_dans_un_fichier(self):
        with tempfile.TemporaryDirectory() as dossier:
            chemin = os.path.join(dossier, "doublon.csv")
            with open(chemin, "w", encoding="utf-8") as f:
                f.write("identifiant;poids;valeur;priorite;destination\n"
                        "1;3;10;2;Lyon\n1;4;12;3;Nice\n")
            with self.assertRaises(ValueError):
                GestionColis.depuis_csv(chemin)

    def test_prochain_identifiant(self):
        self.assertEqual(GestionColis().prochain_identifiant(), 1)
        g = collection_du_sujet()
        self.assertEqual(g.prochain_identifiant(), 106)
        g.ajouter(Colis(500, 1, 1, 1, "Nice"))
        g.ajouter(Colis(200, 1, 1, 1, "Nice"))
        self.assertEqual(g.prochain_identifiant(), 501)


class TestAffichage(unittest.TestCase):
    def test_ordre_insertion_conserve(self):
        ids = [c.identifiant for c in collection_du_sujet().lister()]
        self.assertEqual(ids, [101, 102, 103, 104, 105])

    def test_lister_renvoie_une_copie(self):
        g = collection_du_sujet()
        g.lister().clear()
        self.assertEqual(len(g), 5)

    def test_tableau_complet(self):
        lignes = tableau(collection_du_sujet().lister())
        self.assertEqual(lignes[0], ENTETE)
        self.assertEqual(len(lignes), 2 + 5)  # en-tête + séparateur + 5 colis
        self.assertIn("Lyon", lignes[4])

    def test_tableau_limite(self):
        lignes = tableau(collection_du_sujet().lister(), limite=2)
        self.assertEqual(len(lignes), 2 + 2 + 1)
        self.assertIn("3 autre(s) colis", lignes[-1])

    def test_tableau_vide(self):
        self.assertEqual(tableau([]), ["(aucun colis)"])

    def test_ligne(self):
        texte = ligne(Colis(101, 8, 20, 2, "Paris"))
        for morceau in ("101", "8", "20", "2", "Paris"):
            self.assertIn(morceau, texte)


class TestRecherche(unittest.TestCase):
    def test_recherche_existant(self):
        c = collection_du_sujet().rechercher(103)
        self.assertEqual((c.poids, c.valeur, c.priorite, c.destination), (12, 40, 1, "Lyon"))

    def test_recherche_absent(self):
        self.assertIsNone(collection_du_sujet().rechercher(999))
        self.assertIsNone(GestionColis().rechercher(1))

    def test_hachage_et_sequentielle_concordent(self):
        rng = random.Random(1)
        ids = rng.sample(range(1, 100_000), 2_000)
        g = GestionColis(Colis(i, 1 + i % 30, i % 100, 1 + i % 5, "Paris") for i in ids)
        for cible in rng.sample(ids, 200) + [0, 100_001]:
            self.assertIs(g.rechercher(cible), g.rechercher_sequentielle(cible))


if __name__ == "__main__":
    unittest.main()
