"""Collection de colis.

Structure retenue : une table de hachage (dict Python) qui associe à chaque
identifiant le colis correspondant :  identifiant -> Colis.

    - ajouter un colis              : O(1) amorti
    - vérifier qu'un id est libre   : O(1) en moyenne
    - rechercher par identifiant    : O(1) en moyenne
    - parcourir tous les colis      : O(n), dans l'ordre d'insertion
      (un dict Python conserve l'ordre d'insertion depuis Python 3.7)
    - trier                         : voir trier(), O(n log n) ou O(n)
    - statistiques                  : un seul parcours, O(n)
"""

from colis import PRIORITE_MAX, PRIORITE_MIN
from stockage import lire_csv
from tris import tri_comptage, tri_fusion

# Critères de tri proposés (fonctionnalités 4, 5 et 6, plus un tri combiné)
CRITERES = ("poids", "valeur", "priorite", "priorite_valeur")


class GestionColis:
    def __init__(self, colis=()):
        self._par_id = {}          # identifiant -> Colis
        self._id_max = None        # plus grand identifiant, tenu à jour à chaque ajout
        for c in colis:
            self.ajouter(c)

    @classmethod
    def depuis_csv(cls, chemin):
        """Crée une collection à partir d'un fichier CSV. O(n)."""
        return cls(lire_csv(chemin))

    def __len__(self):
        return len(self._par_id)

    def __iter__(self):
        """Parcours des colis dans l'ordre d'insertion. O(n) au total."""
        return iter(self._par_id.values())

    # ------------------------------------------------------------------ #
    # Fonctionnalité 1 : ajouter un colis
    # ------------------------------------------------------------------ #
    def ajouter(self, colis):
        """Ajoute un colis à la collection.

        Lève ValueError si l'identifiant est déjà utilisé (deux colis ne
        doivent jamais partager un identifiant, sinon la recherche serait
        ambiguë). Test d'appartenance et insertion : O(1) amorti.
        """
        if colis.identifiant in self._par_id:
            raise ValueError(f"un colis d'identifiant {colis.identifiant} existe déjà")
        self._par_id[colis.identifiant] = colis
        if self._id_max is None or colis.identifiant > self._id_max:
            self._id_max = colis.identifiant

    def prochain_identifiant(self):
        """Premier identifiant libre au-delà du plus grand utilisé. O(1)."""
        return 1 if self._id_max is None else self._id_max + 1

    # ------------------------------------------------------------------ #
    # Fonctionnalité 2 : afficher les colis
    # ------------------------------------------------------------------ #
    def lister(self):
        """Liste des colis dans l'ordre d'insertion. O(n) en temps et en mémoire."""
        return list(self._par_id.values())

    # ------------------------------------------------------------------ #
    # Fonctionnalité 3 : rechercher un colis
    # ------------------------------------------------------------------ #
    def rechercher(self, identifiant):
        """Renvoie le colis d'identifiant donné, ou None s'il n'existe pas.

        Table de hachage : l'identifiant est haché pour trouver directement la
        case où le colis est rangé, sans parcourir la collection.
        O(1) en moyenne, O(n) dans le pire cas théorique (collisions).
        """
        return self._par_id.get(identifiant)

    # ------------------------------------------------------------------ #
    # Fonctionnalités 4, 5 et 6 : trier par poids, valeur, priorité
    # ------------------------------------------------------------------ #
    def trier(self, critere, decroissant=False):
        """Renvoie une nouvelle liste des colis triés selon ``critere``.

        La collection elle-même n'est pas modifiée : elle garde l'ordre
        d'insertion, et l'on peut demander plusieurs tris successifs.

        - "poids", "valeur" : tri fusion, O(n log n) en temps, O(n) en mémoire ;
        - "priorite"        : tri par comptage, O(n + 5) = O(n) ;
        - "priorite_valeur" : priorité, puis valeur pour départager les colis de
          même priorité. On trie d'abord par valeur (tri fusion), puis par
          priorité avec un tri STABLE (comptage) : au sein d'une même priorité,
          l'ordre des valeurs obtenu au premier tri est conservé. O(n log n).
        """
        if critere == "poids":
            return tri_fusion(self, lambda c: c.poids, decroissant)
        if critere == "valeur":
            return tri_fusion(self, lambda c: c.valeur, decroissant)
        if critere == "priorite":
            return tri_comptage(self, lambda c: c.priorite, PRIORITE_MIN, PRIORITE_MAX, decroissant)
        if critere == "priorite_valeur":
            par_valeur = tri_fusion(self, lambda c: c.valeur, decroissant)
            return tri_comptage(par_valeur, lambda c: c.priorite, PRIORITE_MIN, PRIORITE_MAX, decroissant)
        raise ValueError(f"critère de tri inconnu : {critere!r} (attendu : {', '.join(CRITERES)})")

    # ------------------------------------------------------------------ #
    # Statistiques (option 7 du menu)
    # ------------------------------------------------------------------ #
    def statistiques(self):
        """Indicateurs sur la collection, calculés en UN SEUL parcours : O(n).

        Mémoire : O(k + d), avec k = 5 priorités et d = nombre de destinations
        distinctes (compteurs). Les destinations sont ensuite classées par nom :
        O(d log d), négligeable car d est petit devant n.
        """
        n = len(self._par_id)
        poids_total = valeur_totale = 0
        plus_lourd = plus_leger = plus_precieux = None
        par_priorite = {p: 0 for p in range(PRIORITE_MIN, PRIORITE_MAX + 1)}
        par_destination = {}  # destination -> [nombre, poids, valeur]
        for c in self._par_id.values():
            poids_total += c.poids
            valeur_totale += c.valeur
            if plus_lourd is None or c.poids > plus_lourd.poids:
                plus_lourd = c
            if plus_leger is None or c.poids < plus_leger.poids:
                plus_leger = c
            if plus_precieux is None or c.valeur > plus_precieux.valeur:
                plus_precieux = c
            par_priorite[c.priorite] += 1
            totaux = par_destination.setdefault(c.destination, [0, 0, 0])
            totaux[0] += 1
            totaux[1] += c.poids
            totaux[2] += c.valeur
        return {
            "nombre": n,
            "poids_total": poids_total,
            "valeur_totale": valeur_totale,
            "poids_moyen": poids_total / n if n else 0.0,
            "valeur_moyenne": valeur_totale / n if n else 0.0,
            "plus_lourd": plus_lourd,
            "plus_leger": plus_leger,
            "plus_precieux": plus_precieux,
            "par_priorite": par_priorite,
            "par_destination": {d: tuple(par_destination[d]) for d in sorted(par_destination)},
        }

    def rechercher_sequentielle(self, identifiant):
        """Recherche par parcours de tous les colis : O(n).

        N'est pas utilisée par le programme : elle sert uniquement de point de
        comparaison dans l'étude des performances.
        """
        for c in self._par_id.values():
            if c.identifiant == identifiant:
                return c
        return None
