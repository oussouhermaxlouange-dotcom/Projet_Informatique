#!/usr/bin/env bash
# TP6 — preuves HTTP des six cas demandés.
# Prérequis : serveur lancé et base réinitialisée depuis le jeu d'essai TP3.
#   mysql -u root < ../TP3_Modele_donnees/001_schema.sql
#   mysql -u root < ../TP3_Modele_donnees/002_seed.sql
#   php -S 127.0.0.1:8000 -t public public/index.php
# Usage : ./tests/tester_api.sh [base_url]
set -u

BASE="${1:-http://127.0.0.1:8000}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

ETU="$TMP/etudiant.cookies"
RESP="$TMP/responsable.cookies"

echecs=0
total=0
DERNIER_CODE=""
DERNIER_CORPS=""

requete() {
    local libelle="$1" methode="$2" chemin="$3" cookies="$4" corps="$5" attendu="$6"

    local args=(-sS -X "$methode" -o "$TMP/derniere.json" -w '%{http_code}'
                -H 'Content-Type: application/json')
    [[ "$cookies" != "-" ]] && args+=(-b "$cookies" -c "$cookies")
    [[ "$corps" != "-" ]] && args+=(--data-binary "$corps")

    DERNIER_CODE="$(curl "${args[@]}" "$BASE$chemin" 2>/dev/null)" || DERNIER_CODE="000"
    DERNIER_CORPS="$(cat "$TMP/derniere.json" 2>/dev/null)"

    local verdict="OK"
    if [[ "$DERNIER_CODE" != "$attendu" ]]; then
        verdict="ECHEC"
        echecs=$((echecs + 1))
    fi
    total=$((total + 1))

    printf '%-52s %-6s %-28s -> %s (attendu %s)  %s\n' \
        "$libelle" "$methode" "$chemin" "$DERNIER_CODE" "$attendu" "$verdict"
    printf '    %s\n' "$DERNIER_CORPS"
}

id_depuis_reponse() {
    printf '%s' "$DERNIER_CORPS" \
        | php -r '$d = json_decode(stream_get_contents(STDIN), true);
                  echo isset($d["demande"]["id"]) ? $d["demande"]["id"] : "";'
}

cookie_id() {
    awk '$6 == "SESSID_TP6" { print $7 }' "$1" 2>/dev/null | tail -1
}

echo "TP6 — preuves HTTP de l'API des demandes"
echo "Base : $BASE"
echo "Date : $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "---------------------------------------"
echo

echo "[Préparation]"
requete "Session anonyme avant connexion" GET "/api/moi" "$ETU" "-" 401
SESSION_ANONYME="$(cookie_id "$ETU")"

requete "Connexion étudiante" POST "/api/connexion" "$ETU" \
    '{"email":"sena.houngbo@univ.test","mot_de_passe":"Demo1234!"}' 200
SESSION_CONNECTEE="$(cookie_id "$ETU")"

if [[ -n "$SESSION_ANONYME" && -n "$SESSION_CONNECTEE" && "$SESSION_ANONYME" != "$SESSION_CONNECTEE" ]]; then
    echo "    identifiant de session régénéré à la connexion : OK"
else
    echo "    identifiant de session NON régénéré : ECHEC"
    echecs=$((echecs + 1))
fi
total=$((total + 1))

requete "Dépôt d'une demande (SOUMISE)" POST "/api/demandes" "$ETU" \
    '{"entreprise_id":1,"intitule":"Suivi des tournées de collecte","date_debut":"2027-02-01","date_fin":"2027-05-31","soumettre":true}' 201
ID_DEMANDE="$(id_depuis_reponse)"

if [[ -z "$ID_DEMANDE" ]]; then
    echo "Impossible de lire l'identifiant de la demande créée : arrêt."
    exit 1
fi

requete "Connexion responsable pédagogique" POST "/api/connexion" "$RESP" \
    '{"email":"responsable.pedago@univ.test","mot_de_passe":"Demo1234!"}' 200

echo
echo "[Six cas demandés]"

requete "Cas 1 — succès : validation de la demande $ID_DEMANDE" PATCH "/api/demandes/$ID_DEMANDE/statut" "$RESP" \
    '{"statut":"VALIDEE"}' 200
requete "Cas 1 (suite) — persistance en base" GET "/api/demandes/$ID_DEMANDE" "$RESP" "-" 200

requete "Cas 2 — 400 : corps JSON illisible" POST "/api/demandes" "$ETU" \
    '{"entreprise_id":' 400

requete "Cas 3 — 401 : aucune session" POST "/api/demandes" "-" \
    '{"entreprise_id":1,"intitule":"Sans session","date_debut":"2027-02-01","date_fin":"2027-05-31"}' 401

requete "Cas 4 — 403 : étudiant qui décide" PATCH "/api/demandes/2/statut" "$ETU" \
    '{"statut":"VALIDEE"}' 403

requete "Cas 5 — 404 : demande inconnue" PATCH "/api/demandes/999999/statut" "$RESP" \
    '{"statut":"VALIDEE"}' 404

requete "Cas 6 — 409 : demande déjà validée" PATCH "/api/demandes/4/statut" "$RESP" \
    '{"statut":"REFUSEE","motif":"Hors délai"}' 409

echo
echo "[Contrôles complémentaires]"

requete "422 : champs absents ou incohérents" POST "/api/demandes" "$ETU" \
    '{"entreprise_id":999}' 422

requete "401 : mot de passe incorrect" POST "/api/connexion" "-" \
    '{"email":"sena.houngbo@univ.test","mot_de_passe":"faux"}' 401

echo
echo "---------------------------------------"
if [[ "$echecs" -eq 0 ]]; then
    echo "Bilan : $total/$total réponses conformes."
    exit 0
fi

echo "Bilan : $((total - echecs))/$total réponses conformes, $echecs échec(s)."
exit 1
