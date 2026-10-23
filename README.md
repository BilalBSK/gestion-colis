# Gestion des colis et optimisation du chargement d'un camion

Projet informatique : programme permettant de gérer une collection de colis
(ajout, affichage, recherche, tris) et de préparer le chargement d'un camion
en maximisant la valeur transportée, tout en tenant compte de la priorité des colis.

Les choix algorithmiques, leurs complexités et les mesures sont détaillés dans
[rapport.pdf](rapport.pdf).

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
ou 100 000 colis pour tester le passage à l'échelle, et l'option 9 charge un autre fichier, par
exemple `donnees/colis_camion.csv` (les colis A, B, C, D de la partie camion). Menu :

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
9. Charger un fichier de colis
0. Quitter
```

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## Mesures de performance

```bash
python3 outils/benchmark.py      # principales opérations, 100 à 100 000 colis
python3 outils/graphiques.py     # courbes (docs/graphiques/*.svg) à partir des mesures
python3 outils/etude_exemple_camion.py comparaison   # DP, glouton et force brute sur A, B, C, D
```

Le PDF se régénère avec `sh outils/generer_rapport.sh` (Google Chrome est nécessaire).

## Organisation du dépôt

```
projet/
├── src/          code source
│   ├── colis.py      modèle Colis (validation des données)
│   ├── stockage.py   lecture des colis au format CSV
│   ├── gestion.py    collection de colis (table de hachage) : ajout, affichage, recherche, tris
│   ├── affichage.py  mise en forme des colis en tableau
│   ├── tris.py       tri fusion et tri par comptage (implémentés à la main)
│   ├── generateur.py jeux de données aléatoires reproductibles (100 à 100 000 colis)
│   ├── chargement.py chargement du camion (sac à dos 0/1) : programmation dynamique avec
│   │                 élagage, glouton et force brute pour comparer, prise en compte de la priorité
│   ├── saisie.py     saisies au clavier (redemande tant que la réponse est invalide)
│   └── main.py       interface en menu (point d'entrée)
├── tests/        tests unitaires
├── donnees/      colis d'exemple du sujet (CSV)
├── docs/         source du rapport, captures d'écran, mesures et graphiques
├── outils/       génération du rapport PDF, captures, mesures
├── README.md
└── rapport.pdf
```

## Dépôt GitHub

https://github.com/BilalBSK/gestion-colis
