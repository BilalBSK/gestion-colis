"""Capture d'écran de l'exécution réelle d'une commande, pour le rapport.

La commande est exécutée depuis la racine du projet ; sa sortie est mise en
forme comme une fenêtre de terminal puis photographiée par Google Chrome
(mode sans interface). L'image est enregistrée dans docs/captures/.

Usage, depuis la racine du projet :
    python3 outils/capture.py NOM "COMMANDE"
Exemple :
    python3 outils/capture.py etape1_tests "python3 -m unittest discover -s tests -v"
"""

import html
import os
import subprocess
import sys
import tempfile

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
TAILLE_POLICE = 13      # px
HAUTEUR_LIGNE = 18      # px
LARGEUR_CARACTERE = 7.9  # px, pour Menlo 13 px

GABARIT = """<!DOCTYPE html><html><head><meta charset="utf-8"><style>
html, body {{ margin: 0; background: #fff; }}
.fenetre {{ margin: 0; border: 1px solid #9a9a9a; border-radius: 6px; overflow: hidden; }}
.barre {{ height: 24px; background: #e6e6e6; border-bottom: 1px solid #c4c4c4;
         font: 12px -apple-system, Helvetica, sans-serif; color: #444; text-align: center; line-height: 24px; position: relative; }}
.points {{ position: absolute; left: 9px; top: 6px; }}
.points span {{ display: inline-block; width: 11px; height: 11px; border-radius: 50%; margin-right: 6px; }}
pre {{ margin: 0; padding: 10px 14px; font: {police}px/{ligne}px Menlo, Monaco, monospace; color: #000; white-space: pre; }}
.invite {{ font-weight: bold; }}
</style></head><body><div class="fenetre">
<div class="barre"><div class="points"><span style="background:#fe5f57"></span><span style="background:#febc2e"></span><span style="background:#28c840"></span></div>Terminal - projet</div>
<pre>{contenu}</pre></div></body></html>"""


def executer(commande):
    resultat = subprocess.run(commande, shell=True, cwd=RACINE, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    return resultat.stdout.rstrip("\n")


def capturer(nom, commande):
    sortie = executer(commande)
    lignes = [f"$ {commande}"] + sortie.split("\n")
    contenu = ('<span class="invite">' + html.escape(lignes[0]) + "</span>\n"
               + html.escape("\n".join(lignes[1:])))
    largeur = int(max(640, max(len(l) for l in lignes) * LARGEUR_CARACTERE + 40))
    hauteur = len(lignes) * HAUTEUR_LIGNE + 24 + 22 + 2

    destination = os.path.join(RACINE, "docs", "captures", f"{nom}.png")
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(GABARIT.format(police=TAILLE_POLICE, ligne=HAUTEUR_LIGNE, contenu=contenu))
        page = f.name
    try:
        subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=2", f"--window-size={largeur},{hauteur}",
                        f"--screenshot={destination}", f"file://{page}"],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    finally:
        os.remove(page)
    print(sortie)
    print(f"\nCapture enregistrée : {os.path.relpath(destination, RACINE)}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    capturer(sys.argv[1], sys.argv[2])
