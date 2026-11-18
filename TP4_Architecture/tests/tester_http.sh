#!/usr/bin/env bash
# Vérification HTTP réelle du squelette (le serveur doit déjà tourner).
# Usage : ./tests/tester_http.sh [base_url]
set -u

BASE="${1:-http://127.0.0.1:8000}"

echo "Test HTTP — base ${BASE}"
echo "------------------------------"

for requete in "GET /api/sante" "GET /api/inconnue" "POST /api/sante"; do
    methode="${requete%% *}"
    chemin="${requete#* }"
    echo
    echo "> ${methode} ${chemin}"
    curl -sS -i -X "${methode}" "${BASE}${chemin}" | sed -n '1,12p'
done
