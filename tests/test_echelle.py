"""Tests de l'étape 5 : générateur de données et fonctionnement aux 4 niveaux du sujet."""

import os
import random
import subprocess
import sys
import tempfile
import unittest

RACINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(RACINE, "src"))

from colis import PRIORITE_MAX, PRIORITE_MIN  # noqa: E402
from generateur import DESTINATIONS, NIVEAUX, POIDS_MAX, POIDS_MIN, generer_colis  # noqa: E402
from gestion import GestionColis  # noqa: E402
from stockage import ecrire_csv, lire_csv  # noqa: E402

MAIN = os.path.join(RACINE, "src", "main.py")


class TestGenerateur(unittest.TestCase):
    def test_taille_et_identifiants_uniques(self):
        colis = generer_colis(1_000, graine=1)
        self.assertEqual(len(colis), 1_000)
        self.assertEqual(sorted(c.identifiant for c in colis), list(range(1, 1_001)))

    def test_identifiants_melanges(self):
        ids = [c.identifiant for c in generer_colis(1_000, graine=1)]
        self.assertNotEqual(ids, sorted(ids))

    def test_reproductible(self):
        self.assertEqual(generer_colis(200, graine=7), generer_colis(200, graine=7))
        self.assertNotEqual(generer_colis(200, graine=7), generer_colis(200, graine=8))

    def test_identifiant_de_depart(self):
        ids = {c.identifiant for c in generer_colis(50, identifiant_depart=500)}
        self.assertEqual(ids, set(range(500, 550)))

    def test_valeurs_dans_les_bornes(self):
        for c in generer_colis(5_000, graine=3):
            self.assertTrue(POIDS_MIN <= c.poids <= POIDS_MAX)
            self.assertTrue(c.poids <= c.valeur <= 4 * c.poids + 10)   # valeur corrélée au poids
            self.assertTrue(PRIORITE_MIN <= c.priorite <= PRIORITE_MAX)
            self.assertIn(c.destination, DESTINATIONS)


class TestQuatreNiveaux(unittest.TestCase):
    """Toutes les opérations de gestion sont vérifiées pour 100, 1 000, 10 000 et 100 000 colis."""

    def test_operations_a_chaque_niveau(self):
        rng = random.Random(0)
        for niveau, n in NIVEAUX.items():
            with self.subTest(niveau=niveau, n=n):
                colis = generer_colis(n, graine=niveau)
                g = GestionColis(colis)
                self.assertEqual(len(g), n)
                # recherche : jusqu'à 200 identifiants présents et un absent
                for c in rng.sample(colis, min(200, n)):
                    self.assertIs(g.rechercher(c.identifiant), c)
                self.assertIsNone(g.rechercher(n + 1))
                # tris : conformes à sorted()
                for critere in ("poids", "valeur", "priorite"):
                    attendu = sorted(colis, key=lambda c: getattr(c, critere), reverse=True)
                    self.assertEqual(g.trier(critere, decroissant=True), attendu)
                # statistiques : cohérentes avec un calcul direct
                s = g.statistiques()
                self.assertEqual(s["poids_total"], sum(c.poids for c in colis))
                self.assertEqual(sum(s["par_priorite"].values()), n)
                self.assertEqual(sum(nb for nb, _, _ in s["par_destination"].values()), n)

    def test_fichier_csv_de_100000_colis(self):
        colis = generer_colis(100_000)
        with tempfile.TemporaryDirectory() as dossier:
            chemin = os.path.join(dossier, "niveau4.csv")
            ecrire_csv(chemin, colis)
            self.assertEqual(lire_csv(chemin), colis)


class TestMenuNiveaux(unittest.TestCase):
    def session(self, saisies):
        r = subprocess.run([sys.executable, MAIN], input=saisies, text=True, capture_output=True,
                           timeout=60, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        return r.stdout + r.stderr

    def test_generer_niveau_4_puis_paginer(self):
        sortie = self.session("8\n4\n\n1\n\nq\n0\n")
        self.assertIn("100000 colis générés", sortie)
        self.assertIn("Colis 1 à 20 sur 100000", sortie)
        self.assertIn("Colis 21 à 40 sur 100000", sortie)
        self.assertNotIn("Colis 41 à 60", sortie)          # « q » arrête la pagination

    def test_ajouter_a_la_collection_sans_doublon(self):
        sortie = self.session("8\n1\nn\n0\n")           # 100 colis ajoutés aux 5 du sujet
        self.assertIn("La collection contient 105 colis.", sortie)

    def test_enregistrer_puis_recharger(self):
        with tempfile.TemporaryDirectory() as dossier:
            chemin = os.path.join(dossier, "copie.csv")
            sortie = self.session(f"8\n2\n\n9\n2\n{chemin}\n9\n1\n{chemin}\n0\n")
            self.assertIn("1000 colis enregistrés", sortie)
            self.assertIn("1000 colis chargés", sortie)

    def test_fichier_absent(self):
        sortie = self.session("9\n1\ndonnees/absent.csv\n7\n0\n")
        self.assertIn("fichier introuvable", sortie)
        self.assertIn("Nombre de colis     : 5", sortie)   # collection inchangée


if __name__ == "__main__":
    unittest.main()
