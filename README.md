# Gestion des colis et optimisation du chargement d'un camion

Projet informatique : programme permettant de gérer une collection de colis
(ajout, affichage, recherche, tris) et de préparer le chargement d'un camion
en maximisant la valeur transportée, tout en tenant compte de la priorité des colis.

> Projet en cours de réalisation : ce README sera complété à chaque étape.

## Langage

**Python 3** (version 3.10 ou plus récente), avec la **bibliothèque standard uniquement**.

Python a été choisi pour sa lisibilité : le code reste proche du pseudo-code, ce qui
permet de se concentrer sur les choix algorithmiques et leur justification. Les algorithmes
au cœur du sujet (tris, optimisation du chargement) sont implémentés à la main, et non
délégués à des fonctions natives.

## Lancement

```bash
python3 src/main.py
```

Les 5 colis d'exemple du sujet sont chargés au démarrage. L'option 8 génère 100, 1 000, 10 000
ou 100 000 colis pour tester le passage à l'échelle. Menu :

```
===== GESTION DES LIVRAISONS =====

1. Afficher les colis
2. Ajouter un colis
3. Rechercher un colis
4. Organiser les colis
5. Préparer un camion
6. Afficher le chargement
7. Afficher les statistiques
8. Générer des colis (100 à 100 000)
9. Charger / enregistrer un fichier CSV
0. Quitter
```

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## Organisation du dépôt

```
projet/
├── src/          code source
│   ├── colis.py      modèle Colis (validation des données)
│   ├── stockage.py   lecture / écriture des colis au format CSV
│   ├── gestion.py    collection de colis (table de hachage) : ajout, affichage, recherche, tris
│   ├── affichage.py  mise en forme des colis en tableau
│   ├── tris.py       tri fusion et tri par comptage (implémentés à la main)
│   ├── generateur.py jeux de données aléatoires reproductibles (100 à 100 000 colis)
│   ├── saisie.py     saisies clavier robustes
│   └── main.py       interface en menu (point d'entrée)
├── tests/        tests unitaires
├── donnees/      colis d'exemple du sujet (CSV)
├── docs/         source du rapport et captures d'écran
├── outils/       génération du rapport PDF, captures, mesures
├── README.md
└── rapport.pdf
```

## Dépôt GitHub

https://github.com/BilalBSK/gestion-colis
