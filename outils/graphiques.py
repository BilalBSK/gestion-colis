"""Trace l'évolution des temps en fonction du nombre de colis (graphiques SVG du rapport).

Lit docs/mesures/benchmark.json (produit par outils/benchmark.py) et écrit
docs/graphiques/gestion.svg et docs/graphiques/chargement.svg.
Échelles logarithmiques sur les deux axes : une droite de pente 1 correspond
à un coût O(n), une droite horizontale à un coût O(1).

Usage, depuis la racine du projet :  python3 outils/graphiques.py
"""

import json
import math
import os

RACINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ENTREE = os.path.join(RACINE, "docs", "mesures", "benchmark.json")
DOSSIER = os.path.join(RACINE, "docs", "graphiques")

# couleurs des courbes (toujours dans le même ordre), du texte et du quadrillage
SERIES = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100")
TEXTE, TEXTE_2, GRILLE, FOND = "#0b0b0b", "#52514e", "#e1e0d9", "#ffffff"
LARGEUR, HAUTEUR = 680, 420
GAUCHE, DROITE, HAUT, BAS = 70, 210, 70, 52      # marges ; celle de droite laisse la place aux étiquettes

GRAPHIQUES = {
    "gestion": [
        ("recherche_hachage", "Recherche, table de hachage", "O(1)"),
        ("recherche_sequentielle", "Recherche séquentielle", "O(n)"),
        ("tri_comptage", "Tri par priorité (comptage)", "O(n)"),
        ("tri_fusion", "Tri par poids (fusion)", "O(n log n)"),
    ],
    "chargement": [
        ("dp_sans_elagage", "DP sans élagage", "O(n.W)"),
        ("dp_avec_elagage", "DP avec élagage", "O(n log n + n'.W)"),
        ("glouton", "Glouton (non optimal)", "O(n log n)"),
    ],
}


def etiquette_temps(s):
    for seuil, unite, facteur in ((1, "s", 1), (1e-3, "ms", 1e3), (1e-6, "µs", 1e6), (0, "ns", 1e9)):
        if s >= seuil:
            v = s * facteur
            return f"{v:.0f} {unite}" if v >= 10 else f"{v:g} {unite}"
    return f"{s * 1e9:.0f} ns"


def mesure(s):
    """Valeur mesurée lisible, avec la virgule décimale : 40 ns, 537 µs, 3,2 ms, 2,03 s."""
    if s < 1e-6:
        texte = f"{s * 1e9:.0f} ns"
    elif s < 1e-3:
        texte = f"{s * 1e6:.0f} µs"
    elif s < 1:
        texte = f"{s * 1e3:.1f} ms" if s < 0.01 else f"{s * 1e3:.0f} ms"
    else:
        texte = f"{s:.2f} s"
    return texte.replace(".", ",")


def tracer(nom, series, resultats, annotation=None):
    tailles = sorted(int(n) for n in resultats)
    valeurs = [resultats[str(n)]["temps"][cle] for cle, _, _ in series for n in tailles]
    y_min = 10 ** math.floor(math.log10(min(valeurs)))
    y_max = 10 ** math.ceil(math.log10(max(valeurs)))
    x_min, x_max = math.log10(tailles[0]), math.log10(tailles[-1])
    zone_l, zone_h = LARGEUR - GAUCHE - DROITE, HAUTEUR - HAUT - BAS

    def px(n):
        return GAUCHE + (math.log10(n) - x_min) / (x_max - x_min) * zone_l

    def py(t):
        return HAUT + (math.log10(y_max) - math.log10(t)) / (math.log10(y_max) - math.log10(y_min)) * zone_h

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{LARGEUR}" height="{HAUTEUR}" '
           f'viewBox="0 0 {LARGEUR} {HAUTEUR}" font-family="Arial, Helvetica, sans-serif">',
           f'<rect width="{LARGEUR}" height="{HAUTEUR}" fill="{FOND}"/>']

    # Légende au-dessus du graphique, sur une ou deux lignes
    x, y_legende = GAUCHE, 20
    for i, (_, libelle, _) in enumerate(series):
        largeur_item = 24 + 6.6 * len(libelle) + 22
        if x + largeur_item > LARGEUR - 10:
            x, y_legende = GAUCHE, y_legende + 22
        svg.append(f'<line x1="{x}" y1="{y_legende}" x2="{x + 18}" y2="{y_legende}" stroke="{SERIES[i]}" '
                   f'stroke-width="2" stroke-linecap="round"/><circle cx="{x + 9}" cy="{y_legende}" r="4" '
                   f'fill="{SERIES[i]}" stroke="{FOND}" stroke-width="2"/>')
        svg.append(f'<text x="{x + 24}" y="{y_legende + 4}" font-size="12" fill="{TEXTE}">{libelle}</text>')
        x += largeur_item

    # Quadrillage horizontal : une ligne par puissance de 10
    decade = y_min
    while decade <= y_max * 1.0001:
        y = py(decade)
        svg.append(f'<line x1="{GAUCHE}" y1="{y:.1f}" x2="{GAUCHE + zone_l}" y2="{y:.1f}" stroke="{GRILLE}" stroke-width="1"/>')
        svg.append(f'<text x="{GAUCHE - 8}" y="{y + 4:.1f}" font-size="11" fill="{TEXTE_2}" text-anchor="end">'
                   f'{etiquette_temps(decade)}</text>')
        decade *= 10
    # Axe horizontal : les 4 niveaux du sujet
    for n in tailles:
        svg.append(f'<line x1="{px(n):.1f}" y1="{HAUT}" x2="{px(n):.1f}" y2="{HAUT + zone_h}" stroke="{GRILLE}" stroke-width="1"/>')
        svg.append(f'<text x="{px(n):.1f}" y="{HAUT + zone_h + 18}" font-size="11" fill="{TEXTE_2}" '
                   f'text-anchor="middle">{n:,}</text>'.replace(",", " "))
    svg.append(f'<text x="{GAUCHE + zone_l / 2}" y="{HAUTEUR - 10}" font-size="12" fill="{TEXTE_2}" '
               f'text-anchor="middle">Nombre de colis n (échelle logarithmique)</text>')
    svg.append(f'<text x="16" y="{HAUT + zone_h / 2}" font-size="12" fill="{TEXTE_2}" text-anchor="middle" '
               f'transform="rotate(-90 16 {HAUT + zone_h / 2})">Temps (échelle logarithmique)</text>')

    # une courbe par opération, avec un point par taille
    fins = []
    for i, (cle, libelle, complexite) in enumerate(series):
        points = [(px(n), py(resultats[str(n)]["temps"][cle])) for n in tailles]
        chemin = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
        svg.append(f'<polyline points="{chemin}" fill="none" stroke="{SERIES[i]}" stroke-width="2" '
                   f'stroke-linejoin="round" stroke-linecap="round"/>')
        for x, y in points:
            svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{SERIES[i]}" stroke="{FOND}" stroke-width="2"/>')
        fins.append([points[-1][1], points[-1][1], i, libelle, complexite,
                     resultats[str(tailles[-1])]["temps"][cle]])

    # J'écris la complexité et la dernière mesure au bout de chaque courbe, en les
    # écartant d'au moins 30 px pour qu'elles ne se chevauchent pas
    fins.sort()
    for k in range(1, len(fins)):
        fins[k][1] = max(fins[k][1], fins[k - 1][1] + 30)
    x_fin = GAUCHE + zone_l
    for y_point, y_texte, i, libelle, complexite, valeur in fins:
        if abs(y_texte - y_point) > 1:
            svg.append(f'<polyline points="{x_fin + 6},{y_point:.1f} {x_fin + 14},{y_texte:.1f} {x_fin + 20},{y_texte:.1f}" '
                       f'fill="none" stroke="{TEXTE_2}" stroke-width="1"/>')
        svg.append(f'<text x="{x_fin + 24}" y="{y_texte - 2:.1f}" font-size="12" fill="{TEXTE}">'
                   f'{complexite} : {mesure(valeur)}</text>')
        svg.append(f'<text x="{x_fin + 24}" y="{y_texte + 12:.1f}" font-size="11" fill="{TEXTE_2}">{libelle}</text>')
    if annotation:
        # remarque placée en haut à gauche, où il n'y a rien, et reliée au point concerné
        n, cle, lignes = annotation
        x, y = px(n), py(resultats[str(n)]["temps"][cle])
        y_texte = HAUT + 60
        svg.append(f'<line x1="{x:.1f}" y1="{y - 8:.1f}" x2="{x:.1f}" y2="{y_texte + 6 + 14 * (len(lignes) - 1):.1f}" '
                   f'stroke="{TEXTE_2}" stroke-width="1"/>')
        for k, texte in enumerate(lignes):
            svg.append(f'<text x="{GAUCHE + 8}" y="{y_texte + 14 * k:.1f}" font-size="11" fill="{TEXTE_2}">{texte}</text>')
    svg.append("</svg>")

    os.makedirs(DOSSIER, exist_ok=True)
    chemin = os.path.join(DOSSIER, f"{nom}.svg")
    with open(chemin, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Graphique enregistré : {os.path.relpath(chemin, RACINE)}")


def main():
    with open(ENTREE, encoding="utf-8") as f:
        resultats = json.load(f)["resultats"]
    for nom, series in GRAPHIQUES.items():
        annotation = None
        if nom == "chargement":
            annotation = (1_000, "dp_avec_elagage", ["Jusqu'à 1 000 colis, rien à élaguer :", "les deux courbes DP sont confondues"])
        tracer(nom, series, resultats, annotation)


if __name__ == "__main__":
    main()
