"""Modèle de données : un colis.

Un colis est représenté par une classe de données (dataclass) :
  - frozen=True : un colis est immuable une fois créé. Son identifiant sert de
    clé dans la collection : le modifier « en douce » corromprait l'index.
  - slots=True  : les attributs sont stockés dans des emplacements fixes au lieu
    d'un dictionnaire propre à chaque objet, ce qui réduit fortement la mémoire
    par colis (important à 100 000 colis et plus).
"""

from dataclasses import dataclass

# Convention retenue : 1 = priorité la plus faible, 5 = priorité la plus forte.
PRIORITE_MIN = 1
PRIORITE_MAX = 5


@dataclass(frozen=True, slots=True)
class Colis:
    identifiant: int   # unique dans la collection
    poids: int         # en kg, entier strictement positif
    valeur: int        # entier positif ou nul
    priorite: int      # de PRIORITE_MIN à PRIORITE_MAX
    destination: str   # texte non vide

    def __post_init__(self):
        """Vérifie la cohérence des données dès la création : O(1)."""
        for nom in ("identifiant", "poids", "valeur", "priorite"):
            valeur = getattr(self, nom)
            # bool est un sous-type de int en Python : on l'exclut explicitement
            if not isinstance(valeur, int) or isinstance(valeur, bool):
                raise TypeError(f"{nom} doit être un entier (reçu : {valeur!r})")
        if self.identifiant < 0:
            raise ValueError("l'identifiant doit être positif ou nul")
        if self.poids <= 0:
            raise ValueError("le poids doit être strictement positif")
        if self.valeur < 0:
            raise ValueError("la valeur doit être positive ou nulle")
        if not PRIORITE_MIN <= self.priorite <= PRIORITE_MAX:
            raise ValueError(f"la priorité doit être comprise entre {PRIORITE_MIN} et {PRIORITE_MAX}")
        if not isinstance(self.destination, str) or not self.destination.strip():
            raise ValueError("la destination doit être un texte non vide")
        # Classe immuable : on passe par object.__setattr__ pour normaliser le texte
        object.__setattr__(self, "destination", self.destination.strip())
