"""Optimisation du chargement d'un camion : le problème du sac à dos 0/1.

Chaque colis est soit chargé entièrement, soit laissé (pas de fraction). On
cherche le sous-ensemble de colis de poids total <= capacité qui maximise la
somme des « utilités ». Par défaut, l'utilité d'un colis est sa valeur ; la
prise en compte de la priorité (partie 9 du rapport) remplace simplement
cette fonction (voir fabrique_utilite).

Trois méthodes :
  - sac_a_dos_dp : programmation dynamique. EXACTE (toujours optimale).
                   O(n x W) en temps et en mémoire (W = capacité en kg).
  - glouton      : tri par rapport utilité / poids. O(n log n), RAPIDE mais
                   PAS TOUJOURS OPTIMAL.
  - force_brute  : essaie les 2^n combinaisons. Exacte mais inutilisable
                   au-delà d'une vingtaine de colis : sert à VÉRIFIER les deux autres.
"""

from dataclasses import dataclass, field

from colis import PRIORITE_MAX, PRIORITE_MIN
from tris import tri_fusion

FORCE_BRUTE_MAX = 20  # 2^20 ~ 1 million de combinaisons
ALPHA_PAR_DEFAUT = 1.0

# Règles de sélection (partie 9 du rapport) : nom court -> description
REGLES = {
    "valeur": "valeur seule",
    "ponderee": "valeur pondérée par la priorité",
    "stricte": "priorité stricte",
}


def utilite_valeur(colis):
    """Critère de la partie 5 du sujet : on maximise la valeur transportée."""
    return colis.valeur


def fabrique_utilite(regle, colis=(), alpha=ALPHA_PAR_DEFAUT):
    """Renvoie la fonction d'utilité de la règle demandée.

    - "valeur"   : utilité = valeur.
    - "ponderee" : utilité = valeur x (1 + alpha x (priorité - 1) / 4).
                   Le coefficient va de 1 (priorité 1) à 1 + alpha (priorité 5) :
                   avec alpha = 1, un colis de priorité 5 « compte double » ;
                   avec alpha = 0, on retrouve exactement la règle « valeur ».
    - "stricte"  : utilité = (valeur + 1) x B^(priorité - 1), où B dépasse la
                   somme des (valeur + 1) de tous les colis. Un colis de
                   priorité p vaut alors plus que TOUS les colis de priorité
                   < p réunis : on maximise d'abord ce qui est chargé en
                   priorité 5, puis en priorité 4, etc. (ordre lexicographique).
                   « + 1 » : un colis prioritaire sans valeur compte quand même.
                   Les entiers Python n'ont pas de limite : le calcul est exact.
    ``colis`` ne sert qu'à la règle stricte (calcul de B) : O(n).
    """
    if regle == "valeur":
        return utilite_valeur
    if regle == "ponderee":
        if alpha < 0:
            raise ValueError("alpha doit être positif ou nul")
        etendue = PRIORITE_MAX - PRIORITE_MIN

        def utilite_ponderee(c):
            return c.valeur * (1 + alpha * (c.priorite - PRIORITE_MIN) / etendue)
        return utilite_ponderee
    if regle == "stricte":
        base = sum(c.valeur + 1 for c in colis) + 1

        def utilite_stricte(c):
            return (c.valeur + 1) * base ** (c.priorite - PRIORITE_MIN)
        return utilite_stricte
    raise ValueError(f"règle inconnue : {regle!r} (attendu : {', '.join(REGLES)})")


@dataclass
class Chargement:
    """Résultat d'une préparation de camion."""
    capacite: int
    colis: list = field(default_factory=list)
    methode: str = ""
    score: float = 0          # somme des utilités (= valeur totale pour la règle « valeur »)
    regle: str = REGLES["valeur"]
    candidats: int = 0        # nombre de colis réellement traités par l'algorithme (n')

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
        """Nombre de colis chargés pour chaque priorité, de la plus forte à la plus faible."""
        compte = {p: 0 for p in range(PRIORITE_MAX, PRIORITE_MIN - 1, -1)}
        for c in self.colis:
            compte[c.priorite] += 1
        return compte


def _verifier_capacite(capacite):
    if not isinstance(capacite, int) or isinstance(capacite, bool) or capacite < 0:
        raise ValueError("la capacité doit être un entier positif ou nul (kg)")


# ---------------------------------------------------------------------- #
# Élagage par dominance (pré-traitement exact, partie 10 du rapport)
# ---------------------------------------------------------------------- #
def elaguer(colis, capacite, utilite=utilite_valeur):
    """Écarte les colis qui ne peuvent appartenir à AUCUN chargement optimal.

    Un chargement valide contient au plus k = W // p colis de poids p. Pour
    chaque poids p, il suffit donc de garder les k colis de plus grande utilité.
    Preuve (argument d'échange) : si un chargement optimal contenait un colis X
    de poids p hors de ces k meilleurs, l'un des k meilleurs, Y, serait
    forcément absent du chargement (il contient au plus k colis de poids p).
    Remplacer X par Y ne change pas le poids et n'abaisse pas l'utilité : on
    obtient un chargement optimal qui n'utilise que les colis gardés.

    Colis gardés : au plus somme sur p de W // p, soit environ W x ln(poids max),
    quel que soit le nombre total de colis. Les colis trop lourds ou d'utilité
    nulle sont aussi écartés.
    Coût : O(n) pour regrouper par poids + O(n log n) au pire pour trier les
    groupes (tri fusion). Mémoire : O(n).
    """
    par_poids = {}
    for c in colis:
        if c.poids <= capacite and utilite(c) > 0:
            par_poids.setdefault(c.poids, []).append(c)
    gardes = []
    for poids, groupe in par_poids.items():
        k = capacite // poids
        if len(groupe) > k:
            groupe = tri_fusion(groupe, utilite, decroissant=True)[:k]
        gardes.extend(groupe)
    return gardes


def nombre_candidats(colis, capacite):
    """Nombre de colis gardés par l'élagage (hors colis d'utilité nulle), sans les trier.

    Le nombre gardé pour un poids p vaut min(nombre de colis de poids p, W // p) :
    il ne dépend pas de la règle de sélection. O(n). Sert à estimer le coût
    n' x (W + 1) du calcul avant de le lancer.
    """
    par_poids = {}
    for c in colis:
        if c.poids <= capacite:
            par_poids[c.poids] = par_poids.get(c.poids, 0) + 1
    return sum(min(nombre, capacite // poids) for poids, nombre in par_poids.items())


# ---------------------------------------------------------------------- #
# Programmation dynamique (méthode retenue)
# ---------------------------------------------------------------------- #
def sac_a_dos_dp(colis, capacite, utilite=utilite_valeur, avec_elagage=True):
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

    Temps   : O(n' x W), avec n' le nombre de colis candidats.
    Mémoire : O(W) pour ``meilleur`` + n' x (W + 1) octets pour les décisions.
    Sans élagage, n' = n (moins les colis trop lourds). Avec élagage (par défaut),
    n' <= somme des W // p : il ne dépend plus du nombre total de colis.
    """
    _verifier_capacite(capacite)
    if avec_elagage:
        candidats = elaguer(colis, capacite, utilite)
    else:
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
    methode = "programmation dynamique" + (" avec élagage" if avec_elagage else "")
    return Chargement(capacite, selection, methode, meilleur[capacite], candidats=len(candidats))


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


# ---------------------------------------------------------------------- #
# Point d'entrée utilisé par l'interface
# ---------------------------------------------------------------------- #
METHODES = {"dp": sac_a_dos_dp, "glouton": glouton, "force_brute": force_brute}


def preparer_camion(colis, capacite, regle="valeur", alpha=ALPHA_PAR_DEFAUT, methode="dp"):
    """Prépare un camion selon une règle de sélection et une méthode de calcul.

    La règle ne fait que fournir la fonction d'utilité : l'algorithme, sa
    complexité et sa garantie d'optimalité sont ceux de la méthode choisie.
    """
    if methode not in METHODES:
        raise ValueError(f"méthode inconnue : {methode!r} (attendu : {', '.join(METHODES)})")
    colis = list(colis)
    utilite = fabrique_utilite(regle, colis, alpha)
    resultat = METHODES[methode](colis, capacite, utilite)
    resultat.regle = REGLES[regle] + (f" (alpha = {alpha:g})" if regle == "ponderee" else "")
    return resultat
