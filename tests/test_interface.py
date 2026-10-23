"""Tests des saisies et du menu. Pour le menu, je lance le vrai programme avec des
saisies (y compris fausses) et je regarde ce qu'il affiche."""

import os
import subprocess
import sys
import unittest
from unittest import mock

RACINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(RACINE, "src"))

from saisie import Abandon, lire_entier, lire_oui_non, lire_reel, lire_texte  # noqa: E402

MAIN = os.path.join(RACINE, "src", "main.py")


def clavier(*lignes):
    return mock.patch("builtins.input", side_effect=list(lignes))


def session(saisies):
    resultat = subprocess.run([sys.executable, MAIN], input=saisies, text=True, capture_output=True,
                              timeout=60, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    return resultat.returncode, resultat.stdout + resultat.stderr


class TestSaisie(unittest.TestCase):
    def test_entier_redemande_tant_que_invalide(self):
        with clavier("abc", "2.5", "", "0", "9", "4"), mock.patch("builtins.print"):
            self.assertEqual(lire_entier("? ", 1, 5), 4)

    def test_valeur_par_defaut(self):
        with clavier(""):
            self.assertEqual(lire_entier("? ", 0, defaut=106), 106)

    def test_reel_avec_virgule(self):
        with clavier("beaucoup", "-1", "0,5"), mock.patch("builtins.print"):
            self.assertEqual(lire_reel("? ", minimum=0), 0.5)

    def test_texte_et_oui_non(self):
        with clavier("", " Nice "), mock.patch("builtins.print"):
            self.assertEqual(lire_texte("? "), "Nice")
        with clavier("peut-être", "O"), mock.patch("builtins.print"):
            self.assertTrue(lire_oui_non("? "))

    def test_ctrl_d(self):
        with mock.patch("builtins.input", side_effect=EOFError):
            with self.assertRaises(Abandon):
                lire_entier("? ")


class TestMenu(unittest.TestCase):
    def test_menu_complet(self):
        code, sortie = session("0\n")
        self.assertEqual(code, 0)
        for option in ("===== GESTION DES LIVRAISONS =====", "1. Afficher les colis", "2. Ajouter un colis",
                       "3. Rechercher un colis", "4. Organiser les colis", "5. Préparer un camion",
                       "6. Afficher le chargement", "7. Afficher les statistiques", "0. Quitter"):
            self.assertIn(option, sortie)

    def test_afficher_ajouter_rechercher(self):
        _, sortie = session("1\n2\n\n4\n30\n5\nNice\n3\n106\n3\n999\n0\n")
        self.assertIn("Colis 1 à 5 sur 5", sortie)
        self.assertIn("Colis 106 ajouté. La collection contient 6 colis.", sortie)
        self.assertRegex(sortie, r"106 \|\s+4 \|\s+30 \|\s+5 \| Nice")
        self.assertIn("Aucun colis d'identifiant 999.", sortie)

    def test_saisies_invalides_et_doublon(self):
        _, sortie = session("2\n\nabc\n0\n4\n30\n9\n5\n\nNice\n2\n101\n0\n")
        for message in ("Veuillez saisir un nombre entier.", "La valeur doit être supérieure ou égale à 1.",
                        "La valeur doit être inférieure ou égale à 5.", "Saisie obligatoire.",
                        "Colis 106 ajouté.", "un colis d'identifiant 101 existe déjà"):
            self.assertIn(message, sortie)

    def test_organiser(self):
        _, sortie = session("4\n2\n2\n0\n")          # par valeur, décroissant
        lignes = [l for l in sortie.splitlines() if l.strip()[:3] in ("101", "102", "103", "104", "105")]
        self.assertEqual([l.split("|")[0].strip() for l in lignes], ["103", "104", "101", "105", "102"])

    def test_statistiques(self):
        _, sortie = session("7\n0\n")
        self.assertIn("Poids total         : 30 kg (moyenne 6.00 kg)", sortie)

    def test_camion_valeur_seule(self):
        _, sortie = session("6\n5\n20\n0\n6\n0\n")
        self.assertIn("utilisez d'abord l'option 5", sortie)
        self.assertIn("3 colis, 19 / 20 kg, valeur totale 80", sortie)        # optimum
        self.assertIn("4 colis, 18 / 20 kg, valeur totale 70", sortie)        # glouton
        self.assertIn("remplissage 95.0 %", sortie)

    def test_camion_avec_priorite_sur_les_colis_a_b_c_d(self):
        _, sortie = session("9\ndonnees/colis_camion.csv\n5\n14\n\n0\n")
        self.assertIn("2 colis, 13 / 14 kg, valeur totale 38, priorité moyenne 4.50", sortie)
        self.assertIn("la priorité coûte 7 de valeur", sortie)

    def test_generer_100000_colis_et_paginer(self):
        _, sortie = session("8\n4\n\n1\n\nq\n5\n1000\n0\n0\n")
        self.assertIn("100000 colis générés", sortie)
        self.assertIn("Colis 21 à 40 sur 100000", sortie)
        self.assertNotIn("Colis 41 à 60", sortie)
        self.assertIn("3983 colis gardés sur 100000", sortie)
        self.assertNotIn("Attention", sortie)

    def test_confirmation_pour_un_tres_gros_calcul(self):
        _, sortie = session("8\n4\n\n5\n100000\n0\nn\n0\n")
        self.assertIn("Attention", sortie)
        self.assertNotIn("Chargement optimal", sortie)

    def test_fichier_absent_et_choix_invalides(self):
        code, sortie = session("9\ndonnees/absent.csv\nabc\n10\n")   # puis Ctrl-D
        self.assertEqual(code, 0)
        self.assertIn("fichier introuvable", sortie)
        self.assertIn("La valeur doit être inférieure ou égale à 9.", sortie)
        self.assertIn("Au revoir.", sortie)
        self.assertNotIn("Traceback", sortie)


if __name__ == "__main__":
    unittest.main()
