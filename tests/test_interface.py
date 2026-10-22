"""Tests de l'étape 4 : saisies, statistiques, pagination et sessions complètes du menu."""

import os
import subprocess
import sys
import unittest
from unittest import mock

RACINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(RACINE, "src"))

from affichage import page  # noqa: E402
from colis import Colis  # noqa: E402
from gestion import GestionColis  # noqa: E402
from saisie import Abandon, lire_entier, lire_oui_non, lire_texte  # noqa: E402

EXEMPLE = os.path.join(RACINE, "donnees", "colis_exemple.csv")
MAIN = os.path.join(RACINE, "src", "main.py")


def clavier(*lignes):
    """Simule des saisies au clavier (chaque élément = une ligne tapée)."""
    return mock.patch("builtins.input", side_effect=list(lignes))


def session(saisies):
    """Lance le vrai programme avec des saisies et renvoie sa sortie."""
    resultat = subprocess.run([sys.executable, MAIN], input=saisies, text=True,
                              capture_output=True, timeout=30,
                              env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    return resultat.returncode, resultat.stdout + resultat.stderr


class TestSaisie(unittest.TestCase):
    def test_entier_redemande_tant_que_invalide(self):
        with clavier("abc", "2.5", "", "0", "9", "4"), mock.patch("builtins.print"):
            self.assertEqual(lire_entier("? ", 1, 5), 4)

    def test_entier_valeur_par_defaut(self):
        with clavier(""):
            self.assertEqual(lire_entier("? ", 0, defaut=106), 106)

    def test_texte_obligatoire(self):
        with clavier("", "   ", " Nice "), mock.patch("builtins.print"):
            self.assertEqual(lire_texte("? "), "Nice")

    def test_oui_non(self):
        with clavier("peut-être", "O"), mock.patch("builtins.print"):
            self.assertTrue(lire_oui_non("? "))
        with clavier(""):
            self.assertFalse(lire_oui_non("? ", defaut=False))

    def test_fin_de_saisie(self):
        with mock.patch("builtins.input", side_effect=EOFError):
            with self.assertRaises(Abandon):
                lire_entier("? ")


class TestStatistiques(unittest.TestCase):
    def test_donnees_du_sujet(self):
        s = GestionColis.depuis_csv(EXEMPLE).statistiques()
        self.assertEqual((s["nombre"], s["poids_total"], s["valeur_totale"]), (5, 30, 110))
        self.assertAlmostEqual(s["poids_moyen"], 6.0)
        self.assertAlmostEqual(s["valeur_moyenne"], 22.0)
        self.assertEqual(s["plus_lourd"].identifiant, 103)
        self.assertEqual(s["plus_leger"].identifiant, 105)
        self.assertEqual(s["plus_precieux"].identifiant, 103)
        self.assertEqual(s["par_priorite"], {1: 1, 2: 1, 3: 1, 4: 1, 5: 1})
        self.assertEqual(s["par_destination"],
                         {"Lille": (2, 5, 25), "Lyon": (1, 12, 40), "Paris": (2, 13, 45)})

    def test_collection_vide(self):
        s = GestionColis().statistiques()
        self.assertEqual(s["nombre"], 0)
        self.assertIsNone(s["plus_lourd"])
        self.assertEqual(s["par_priorite"], {1: 0, 2: 0, 3: 0, 4: 0, 5: 0})


class TestPagination(unittest.TestCase):
    def test_pages(self):
        colis = [Colis(i, 1, 1, 1, "X") for i in range(1, 46)]   # 45 colis
        premiere = page(colis, 0, 20)
        self.assertEqual(len(premiere), 2 + 20 + 1)
        self.assertEqual(premiere[-1], "Colis 1 à 20 sur 45")
        derniere = page(colis, 2, 20)
        self.assertEqual(len(derniere), 2 + 5 + 1)
        self.assertEqual(derniere[-1], "Colis 41 à 45 sur 45")


class TestSessionsDuMenu(unittest.TestCase):
    """Le vrai programme est lancé avec des saisies, comme par un utilisateur."""

    def test_menu_du_sujet_affiche(self):
        code, sortie = session("0\n")
        self.assertEqual(code, 0)
        for option in ("===== GESTION DES LIVRAISONS =====", "1. Afficher les colis",
                       "2. Ajouter un colis", "3. Rechercher un colis", "4. Organiser les colis",
                       "5. Préparer un camion", "6. Afficher le chargement",
                       "7. Afficher les statistiques", "8. Générer des colis (100 à 100 000)",
                       "9. Charger / enregistrer un fichier CSV", "0. Quitter", "Au revoir."):
            self.assertIn(option, sortie)

    def test_afficher(self):
        _, sortie = session("1\n0\n")
        self.assertIn("Colis 1 à 5 sur 5", sortie)

    def test_ajouter_puis_rechercher(self):
        _, sortie = session("2\n\n4\n30\n5\nNice\n3\n106\n0\n")
        self.assertIn("Colis 106 ajouté. La collection contient 6 colis.", sortie)
        self.assertRegex(sortie, r"106 \|\s+4 \|\s+30 \|\s+5 \| Nice")

    def test_ajout_avec_saisies_invalides(self):
        _, sortie = session("2\n\nabc\n0\n4\n-5\n30\n9\n5\n\nNice\n0\n")
        self.assertIn("Veuillez saisir un nombre entier.", sortie)
        self.assertIn("La valeur doit être supérieure ou égale à 1.", sortie)
        self.assertIn("La valeur doit être inférieure ou égale à 5.", sortie)
        self.assertIn("Saisie obligatoire.", sortie)
        self.assertIn("Colis 106 ajouté.", sortie)

    def test_ajout_identifiant_existant_refuse(self):
        _, sortie = session("2\n101\n0\n")
        self.assertIn("un colis d'identifiant 101 existe déjà", sortie)

    def test_recherche_absente(self):
        _, sortie = session("3\n999\n0\n")
        self.assertIn("Aucun colis d'identifiant 999.", sortie)

    def test_organiser(self):
        _, sortie = session("4\n2\n2\n0\n")   # par valeur, décroissant
        self.assertIn("5 colis triés", sortie)
        lignes = [l for l in sortie.splitlines() if l.strip()[:3] in ("101", "102", "103", "104", "105")]
        self.assertEqual([l.split("|")[0].strip() for l in lignes], ["103", "104", "101", "105", "102"])

    def test_statistiques(self):
        _, sortie = session("7\n0\n")
        self.assertIn("Poids total         : 30 kg (moyenne 6.00 kg)", sortie)

    def test_choix_invalides_et_fin_de_saisie(self):
        code, sortie = session("abc\n10\n")   # puis fin de l'entrée (Ctrl-D)
        self.assertEqual(code, 0)
        self.assertIn("Veuillez saisir un nombre entier.", sortie)
        self.assertIn("La valeur doit être inférieure ou égale à 9.", sortie)
        self.assertIn("Au revoir.", sortie)
        self.assertNotIn("Traceback", sortie)


if __name__ == "__main__":
    unittest.main()
