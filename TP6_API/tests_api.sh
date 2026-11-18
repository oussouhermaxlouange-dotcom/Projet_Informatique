#!/usr/bin/env bash
# TP6 — rejoue les cas de test contre la base tp3_conventions et l'API réelle.
# Sorties : preuves/sorties.tsv (un cas par ligne), preuves/etat_base.tsv,
#           preuves/capture_api.png
# Usage : ./tests_api.sh
#
# Le script recharge la base depuis le jeu d'essai TP3 avant chaque exécution,
# puis démarre le serveur PHP intégré sur le port 8082.
set -u
cd "$(dirname "$0")"

RACINE="$(cd .. && pwd)"
APP="$RACINE/TP4_Architecture"
PORT=8082
BASE="http://127.0.0.1:$PORT"
SORTIES=preuves/sorties.tsv
ETAT=preuves/etat_base.tsv
JAR_RESP=/tmp/tp6_hermax_resp.jar
JAR_ETU=/tmp/tp6_hermax_etu.jar
JAR_VIDE=/tmp/tp6_hermax_vide.jar
CORPS=/tmp/tp6_hermax_corps

mkdir -p preuves

# --- Configuration de la base : reprise du .env de l'application -------------
lire_env() {
    grep -E "^$1=" "$APP/.env" 2>/dev/null | head -1 | cut -d= -f2-
}

DB_SOCKET="$(lire_env DB_SOCKET)"
DB_HOST="$(lire_env DB_HOST)"; DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="$(lire_env DB_PORT)"; DB_PORT="${DB_PORT:-3306}"
DB_NAME="$(lire_env DB_NAME)"; DB_NAME="${DB_NAME:-tp3_conventions}"
DB_USER="$(lire_env DB_USER)"; DB_USER="${DB_USER:-root}"
DB_PASSWORD="$(lire_env DB_PASSWORD)"

MYSQL=(mysql -u "$DB_USER")
if [[ -n "$DB_SOCKET" ]]; then
    MYSQL+=(--socket="$DB_SOCKET")
else
    MYSQL+=(-h "$DB_HOST" -P "$DB_PORT")
fi
[[ -n "$DB_PASSWORD" ]] && MYSQL+=("-p$DB_PASSWORD")

SERVEUR=""
nettoyer() {
    [[ -n "$SERVEUR" ]] && kill "$SERVEUR" >/dev/null 2>&1
    rm -f "$JAR_RESP" "$JAR_ETU" "$JAR_VIDE" "$CORPS"
}
trap nettoyer EXIT

# --- Base rechargée depuis le modèle TP3 ------------------------------------
"${MYSQL[@]}" < "$RACINE/TP3_Modele_donnees/001_schema.sql" || {
    echo "Échec du chargement du schéma TP3"; exit 1; }
"${MYSQL[@]}" < "$RACINE/TP3_Modele_donnees/002_seed.sql" || {
    echo "Échec du chargement du jeu d'essai TP3"; exit 1; }

# --- Serveur ----------------------------------------------------------------
php -S "127.0.0.1:$PORT" -t "$APP/public" "$APP/public/index.php" \
    >/tmp/tp6_hermax_php.log 2>&1 &
SERVEUR=$!

pret=0
for _ in $(seq 1 30); do
    if curl -s -o /dev/null "$BASE/api/sante"; then pret=1; break; fi
    sleep 0.3
done
[[ "$pret" -eq 1 ]] || { echo "Le serveur PHP n'a pas démarré"; exit 1; }

# --- Cas de test -------------------------------------------------------------
: > "$SORTIES"
printf 'numero\tcas\tattendu\trequete\tobtenu\tconforme\treponse\n' > "$SORTIES"

# appel NUMERO LIBELLE ATTENDU METHODE CHEMIN JAR [CORPS_JSON]
appel() {
    local num=$1 lib=$2 attendu=$3 methode=$4 chemin=$5 jar=$6 corps=${7:-}
    local args=(-s -o "$CORPS" -w '%{http_code}' -X "$methode" "$BASE$chemin"
                -H 'Content-Type: application/json')
    [[ -n "$jar" ]] && args+=(-b "$jar" -c "$jar")
    [[ -n "$corps" ]] && args+=(--data-binary "$corps")

    local obtenu; obtenu="$(curl "${args[@]}")"
    local reponse; reponse="$(tr -d '\n\t' < "$CORPS")"
    local conforme=NON; [[ "$obtenu" == "$attendu" ]] && conforme=OUI
    printf '%s\t%s\t%s\t%s %s\t%s\t%s\t%s\n' \
        "$num" "$lib" "$attendu" "$methode" "$chemin" "$obtenu" "$conforme" "$reponse" >> "$SORTIES"
}

appel S1  "Connexion du responsable pédagogique" 200 POST /api/connexion "$JAR_RESP" \
    '{"email":"responsable.pedago@univ.test","mot_de_passe":"Demo1234!"}'
appel S2  "Connexion de l'étudiante Sènami HOUNGBO" 200 POST /api/connexion "$JAR_ETU" \
    '{"email":"sena.houngbo@univ.test","mot_de_passe":"Demo1234!"}'
appel S3  "Connexion avec un mauvais mot de passe" 401 POST /api/connexion "$JAR_VIDE" \
    '{"email":"sena.houngbo@univ.test","mot_de_passe":"faux"}'
appel S4  "Création et soumission d'une demande par l'étudiante" 201 POST /api/demandes "$JAR_ETU" \
    '{"entreprise_id":1,"intitule":"Suivi des tournées de collecte","date_debut":"2027-02-01","date_fin":"2027-05-31","soumettre":true}'

# Les six cas exigés par le sujet.
appel S5  "Succès : le responsable valide la demande 7 (SOUMISE vers VALIDEE)" 200 PATCH /api/demandes/7/statut "$JAR_RESP" \
    '{"statut":"VALIDEE"}'
appel S6  "Erreur 400 : corps JSON illisible" 400 POST /api/demandes "$JAR_ETU" \
    '{"entreprise_id":'
appel S7  "Erreur 401 : aucune session" 401 PATCH /api/demandes/2/statut "$JAR_VIDE" \
    '{"statut":"VALIDEE"}'
appel S8  "Erreur 403 : l'étudiante tente de valider" 403 PATCH /api/demandes/2/statut "$JAR_ETU" \
    '{"statut":"VALIDEE"}'
appel S9  "Erreur 404 : demande inexistante (999)" 404 PATCH /api/demandes/999/statut "$JAR_RESP" \
    '{"statut":"VALIDEE"}'
appel S10 "Erreur 409 : valider une demande déjà validée (demande 4)" 409 PATCH /api/demandes/4/statut "$JAR_RESP" \
    '{"statut":"REFUSEE","motif":"Hors délai"}'

# Contrôles complémentaires.
appel S11 "Refus motivé par le responsable (demande 2)" 200 PATCH /api/demandes/2/statut "$JAR_RESP" \
    '{"statut":"REFUSEE","motif":"Convention incomplète"}'
appel S12 "Liste de toutes les demandes par le responsable" 200 GET /api/demandes "$JAR_RESP"
appel S13 "Liste des demandes de l'étudiante (ses dossiers uniquement)" 200 GET /api/demandes "$JAR_ETU"
appel S14 "Entreprise inconnue à la création" 422 POST /api/demandes "$JAR_ETU" \
    '{"entreprise_id":999,"intitule":"Test entreprise inconnue","date_debut":"2027-02-01","date_fin":"2027-05-31"}'

# --- État de la base après les cas ------------------------------------------
"${MYSQL[@]}" -B "$DB_NAME" -e \
    "SELECT id, etudiant_id, statut, IFNULL(motif_refus, 'NULL') AS motif_refus,
            IFNULL(date_decision, 'NULL') AS date_decision
       FROM convention ORDER BY id;" > "$ETAT"
"${MYSQL[@]}" -B -N "$DB_NAME" -e \
    "SELECT 'lignes_historique', COUNT(*) FROM historique;" >> "$ETAT"

# --- Capture réelle de /api/sante (comme dans un navigateur) ----------------
if command -v google-chrome >/dev/null 2>&1; then
    google-chrome --headless --disable-gpu --no-sandbox --hide-scrollbars \
        --window-size=900,260 --screenshot="$PWD/preuves/capture_api.png" \
        "$BASE/api/sante" >/dev/null 2>&1
fi

total=$(( $(wc -l < "$SORTIES") - 1 ))
conformes=$(awk -F'\t' 'NR > 1 && $6 == "OUI"' "$SORTIES" | wc -l)
echo "sorties   : $total cas (preuves/sorties.tsv)"
echo "conformes : $conformes / $total"
echo "base      : $(awk -F'\t' 'NR > 1 && $1 == "lignes_historique" { exit } NR > 1 && $1 ~ /^[0-9]+$/ { n++ } END { print n + 0 }' "$ETAT") demandes"

[[ "$conformes" -eq "$total" ]]
