#!/bin/sh
# Génère rapport.pdf (à la racine du projet) à partir de docs/rapport.html,
# en utilisant Google Chrome en mode sans interface (headless).
# Usage, depuis la racine du projet :  sh outils/generer_rapport.sh

set -e
RACINE="$(cd "$(dirname "$0")/.." && pwd)"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

if [ ! -x "$CHROME" ]; then
    echo "Google Chrome est introuvable : $CHROME" >&2
    exit 1
fi

"$CHROME" --headless --disable-gpu --no-pdf-header-footer \
    --print-to-pdf="$RACINE/rapport.pdf" \
    "file://$RACINE/docs/rapport.html" 2>/dev/null

echo "Rapport généré : $RACINE/rapport.pdf"
