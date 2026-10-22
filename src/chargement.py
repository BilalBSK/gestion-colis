"""Optimisation du chargement d'un camion : le problème du sac à dos 0/1.

Chaque colis est soit chargé entièrement, soit laissé (pas de fraction). On
cherche le sous-ensemble de colis de poids total <= capacité qui maximise la
somme des « utilités ». Par défaut, l'utilité d'un colis est sa valeur ; la
prise en compte de la priorité (partie 9 du rapport) remplacera simplement
cette fonction.

Trois méthodes :
  - sac_a_dos_dp : programmation dynamique. EXACTE (toujours optimale).
                   O(n x W) en temps et en mémoire (W = capacité en kg).
  - glouton      : tri par rapport utilité / poids. O(n log n), RAPIDE mais
                   PAS TOUJOURS OPTIMAL.
  - force_brute  : essaie les 2^n combinaisons. Exacte mais inutilisable
                   au-delà d'une vingtaine de colis : sert à VÉRIFIER les deux autres.
"""

from dataclasses import dataclass, field

from tris import tri_fusion

FORCE_BRUTE_MAX = 20  # 2^20 ~ 1 million de combinaisons


def utilite_valeur(colis):
    """Critère de la partie 5 du sujet : on maximise la valeur transportée."""
    return colis.valeur


@dataclass
class Chargement:
    """Résultat d'une préparation de camion."""
    capacite: int
    colis: list = field(default_factory=list)
    methode: str = ""
    score: float = 0          # somme des utilités (= valeur totale par défaut)

    @property
    def poids_total(self):
        return sum(c.poids for c in self.colis)

    @property
    def valeur_totale(self):
        return sum(c.valeur for c in self.colis)

    @property
    def taux_remplissage(self):
        return self.poids_total / self.capacite if self.capacite else 0.0


def _verifier_capacite(capacite):
    if not isinstance(capacite, int) or isinstance(capacite, bool) or capacite < 0:
        raise ValueError("la capacité doit être un entier positif ou nul (kg)")


# ---------------------------------------------------------------------- #
# Programmation dynamique (méthode retenue)
# ---------------------------------------------------------------------- #
def sac_a_dos_dp(colis, capacite, utilite=utilite_valeur):
    """Chargement OPTIMAL par programmation dynamique.

    meilleur[w] = meilleure utilité totale possible avec une capacité de w kg,
    en n'utilisant que les colis déjà examinés. Au départ, meilleur[w] = 0.
    Pour chaque colis (poids p, utilité u), pour w de W jusqu'à p :

        meilleur[w] = max( meilleur[w],             # on ne prend pas le colis
                           meilleur[w - p] + u )    # on le prend : il reste w - p kg

    Le parcours de w en ordre DÉCROISSANT garantit que meilleur[w - p] ne
    contient pas encore le colis courant : chaque colis est pris au plus une fois.

    Pour savoir QUELS colis charger, on mémorise pour chaque colis un tableau
    d'octets pris[w] (1 si le colis améliore meilleur[w]), puis on remonte les
    décisions du dernier colis au premier en partant de w = W.

    Temps   : O(n x W).
    Mémoire : O(W) pour ``meilleur`` + n x (W + 1) octets pour les décisions.
    """
    _verifier_capacite(capacite)
    # Un colis plus lourd que le camion ne peut jamais être chargé : O(n)
    candidats = [c for c in colis if c.poids <= capacite]

    meilleur = [0] * (capacite + 1)
    decisions = []                       # liste de (colis, pris)
    for c in candidats:
        p, u = c.poids, utilite(c)
        if u <= 0:
            continue                     # un colis sans utilité n'améliore jamais rien
        pris = bytearray(capacite + 1)   # W + 1 octets, initialisés à 0
        for w in range(capacite, p - 1, -1):
            avec = meilleur[w - p] + u
            if avec > meilleur[w]:
                meilleur[w] = avec
                pris[w] = 1
        decisions.append((c, pris))

    # Reconstruction : O(n)
    selection = []
    w = capacite
    for c, pris in reversed(decisions):
        if pris[w]:
            selection.append(c)
            w -= c.poids
    selection.reverse()
    return Chargement(capacite, selection, "programmation dynamique", meilleur[capacite])


# ---------------------------------------------------------------------- #
# Glouton (heuristique, pour comparaison)
# ---------------------------------------------------------------------- #
def glouton(colis, capacite, utilite=utilite_valeur):
    """Prend les colis par rapport utilité / poids décroissant, tant qu'ils tiennent.

    Idée : charger d'abord les colis qui « rapportent le plus par kilo ».
    Tri O(n log n) + un parcours O(n). Mémoire O(n).
    NON OPTIMAL en 0/1 : un colis très rentable peut occuper une place qui
    aurait été mieux remplie par deux autres colis.
    """
    _verifier_capacite(capacite)
    ordre = tri_fusion(colis, lambda c: utilite(c) / c.poids, decroissant=True)
    restant = capacite
    selection, score = [], 0
    for c in ordre:
        if c.poids <= restant:
            selection.append(c)
            restant -= c.poids
            score += utilite(c)
    return Chargement(capacite, selection, "glouton (utilité / poids)", score)


# ---------------------------------------------------------------------- #
# Force brute (vérification)
# ---------------------------------------------------------------------- #
def force_brute(colis, capacite, utilite=utilite_valeur):
    """Essaie les 2^n sous-ensembles et garde le meilleur : O(2^n x n).

    Chaque sous-ensemble correspond à un entier « masque » de n bits : le bit i
    vaut 1 si le colis i est chargé. Réservée à n <= FORCE_BRUTE_MAX.
    """
    _verifier_capacite(capacite)
    colis = list(colis)
    if len(colis) > FORCE_BRUTE_MAX:
        raise ValueError(f"force brute limitée à {FORCE_BRUTE_MAX} colis")
    meilleur_score, meilleur_masque = 0, 0
    for masque in range(1 << len(colis)):
        poids = score = 0
        for i, c in enumerate(colis):
            if masque >> i & 1:
                poids += c.poids
                score += utilite(c)
        if poids <= capacite and score > meilleur_score:
            meilleur_score, meilleur_masque = score, masque
    selection = [c for i, c in enumerate(colis) if meilleur_masque >> i & 1]
    return Chargement(capacite, selection, "force brute", meilleur_score)
