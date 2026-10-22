"""Algorithmes de tri, implémentés à la main.

  - tri_fusion    : tri par comparaison, stable, O(n log n) dans tous les cas,
                    O(n) de mémoire supplémentaire. Utilisé pour le poids et la valeur.
  - tri_comptage  : tri sans comparaison pour des clés entières dans un petit
                    intervalle [cle_min, cle_max] : O(n + k) avec k = taille de
                    l'intervalle. Utilisé pour la priorité (k = 5).
  - tri_insertion : O(n²). N'est pas utilisé par le programme : il sert de
                    référence « naïve » dans l'étude des performances.

Les trois fonctions renvoient une NOUVELLE liste (l'entrée n'est pas modifiée)
et sont STABLES : deux éléments de même clé restent dans leur ordre d'origine.
"""


def _avant(a, b, decroissant):
    """Vrai si la clé a peut être placée avant la clé b sans briser la stabilité.

    En cas d'égalité on répond Vrai : l'élément de gauche (arrivé en premier)
    reste devant. C'est ce qui rend le tri stable, dans les deux sens.
    """
    return a >= b if decroissant else a <= b


# ---------------------------------------------------------------------- #
# Tri fusion
# ---------------------------------------------------------------------- #
def tri_fusion(elements, cle=None, decroissant=False):
    """Trie ``elements`` selon ``cle`` par la méthode « diviser pour régner ».

    1. Diviser : on coupe la liste en deux moitiés.
    2. Régner  : on trie chaque moitié (appel récursif).
    3. Combiner: on fusionne les deux moitiés triées en une seule liste triée.

    Il y a log2(n) niveaux de découpage, et chaque niveau fusionne au total
    n éléments : O(n log n) en temps, quel que soit l'ordre initial.
    Mémoire : un tampon de n cases partagé par toutes les fusions (O(n)),
    plus la pile des appels récursifs (O(log n)).

    Les clés sont calculées une seule fois par élément (n appels à ``cle``),
    puis déplacées avec les éléments.
    """
    items = list(elements)
    n = len(items)
    if n < 2:
        return items
    cles = [cle(x) for x in items] if cle is not None else list(items)
    tampon_items = [None] * n
    tampon_cles = [None] * n

    def trier(debut, fin):
        """Trie la tranche [debut, fin[ de ``items`` (et ``cles`` en parallèle)."""
        if fin - debut < 2:
            return                       # 0 ou 1 élément : déjà trié
        milieu = (debut + fin) // 2
        trier(debut, milieu)
        trier(milieu, fin)
        fusionner(debut, milieu, fin)

    def fusionner(debut, milieu, fin):
        """Fusionne les tranches triées [debut, milieu[ et [milieu, fin[ : O(fin - debut)."""
        i, j, k = debut, milieu, debut
        # Tant que les deux moitiés ont des éléments, on prend le plus petit des deux en tête
        while i < milieu and j < fin:
            if _avant(cles[i], cles[j], decroissant):
                tampon_items[k], tampon_cles[k] = items[i], cles[i]
                i += 1
            else:
                tampon_items[k], tampon_cles[k] = items[j], cles[j]
                j += 1
            k += 1
        # Une des deux moitiés est épuisée : on recopie le reste de l'autre
        while i < milieu:
            tampon_items[k], tampon_cles[k] = items[i], cles[i]
            i += 1
            k += 1
        while j < fin:
            tampon_items[k], tampon_cles[k] = items[j], cles[j]
            j += 1
            k += 1
        # Le résultat de la fusion remplace la tranche d'origine
        items[debut:fin] = tampon_items[debut:fin]
        cles[debut:fin] = tampon_cles[debut:fin]

    trier(0, n)
    return items


# ---------------------------------------------------------------------- #
# Tri par comptage
# ---------------------------------------------------------------------- #
def tri_comptage(elements, cle, cle_min, cle_max, decroissant=False):
    """Trie des éléments dont la clé est un entier de [cle_min, cle_max].

    On prépare un « seau » (une liste) par valeur de clé possible, on range
    chaque élément dans le seau de sa clé, dans l'ordre d'arrivée (stabilité),
    puis on vide les seaux dans l'ordre croissant (ou décroissant) des clés.
    Aucune comparaison entre éléments : O(n + k) en temps et en mémoire,
    avec k = cle_max - cle_min + 1.
    """
    seaux = [[] for _ in range(cle_max - cle_min + 1)]
    for x in elements:                       # n étapes
        c = cle(x)
        if not cle_min <= c <= cle_max:
            raise ValueError(f"clé {c} hors de l'intervalle [{cle_min}, {cle_max}]")
        seaux[c - cle_min].append(x)
    if decroissant:
        seaux.reverse()                      # k étapes
    resultat = []
    for seau in seaux:                       # n + k étapes au total
        resultat.extend(seau)
    return resultat


# ---------------------------------------------------------------------- #
# Tri par insertion (référence pour la comparaison)
# ---------------------------------------------------------------------- #
def tri_insertion(elements, cle=None, decroissant=False):
    """Insère chaque élément à sa place dans la partie déjà triée : O(n²).

    Sert uniquement de point de comparaison dans l'étude des performances.
    """
    items = list(elements)
    cles = [cle(x) for x in items] if cle is not None else list(items)
    for i in range(1, len(items)):
        item, c = items[i], cles[i]
        j = i - 1
        # On décale vers la droite les éléments qui doivent passer après c
        while j >= 0 and not _avant(cles[j], c, decroissant):
            items[j + 1], cles[j + 1] = items[j], cles[j]
            j -= 1
        items[j + 1], cles[j + 1] = item, c
    return items
