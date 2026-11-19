#!/usr/bin/env bash
# TP8 — plan de tests et audit de sécurité.
#
# Recharge la base TP3, démarre l'API sur le port 8086, puis exécute la matrice
# de tests : cas limites, autorisations, injection, hachage, CSRF.
#
# Sorties : preuves/sorties.tsv     (un test par ligne)
#           preuves/hachages.tsv    (contrôle des mots de passe en base)
#           preuves/resume.txt      (synthèse)
#
# Usage : ./tests_securite.sh
set -u
cd "$(dirname "$0")"

RACINE="$(cd .. && pwd)"
APP="$RACINE/TP4_Architecture"
PORT=8086
BASE="http://127.0.0.1:$PORT"
SORTIES=preuves/sorties.tsv
HACHAGES=preuves/hachages.tsv
RESUME=preuves/resume.txt

JAR_RESP=/tmp/tp8_resp.jar
JAR_A=/tmp/tp8_etudiant_a.jar
JAR_B=/tmp/tp8_etudiant_b.jar
CORPS=/tmp/tp8_corps.json

mkdir -p preuves

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

sql() { "${MYSQL[@]}" -B -N "$DB_NAME" -e "$1"; }

SERVEUR=""
nettoyer() {
    [[ -n "$SERVEUR" ]] && kill "$SERVEUR" >/dev/null 2>&1
    rm -f "$JAR_RESP" "$JAR_A" "$JAR_B" "$CORPS"
}
trap nettoyer EXIT

# --- Base rechargée depuis le modèle TP3 ------------------------------------
"${MYSQL[@]}" < "$RACINE/TP3_Modele_donnees/001_schema.sql" || {
    echo "Échec du chargement du schéma TP3"; exit 1; }
"${MYSQL[@]}" < "$RACINE/TP3_Modele_donnees/002_seed.sql" || {
    echo "Échec du chargement du jeu d'essai TP3"; exit 1; }

php -S "127.0.0.1:$PORT" -t "$APP/public" "$APP/public/index.php" \
    >/tmp/tp8_php.log 2>&1 &
SERVEUR=$!

pret=0
for _ in $(seq 1 30); do
    if curl -s -o /dev/null "$BASE/api/sante"; then pret=1; break; fi
    sleep 0.3
done
[[ "$pret" -eq 1 ]] || { echo "Le serveur PHP n'a pas démarré"; exit 1; }

# --- Sessions de test --------------------------------------------------------
connexion() {
    local jar=$1 email=$2
    curl -s -o /dev/null -c "$jar" -b "$jar" \
        -X POST -H 'Content-Type: application/json' \
        --data-binary "{\"email\":\"$email\",\"mot_de_passe\":\"Demo1234!\"}" \
        "$BASE/api/connexion"
}

connexion "$JAR_RESP" "responsable.pedago@univ.test"
connexion "$JAR_A" "sena.houngbo@univ.test"
connexion "$JAR_B" "ibrahim.sanni@univ.test"

# --- Matrice de tests --------------------------------------------------------
: > "$SORTIES"
printf 'test\texigence\tcas\tattendu\trequete\tobtenu\tconforme\treponse\n' > "$SORTIES"

# cas TEST EXIGENCE CAS ATTENDU(TEXTE) CODE_ATTENDU METHODE CHEMIN JAR CORPS [CONTROLE]
# CONTROLE = "id:statut" vérifie que la demande garde ce statut en base.
cas() {
    local test=$1 exigence=$2 libelle=$3 attendu=$4 code_attendu=$5
    local methode=$6 chemin=$7 jar=$8 corps=${9:-} controle=${10:-}

    local args=(-s -o "$CORPS" -w '%{http_code}' -X "$methode" "$BASE$chemin"
                -H 'Content-Type: application/json')
    [[ -n "$jar" ]] && args+=(-b "$jar" -c "$jar")
    [[ -n "$corps" ]] && args+=(--data-binary "$corps")

    local code; code="$(curl "${args[@]}")"
    local reponse; reponse="$(tr -d '\n\t' < "$CORPS")"
    local conforme=OUI

    [[ "$code" == "$code_attendu" ]] || conforme=NON

    if [[ -n "$controle" ]]; then
        local id="${controle%%:*}" statut_attendu="${controle##*:}"
        local statut_reel; statut_reel="$(sql "SELECT statut FROM convention WHERE id = $id;")"
        if [[ "$statut_reel" != "$statut_attendu" ]]; then
            conforme=NON
            reponse="statut en base = $statut_reel ; $reponse"
        fi
    fi

    printf '%s\t%s\t%s\t%s\t%s %s\t%s\t%s\t%s\n' \
        "$test" "$exigence" "$libelle" "$attendu" "$methode" "$chemin" \
        "$code" "$conforme" "$reponse" >> "$SORTIES"
}

# T-01 : cas limite — ressource inexistante.
cas T-01 EF-03 "Valider une demande inexistante (999)" "404" 404 \
    PATCH /api/demandes/999/statut "$JAR_RESP" '{"statut":"VALIDEE"}'

# T-02 : cas limite — refus sans motif, statut inchangé.
cas T-02 EF-03 "Refuser sans motif (demande 2)" "422, statut inchangé" 422 \
    PATCH /api/demandes/2/statut "$JAR_RESP" '{"statut":"REFUSEE"}' "2:SOUMISE"

# T-03 : cas limite — décision répétée sur une demande déjà validée.
cas T-03 EF-03 "Valider une demande déjà validée (3)" "409, statut inchangé" 409 \
    PATCH /api/demandes/3/statut "$JAR_RESP" '{"statut":"VALIDEE"}' "3:VALIDEE"

# T-04 : cas limite — date inexistante dans le calendrier.
cas T-04 EF-02 "Créer une demande datée du 30 février" "422" 422 \
    POST /api/demandes "$JAR_A" \
    '{"entreprise_id":1,"intitule":"Stage hors calendrier","date_debut":"2027-02-30","date_fin":"2027-05-31"}'

# T-05 : autorisation — l'étudiante B lit le dossier de l'étudiante A.
cas T-05 ENF-01 "Étudiante B lit la demande 1 (étudiante A)" "403 sans donnée" 403 \
    GET /api/demandes/1 "$JAR_B"

# T-06 : injection — identifiant non numérique.
cas T-06 ENF-01 "Identifiant « 1 OR 1=1 »" "404, aucune ligne" 404 \
    GET "/api/demandes/1%20OR%201=1" "$JAR_RESP"

# T-07 : session absente.
cas T-07 ENF-01 "Lister les demandes sans session" "401" 401 \
    GET /api/demandes "" ""

# T-08 : rôle insuffisant.
cas T-08 ENF-01 "Étudiante A tente de valider la demande 2" "403" 403 \
    PATCH /api/demandes/2/statut "$JAR_A" '{"statut":"VALIDEE"}'

# T-09 : injection SQL dans le champ e-mail.
cas T-09 ENF-01 "Connexion, e-mail « ' OR '1'='1 »" "422, jamais atteint SQL" 422 \
    POST /api/connexion "" '{"email":"'"'"' OR '"'"'1'"'"'='"'"'1","mot_de_passe":"x"}'

# T-09b : injection SQL dans le champ mot de passe.
cas T-09b ENF-01 "Connexion, mot de passe « ' OR '1'='1 »" "401" 401 \
    POST /api/connexion "" '{"email":"sena.houngbo@univ.test","mot_de_passe":"'"'"' OR '"'"'1'"'"'='"'"'1"}'

# T-10 : CSRF — écriture depuis une autre origine.
code_origine="$(curl -s -o "$CORPS" -w '%{http_code}' -X POST \
    -H 'Content-Type: application/json' -H 'Origin: http://evil.test' \
    --data-binary '{"email":"sena.houngbo@univ.test","mot_de_passe":"Demo1234!"}' \
    "$BASE/api/connexion")"
printf 'T-10\tENF-01\tÉcriture depuis une origine étrangère\t403\tPOST /api/connexion (Origin: http://evil.test)\t%s\t%s\t%s\n' \
    "$code_origine" "$([[ "$code_origine" == "403" ]] && echo OUI || echo NON)" \
    "$(tr -d '\n\t' < "$CORPS")" >> "$SORTIES"

# T-11 : données hostiles — intitulé contenant des balises.
cas T-11 ENF-02 "Créer un intitulé contenant <script>" "201, stocké tel quel" 201 \
    POST /api/demandes "$JAR_A" \
    '{"entreprise_id":1,"intitule":"<script>alert(1)</script>","date_debut":"2027-03-01","date_fin":"2027-06-30","soumettre":true}'

# T-12 : atomicité — une création invalide ne change pas le nombre de lignes.
avant="$(sql "SELECT COUNT(*) FROM convention;")"
cas T-12 ENF-02 "Création invalide : intitulé vide" "422, base inchangée" 422 \
    POST /api/demandes "$JAR_A" \
    '{"entreprise_id":1,"intitule":"   ","date_debut":"2027-03-01","date_fin":"2027-06-30"}'
apres="$(sql "SELECT COUNT(*) FROM convention;")"
if [[ "$avant" != "$apres" ]]; then
    # Corrige la dernière ligne : le nombre de conventions a bougé.
    sed -i '$ s/\tOUI\t/\tNON\t/' "$SORTIES"
    echo "T-12 : $avant conventions avant, $apres après" >> "$RESUME"
fi

# --- Contrôle des mots de passe en base --------------------------------------
printf 'email\trole\tempreinte\tlongueur\tbcrypt\n' > "$HACHAGES"
while IFS=$'\t' read -r email role empreinte longueur; do
    bcrypt=NON
    [[ "$empreinte" == \$2y\$* && "$longueur" == "60" ]] && bcrypt=OUI
    printf '%s\t%s\t%s…\t%s\t%s\n' "$email" "$role" "${empreinte:0:7}" "$longueur" "$bcrypt" >> "$HACHAGES"
done < <(sql "SELECT email, role, mot_de_passe_hash, CHAR_LENGTH(mot_de_passe_hash)
               FROM utilisateur ORDER BY id;")

hachages_conformes="$(awk -F'\t' 'NR > 1 && $5 == "OUI"' "$HACHAGES" | wc -l)"
hachages_total="$(( $(wc -l < "$HACHAGES") - 1 ))"

# Le jeu d'essai ne doit contenir aucun mot de passe en clair.
clair="$(sql "SELECT COUNT(*) FROM utilisateur WHERE mot_de_passe_hash = 'Demo1234!';")"

printf 'T-13\tENF-01\tMots de passe hachés en base (bcrypt)\t%s/%s empreintes $2y$, 0 en clair\tSELECT … FROM utilisateur\t%s/%s\t%s\t%s\n' \
    "$hachages_conformes" "$hachages_total" "$hachages_conformes" "$hachages_total" \
    "$([[ "$hachages_conformes" == "$hachages_total" && "$clair" == "0" ]] && echo OUI || echo NON)" \
    "clair: $clair ; détail: preuves/hachages.tsv" >> "$SORTIES"

# --- Synthèse -----------------------------------------------------------------
total=$(( $(wc -l < "$SORTIES") - 1 ))
conformes=$(awk -F'\t' 'NR > 1 && $7 == "OUI"' "$SORTIES" | wc -l)

{
    echo "Tests exécutés : $total"
    echo "Conformes      : $conformes / $total"
    echo "Empreintes     : $hachages_conformes / $hachages_total en bcrypt, $clair en clair"
    echo "Base           : $(sql "SELECT COUNT(*) FROM convention;") conventions, $(sql "SELECT COUNT(*) FROM historique;") lignes d'historique"
} > "$RESUME"

cat "$RESUME"
[[ "$conformes" -eq "$total" ]]
