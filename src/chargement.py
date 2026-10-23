"""Préparation d'un camion : le problème du sac à dos 0/1.

Un colis est chargé en entier ou laissé. Je cherche les colis dont le poids
total ne dépasse pas la capacité W et dont la somme des « utilités » est la
plus grande. Sans priorité, l'utilité d'un colis est sa valeur ; avec la
priorité, c'est sa valeur multipliée par un coefficient (voir utilite()).

J'ai écrit trois méthodes :
  - sac_a_dos_dp : programmation dynamique, toujours optimale, O(n x W).
                   C'est celle que le programme utilise.
  - glouton      : tri par utilité / poids, O(n log n). Rapide mais pas
                   toujours optimal, je m'en sers pour comparer.
  - force_brute  : essaie les 2^n combinaisons. Elle me sert seulement à
                   vérifier les deux autres sur de petits exemples.
"""

from dataclasses import dataclass, field

from colis import PRIORITE_MAX, PRIORITE_MIN
from tris import tri_fusion

FORCE_BRUTE_MAX = 20     # 2^20 ~ 1 million de combinaisons, au-delà c'est trop long
ALPHA_PAR_DEFAUT = 1.0   # avec alpha = 1, un colis de priorité 5 compte double


def utilite_valeur(colis):
    return colis.valeur


def utilite(alpha=0.0):
    """Renvoie la fonction d'utilité que le chargement va maximiser.

        utilité = valeur x (1 + alpha x (priorité - 1) / 4)

    Le coefficient va de 1 (priorité 1) à 1 + alpha (priorité 5). Avec
    alpha = 0, je maximise seulement la valeur ; plus alpha est grand, plus
    les colis prioritaires passent devant. J'ai choisi de multiplier la valeur
    plutôt que de lui ajouter un bonus : un colis prioritaire mais sans valeur
    ne prend pas la place d'un colis utile.
    """
    if alpha < 0:
        raise ValueError("alpha doit être positif ou nul")
    if alpha == 0:
        return utilite_valeur
    etendue = PRIORITE_MAX - PRIORITE_MIN

    def utilite_ponderee(c):
        return c.valeur * (1 + alpha * (c.priorite - PRIORITE_MIN) / etendue)
    return utilite_ponderee


def description_regle(alpha):
    return "valeur seule" if alpha == 0 else f"valeur pondérée par la priorité (alpha = {alpha:g})"


@dataclass
class Chargement:
    """Résultat de la préparation d'un camion."""
    capacite: int
    colis: list = field(default_factory=list)
    methode: str = ""
    score: float = 0          # somme des utilités (égale à la valeur totale si alpha = 0)
    alpha: float = 0.0
    candidats: int = 0        # nombre de colis réellement traités par l'algorithme

    @property
    def poids_total(self):
        return sum(c.poids for c in self.colis)

    @property
    def valeur_totale(self):
        return sum(c.valeur for c in self.colis)

    @property
    def taux_remplissage(self):
        return self.poids_total / self.capacite if self.capacite else 0.0

    @property
    def priorite_moyenne(self):
        return sum(c.priorite for c in self.colis) / len(self.colis) if self.colis else 0.0

    @property
    def par_priorite(self):
        """Nombre de colis chargés pour chaque priorité, de 5 à 1."""
        compte = {p: 0 for p in range(PRIORITE_MAX, PRIORITE_MIN - 1, -1)}
        for c in self.colis:
            compte[c.priorite] += 1
        return compte


def _verifier_capacite(capacite):
    if not isinstance(capacite, int) or isinstance(capacite, bool) or capacite < 0:
        raise ValueError("la capacité doit être un entier positif ou nul (en kg)")


def elaguer(colis, capacite, u=utilite_valeur):
    """Ne garde, pour chaque poids p, que les W // p colis de plus grande utilité.

    Un camion de W kg ne peut pas contenir plus de W // p colis de poids p.
    Si un chargement optimal contenait un colis X de poids p qui n'est pas
    parmi ces W // p meilleurs, l'un des meilleurs (Y) en serait forcément
    absent ; en échangeant X et Y, le poids reste le même et l'utilité ne baisse
    pas. Il y a donc toujours un optimum qui n'utilise que les colis gardés.

    Je retire aussi les colis trop lourds ou sans utilité. Il reste au plus
    W // 1 + W // 2 + ... + W // 30 colis (environ 4 x W), quel que soit n.
    Coût : O(n) pour regrouper par poids, O(n log n) au pire pour trier les groupes.
    """
    par_poids = {}
    for c in colis:
        if c.poids <= capacite and u(c) > 0:
            par_poids.setdefault(c.poids, []).append(c)
    gardes = []
    for poids, groupe in par_poids.items():
        k = capacite // poids
        if len(groupe) > k:
            groupe = tri_fusion(groupe, u, decroissant=True)[:k]
        gardes.extend(groupe)
    return gardes


def nombre_candidats(colis, capacite):
    """Nombre de colis que l'élagage va garder, calculé sans trier (O(n)).

    Le menu s'en sert pour estimer la taille du calcul avant de le lancer.
    """
    par_poids = {}
    for c in colis:
        if c.poids <= capacite:
            par_poids[c.poids] = par_poids.get(c.poids, 0) + 1
    return sum(min(nombre, capacite // poids) for poids, nombre in par_poids.items())


def sac_a_dos_dp(colis, capacite, u=utilite_valeur, avec_elagage=True):
    """Chargement optimal par programmation dynamique.

    meilleur[w] est la meilleure utilité possible avec w kg de place, en ne
    regardant que les colis déjà traités. Pour chaque colis (poids p, utilité v),
    je parcours w de W jusqu'à p :

        meilleur[w] = max(meilleur[w], meilleur[w - p] + v)
                          (sans le colis)  (avec le colis)

    Je parcours w en décroissant pour que meilleur[w - p] ne compte pas déjà le
    colis courant : sinon il pourrait être pris deux fois.

    Pour retrouver les colis choisis, je garde pour chaque colis un tableau
    d'octets pris[w], puis je remonte du dernier colis au premier depuis w = W.
    Un octet par case prend bien moins de place qu'un nombre Python.

    Temps : O(n x W). Mémoire : O(W) + n x (W + 1) octets.
    Avec l'élagage, n devient le nombre de colis gardés.
    """
    _verifier_capacite(capacite)
    if avec_elagage:
        candidats = elaguer(colis, capacite, u)
    else:
        candidats = [c for c in colis if c.poids <= capacite]

    meilleur = [0] * (capacite + 1)
    decisions = []                       # (colis, pris)
    for c in candidats:
        p, v = c.poids, u(c)
        if v <= 0:
            continue                     # un colis sans valeur n'améliore jamais rien
        pris = bytearray(capacite + 1)
        for w in range(capacite, p - 1, -1):
            avec = meilleur[w - p] + v
            if avec > meilleur[w]:
                meilleur[w] = avec
                pris[w] = 1
        decisions.append((c, pris))

    # Remontée des décisions : O(n)
    selection = []
    w = capacite
    for c, pris in reversed(decisions):
        if pris[w]:
            selection.append(c)
            w -= c.poids
    selection.reverse()
    methode = "programmation dynamique" + (" avec élagage" if avec_elagage else "")
    return Chargement(capacite, selection, methode, meilleur[capacite], candidats=len(candidats))


def glouton(colis, capacite, u=utilite_valeur):
    """Prend les colis du plus « rentable au kilo » au moins rentable, tant qu'ils rentrent.

    O(n log n) à cause du tri. Pas toujours optimal : un colis très rentable
    peut prendre une place qui aurait été mieux utilisée par d'autres. Je ne
    l'utilise que pour comparer avec la programmation dynamique.
    """
    _verifier_capacite(capacite)
    ordre = tri_fusion(colis, lambda c: u(c) / c.poids, decroissant=True)
    restant = capacite
    selection, score = [], 0
    for c in ordre:
        if c.poids <= restant:
            selection.append(c)
            restant -= c.poids
            score += u(c)
    return Chargement(capacite, selection, "glouton", score)


def force_brute(colis, capacite, u=utilite_valeur):
    """Teste les 2^n combinaisons, chacune codée par un entier de n bits. O(2^n x n)."""
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
                score += u(c)
        if poids <= capacite and score > meilleur_score:
            meilleur_score, meilleur_masque = score, masque
    selection = [c for i, c in enumerate(colis) if meilleur_masque >> i & 1]
    return Chargement(capacite, selection, "force brute", meilleur_score)


METHODES = {"dp": sac_a_dos_dp, "glouton": glouton, "force_brute": force_brute}


def preparer_camion(colis, capacite, alpha=0.0, methode="dp"):
    """Prépare un camion. alpha règle l'importance de la priorité (0 = valeur seule)."""
    if methode not in METHODES:
        raise ValueError(f"méthode inconnue : {methode!r}")
    resultat = METHODES[methode](list(colis), capacite, utilite(alpha))
    resultat.alpha = alpha
    return resultat
