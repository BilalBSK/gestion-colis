"""Tests du modèle Colis et de la lecture des fichiers CSV. Je vérifie surtout
qu'un colis incohérent est refusé dès sa création."""

import dataclasses
import os
import sys
import tempfile
import unittest

RACINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(RACINE, "src"))

from colis import Colis  # noqa: E402
from stockage import lire_csv  # noqa: E402

EXEMPLE = os.path.join(RACINE, "donnees", "colis_exemple.csv")
ENTETE = "identifiant;poids;valeur;priorite;destination\n"


class TestColis(unittest.TestCase):
    def test_colis_valide(self):
        c = Colis(101, 8, 20, 2, "Paris")
        self.assertEqual((c.identifiant, c.poids, c.valeur, c.priorite, c.destination),
                         (101, 8, 20, 2, "Paris"))

    def test_bornes_acceptees(self):
        Colis(0, 1, 0, 1, "A")
        Colis(1, 1, 0, 5, "A")

    def test_destination_sans_espaces_inutiles(self):
        self.assertEqual(Colis(1, 1, 1, 1, "  Lyon  ").destination, "Lyon")

    def test_valeurs_refusees(self):
        for args in ((1, 0, 10, 1, "Lyon"),      # poids nul
                     (1, -3, 10, 1, "Lyon"),     # poids négatif
                     (1, 5, -1, 3, "Lyon"),      # valeur négative
                     (1, 5, 10, 0, "Lyon"),      # priorité trop petite
                     (1, 5, 10, 6, "Lyon"),      # priorité trop grande
                     (-1, 5, 10, 3, "Lyon"),     # identifiant négatif
                     (1, 5, 10, 3, "   ")):      # destination vide
            with self.subTest(args=args), self.assertRaises(ValueError):
                Colis(*args)

    def test_types_refuses(self):
        for args in ((1, 2.5, 10, 3, "Lyon"), (1, 5, "10", 3, "Lyon"), (True, 5, 10, 3, "Lyon")):
            with self.subTest(args=args), self.assertRaises(TypeError):
                Colis(*args)

    def test_colis_non_modifiable(self):
        c = Colis(1, 5, 10, 3, "Lyon")
        with self.assertRaises(dataclasses.FrozenInstanceError):
            c.poids = 99


class TestLectureCsv(unittest.TestCase):
    def fichier(self, dossier, contenu):
        chemin = os.path.join(dossier, "test.csv")
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(contenu)
        return chemin

    def test_donnees_du_sujet(self):
        self.assertEqual(lire_csv(EXEMPLE), [
            Colis(101, 8, 20, 2, "Paris"),
            Colis(102, 3, 10, 5, "Lille"),
            Colis(103, 12, 40, 1, "Lyon"),
            Colis(104, 5, 25, 4, "Paris"),
            Colis(105, 2, 15, 3, "Lille"),
        ])

    def test_ligne_invalide_avec_son_numero(self):
        with tempfile.TemporaryDirectory() as d:
            chemin = self.fichier(d, ENTETE + "1;3;10;2;Lyon\n2;abc;10;2;Lyon\n")
            with self.assertRaisesRegex(ValueError, "ligne 3"):
                lire_csv(chemin)

    def test_priorite_invalide(self):
        with tempfile.TemporaryDirectory() as d:
            chemin = self.fichier(d, ENTETE + "1;3;10;9;Lyon\n")
            with self.assertRaisesRegex(ValueError, "ligne 2.*priorité"):
                lire_csv(chemin)

    def test_entete_ou_colonne_manquante(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, "en-tête"):
                lire_csv(self.fichier(d, "id;poids\n1;3\n"))
            with self.assertRaisesRegex(ValueError, "ligne 2"):
                lire_csv(self.fichier(d, ENTETE + "1;3;10\n"))


if __name__ == "__main__":
    unittest.main()
