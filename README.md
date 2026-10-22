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

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## Organisation du dépôt

```
projet/
├── src/          code source
│   ├── colis.py      modèle Colis (validation des données)
│   └── stockage.py   lecture / écriture des colis au format CSV
├── tests/        tests unitaires
├── donnees/      colis d'exemple du sujet (CSV)
├── docs/         source du rapport et captures d'écran
├── outils/       génération du rapport PDF, captures, mesures
├── README.md
└── rapport.pdf
```

## Dépôt GitHub

https://github.com/BilalBSK/gestion-colis
