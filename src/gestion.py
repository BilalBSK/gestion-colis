"""Collection de colis.

Structure retenue : une table de hachage (dict Python) qui associe à chaque
identifiant le colis correspondant :  identifiant -> Colis.

    - ajouter un colis              : O(1) amorti
    - vérifier qu'un id est libre   : O(1) en moyenne
    - rechercher par identifiant    : O(1) en moyenne
    - parcourir tous les colis      : O(n), dans l'ordre d'insertion
      (un dict Python conserve l'ordre d'insertion depuis Python 3.7)
"""

from stockage import lire_csv


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

    def rechercher_sequentielle(self, identifiant):
        """Recherche par parcours de tous les colis : O(n).

        N'est pas utilisée par le programme : elle sert uniquement de point de
        comparaison dans l'étude des performances.
        """
        for c in self._par_id.values():
            if c.identifiant == identifiant:
                return c
        return None
