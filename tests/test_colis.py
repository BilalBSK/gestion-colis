"""Tests de l'étape 1 : modèle Colis et lecture/écriture CSV."""

import dataclasses
import os
import sys
import tempfile
import unittest

RACINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(RACINE, "src"))

from colis import Colis  # noqa: E402
from stockage import ecrire_csv, lire_csv  # noqa: E402

EXEMPLE = os.path.join(RACINE, "donnees", "colis_exemple.csv")


class TestCreationColis(unittest.TestCase):
    def test_colis_valide(self):
        c = Colis(101, 8, 20, 2, "Paris")
        self.assertEqual((c.identifiant, c.poids, c.valeur, c.priorite, c.destination),
                         (101, 8, 20, 2, "Paris"))

    def test_destination_normalisee(self):
        self.assertEqual(Colis(1, 1, 1, 1, "  Lyon  ").destination, "Lyon")

    def test_bornes_acceptees(self):
        Colis(0, 1, 0, 1, "A")   # identifiant 0, valeur 0, priorité minimale
        Colis(1, 1, 0, 5, "A")   # priorité maximale

    def test_poids_nul_ou_negatif_refuse(self):
        for poids in (0, -3):
            with self.assertRaises(ValueError):
                Colis(1, poids, 10, 1, "Lyon")

    def test_valeur_negative_refusee(self):
        with self.assertRaises(ValueError):
            Colis(1, 5, -1, 3, "Lyon")

    def test_priorite_hors_bornes_refusee(self):
        for priorite in (0, 6):
            with self.assertRaises(ValueError):
                Colis(1, 5, 10, priorite, "Lyon")

    def test_identifiant_negatif_refuse(self):
        with self.assertRaises(ValueError):
            Colis(-1, 5, 10, 3, "Lyon")

    def test_destination_vide_refusee(self):
        for destination in ("", "   "):
            with self.assertRaises(ValueError):
                Colis(1, 5, 10, 3, destination)

    def test_types_non_entiers_refuses(self):
        with self.assertRaises(TypeError):
            Colis(1, 2.5, 10, 3, "Lyon")
        with self.assertRaises(TypeError):
            Colis(1, 5, "10", 3, "Lyon")
        with self.assertRaises(TypeError):
            Colis(True, 5, 10, 3, "Lyon")  # bool est un int en Python

    def test_colis_immuable(self):
        c = Colis(1, 5, 10, 3, "Lyon")
        with self.assertRaises(dataclasses.FrozenInstanceError):
            c.poids = 99

    def test_egalite(self):
        self.assertEqual(Colis(1, 5, 10, 3, "Lyon"), Colis(1, 5, 10, 3, "Lyon"))
        self.assertNotEqual(Colis(1, 5, 10, 3, "Lyon"), Colis(2, 5, 10, 3, "Lyon"))


class TestStockageCsv(unittest.TestCase):
    def test_lecture_donnees_du_sujet(self):
        colis = lire_csv(EXEMPLE)
        self.assertEqual(colis, [
            Colis(101, 8, 20, 2, "Paris"),
            Colis(102, 3, 10, 5, "Lille"),
            Colis(103, 12, 40, 1, "Lyon"),
            Colis(104, 5, 25, 4, "Paris"),
            Colis(105, 2, 15, 3, "Lille"),
        ])

    def test_ecriture_puis_relecture(self):
        colis = lire_csv(EXEMPLE)
        with tempfile.TemporaryDirectory() as dossier:
            chemin = os.path.join(dossier, "copie.csv")
            ecrire_csv(chemin, colis)
            self.assertEqual(lire_csv(chemin), colis)

    def _fichier(self, dossier, contenu):
        chemin = os.path.join(dossier, "test.csv")
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(contenu)
        return chemin

    def test_ligne_invalide_signalee_avec_son_numero(self):
        with tempfile.TemporaryDirectory() as dossier:
            chemin = self._fichier(dossier, "identifiant;poids;valeur;priorite;destination\n"
                                            "1;3;10;2;Lyon\n"
                                            "2;abc;10;2;Lyon\n")
            with self.assertRaisesRegex(ValueError, "ligne 3"):
                lire_csv(chemin)

    def test_priorite_invalide_dans_le_fichier(self):
        with tempfile.TemporaryDirectory() as dossier:
            chemin = self._fichier(dossier, "identifiant;poids;valeur;priorite;destination\n"
                                            "1;3;10;9;Lyon\n")
            with self.assertRaisesRegex(ValueError, "ligne 2.*priorité"):
                lire_csv(chemin)

    def test_entete_incorrect(self):
        with tempfile.TemporaryDirectory() as dossier:
            chemin = self._fichier(dossier, "id;poids\n1;3\n")
            with self.assertRaisesRegex(ValueError, "en-tête"):
                lire_csv(chemin)

    def test_colonne_manquante(self):
        with tempfile.TemporaryDirectory() as dossier:
            chemin = self._fichier(dossier, "identifiant;poids;valeur;priorite;destination\n"
                                            "1;3;10\n")
            with self.assertRaisesRegex(ValueError, "ligne 2"):
                lire_csv(chemin)


if __name__ == "__main__":
    unittest.main()
