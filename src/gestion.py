"""La collection de colis.

Je range les colis dans un dictionnaire Python (une table de hachage) dont la
clé est l'identifiant. Ajouter un colis, vérifier qu'un identifiant est libre
ou retrouver un colis se fait donc en temps constant en moyenne, quel que soit
le nombre de colis. Comme un dict garde l'ordre d'insertion, je n'ai pas besoin
d'une liste à côté pour l'affichage.
"""

from colis import PRIORITE_MAX, PRIORITE_MIN
from stockage import lire_csv
from tris import tri_comptage, tri_fusion

CRITERES = ("poids", "valeur", "priorite")


class GestionColis:
    def __init__(self, colis=()):
        self._par_id = {}          # identifiant -> Colis
        self._id_max = None        # plus grand identifiant vu, pour proposer le suivant
        for c in colis:
            self.ajouter(c)

    @classmethod
    def depuis_csv(cls, chemin):
        return cls(lire_csv(chemin))

    def __len__(self):
        return len(self._par_id)

    def __iter__(self):
        return iter(self._par_id.values())

    def ajouter(self, colis):
        """Ajoute un colis, O(1) amorti. Refuse un identifiant déjà utilisé."""
        if colis.identifiant in self._par_id:
            raise ValueError(f"un colis d'identifiant {colis.identifiant} existe déjà")
        self._par_id[colis.identifiant] = colis
        if self._id_max is None or colis.identifiant > self._id_max:
            self._id_max = colis.identifiant

    def prochain_identifiant(self):
        """Identifiant libre à proposer dans le menu. O(1) car je tiens _id_max à jour."""
        return 1 if self._id_max is None else self._id_max + 1

    def lister(self):
        """Copie de la liste des colis, dans l'ordre où ils ont été ajoutés. O(n)."""
        return list(self._par_id.values())

    def rechercher(self, identifiant):
        """Colis ayant cet identifiant, ou None. O(1) en moyenne."""
        return self._par_id.get(identifiant)

    def rechercher_sequentielle(self, identifiant):
        """Même recherche en parcourant tous les colis, O(n).

        Le programme ne s'en sert pas : je la garde pour comparer les temps
        avec le dictionnaire.
        """
        for c in self._par_id.values():
            if c.identifiant == identifiant:
                return c
        return None

    def trier(self, critere, decroissant=False):
        """Renvoie une nouvelle liste triée ; la collection elle-même ne bouge pas.

        Pour le poids et la valeur j'utilise le tri fusion, O(n log n). Pour la
        priorité, qui n'a que 5 valeurs possibles, le tri par comptage, O(n).
        """
        if critere == "poids":
            return tri_fusion(self, lambda c: c.poids, decroissant)
        if critere == "valeur":
            return tri_fusion(self, lambda c: c.valeur, decroissant)
        if critere == "priorite":
            return tri_comptage(self, lambda c: c.priorite, PRIORITE_MIN, PRIORITE_MAX, decroissant)
        raise ValueError(f"critère de tri inconnu : {critere!r} (attendu : {', '.join(CRITERES)})")

    def statistiques(self):
        """Je calcule tous les indicateurs en un seul parcours de la collection, O(n)."""
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
            # destinations classées par nom pour l'affichage (peu nombreuses)
            "par_destination": {d: tuple(par_destination[d]) for d in sorted(par_destination)},
        }
