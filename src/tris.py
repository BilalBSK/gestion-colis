"""Les tris, que j'ai écrits à la main.

  - tri_fusion    : O(n log n) dans tous les cas, pour le poids et la valeur.
  - tri_comptage  : O(n + k) pour des clés entières entre cle_min et cle_max,
                    pour la priorité (k = 5 valeurs possibles).
  - tri_insertion : O(n²), pas utilisé par le programme ; il me sert seulement
                    de point de comparaison dans les mesures.

Les trois renvoient une nouvelle liste et sont stables : deux éléments de même
clé restent dans leur ordre de départ.
"""


def _avant(a, b, decroissant):
    """Vrai si a peut passer avant b. En cas d'égalité je réponds vrai, ce qui
    laisse devant l'élément arrivé en premier : c'est ce qui rend les tris stables."""
    return a >= b if decroissant else a <= b


def tri_fusion(elements, cle=None, decroissant=False):
    """Tri fusion : je coupe la liste en deux, je trie chaque moitié, puis je
    fusionne les deux moitiés triées.

    Il y a log2(n) niveaux de découpage, et à chaque niveau n éléments sont
    fusionnés en tout : O(n log n), quel que soit l'ordre de départ. Je crée
    les tampons une seule fois (O(n) de mémoire) et je ne calcule la clé
    qu'une fois par élément.
    """
    items = list(elements)
    n = len(items)
    if n < 2:
        return items
    cles = [cle(x) for x in items] if cle is not None else list(items)
    tampon_items = [None] * n
    tampon_cles = [None] * n

    def trier(debut, fin):
        """Trie items[debut:fin] (et cles en parallèle)."""
        if fin - debut < 2:
            return                       # 0 ou 1 élément : déjà trié
        milieu = (debut + fin) // 2
        trier(debut, milieu)
        trier(milieu, fin)
        fusionner(debut, milieu, fin)

    def fusionner(debut, milieu, fin):
        """Fusionne items[debut:milieu] et items[milieu:fin], déjà triés."""
        i, j, k = debut, milieu, debut
        # je prends à chaque fois le plus petit des deux éléments de tête
        while i < milieu and j < fin:
            if _avant(cles[i], cles[j], decroissant):
                tampon_items[k], tampon_cles[k] = items[i], cles[i]
                i += 1
            else:
                tampon_items[k], tampon_cles[k] = items[j], cles[j]
                j += 1
            k += 1
        # une moitié est vide : je recopie la fin de l'autre
        while i < milieu:
            tampon_items[k], tampon_cles[k] = items[i], cles[i]
            i += 1
            k += 1
        while j < fin:
            tampon_items[k], tampon_cles[k] = items[j], cles[j]
            j += 1
            k += 1
        # je remets le résultat à sa place dans items
        items[debut:fin] = tampon_items[debut:fin]
        cles[debut:fin] = tampon_cles[debut:fin]

    trier(0, n)
    return items


def tri_comptage(elements, cle, cle_min, cle_max, decroissant=False):
    """Tri par comptage, pour des clés entières entre cle_min et cle_max.

    Un seau par valeur possible : chaque élément va dans le seau de sa clé, dans
    l'ordre où il arrive, puis je vide les seaux dans l'ordre. Il n'y a aucune
    comparaison entre éléments, d'où O(n + k) avec k = cle_max - cle_min + 1.
    """
    seaux = [[] for _ in range(cle_max - cle_min + 1)]
    for x in elements:
        c = cle(x)
        if not cle_min <= c <= cle_max:
            raise ValueError(f"clé {c} hors de l'intervalle [{cle_min}, {cle_max}]")
        seaux[c - cle_min].append(x)
    if decroissant:
        seaux.reverse()
    resultat = []
    for seau in seaux:
        resultat.extend(seau)
    return resultat


def tri_insertion(elements, cle=None, decroissant=False):
    """Chaque élément est inséré à sa place dans la partie déjà triée : O(n²)."""
    items = list(elements)
    cles = [cle(x) for x in items] if cle is not None else list(items)
    for i in range(1, len(items)):
        item, c = items[i], cles[i]
        j = i - 1
        # je décale vers la droite ceux qui doivent passer après c
        while j >= 0 and not _avant(cles[j], c, decroissant):
            items[j + 1], cles[j + 1] = items[j], cles[j]
            j -= 1
        items[j + 1], cles[j + 1] = item, c
    return items
