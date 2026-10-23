"""Un colis et ses informations.

J'ai pris une dataclass avec deux options :
  - frozen=True : un colis ne peut plus être modifié après sa création. Son
    identifiant sert de clé dans la collection, il ne doit donc pas changer
    une fois le colis rangé.
  - slots=True : les attributs sont rangés dans des emplacements fixes au lieu
    d'un dictionnaire par objet, ce qui fait gagner pas mal de mémoire quand on
    a 100 000 colis.
"""

from dataclasses import dataclass

# 1 = priorité la plus faible, 5 = priorité la plus forte
PRIORITE_MIN = 1
PRIORITE_MAX = 5


@dataclass(frozen=True, slots=True)
class Colis:
    identifiant: int   # unique dans la collection
    poids: int         # en kg, entier > 0
    valeur: int        # entier >= 0
    priorite: int      # de 1 à 5
    destination: str

    def __post_init__(self):
        """Je refuse un colis incohérent dès sa création : le reste du programme
        n'a donc jamais à vérifier les données."""
        for nom in ("identifiant", "poids", "valeur", "priorite"):
            valeur = getattr(self, nom)
            # en Python, True et False sont aussi des int : je les refuse à part
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
        # le colis est figé, je dois passer par object.__setattr__ pour enlever les espaces
        object.__setattr__(self, "destination", self.destination.strip())
