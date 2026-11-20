# API et interface de gestion des stages — TP4 à TP9

**Projet informatique 2 · L3 SIL**  
Application Web de gestion des stages et des soutenances  
Membres : OUSSOU Hermax, TCHEGNON Loïk, KANHONOU Ashley  
Encadreur : MAMA Tairou — version 2.4 — 20/11/2026

## Objectif

Ce dossier contient le socle technique (TP4), l'API des demandes (TP6), l'interface
Web (TP7) et la procédure de déploiement (TP9) : arborescence en couches,
configuration locale, connexion PDO, authentification par session, création et décision
d'une demande avec table des transitions et transaction, puis écrans étudiante et
responsable alimentés en `fetch`. Les preuves et rapports des TP6, TP7, TP8 et TP9 sont
regroupés dans `../TP6_API/`, `../TP7_Frontend/`, `../TP8_Tests/` et
`../TP9_Deploiement/`.

Le modèle de données est celui du TP3 : base `tp3_conventions`, tables `convention` et
`historique`.

## Prérequis

- PHP 8.1 ou supérieur, avec les extensions `pdo_mysql` et `session`
- MySQL 8 ou MariaDB
- Git
- Un navigateur et `curl` pour les vérifications

Sous Ubuntu :

```bash
php -v
php -m | grep -E 'PDO|pdo_mysql'
```

Si MySQL n'écoute qu'en socket Unix, vérifier d'abord que le fichier existe **sur ce
poste** ; un socket recopié d'une autre machine provoque un `503` (voir
`../TP9_Deploiement/ticket_incident.md`) :

```bash
mysqladmin --socket=/var/run/mysqld/mysqld.sock ping
test -S /var/run/mysqld/mysqld.sock && echo "socket présent"
```

## Installation

1. Créer la configuration locale à partir du modèle :

```bash
cp .env.example .env
```

2. Renseigner `.env` (ne jamais versionner ce fichier) :

```ini
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=tp3_conventions
DB_USER=tp4_app
DB_PASSWORD=...
# Socket Unix optionnel : s'il est renseigné, il remplace host/port.
DB_SOCKET=
```

Sur un poste où MySQL n'écoute qu'en socket Unix, renseigner `DB_SOCKET` et laisser
`DB_HOST` / `DB_PORT` inchangés : le socket est prioritaire. Le chemin doit être celui
du poste courant ; un socket absent provoque
`SQLSTATE[HY000] [2002] No such file or directory` et un `503` sur `/api/sante`.

3. Charger le schéma et le jeu d'essai du TP3 (données fictives) :

```bash
mysql -u root -p < ../TP3_Modele_donnees/001_schema.sql
mysql -u root -p < ../TP3_Modele_donnees/002_seed.sql
```

Comptes de démonstration (mot de passe commun `Demo1234!`) :

| Rôle | E-mail |
|---|---|  
| Étudiant | `sena.houngbo@univ.test` |
| Encadreur | `sylvain.kiki@univ.test` |
| Responsable | `responsable.pedago@univ.test` |
| Admin | `admin.siege@univ.test` |

4. Pour un compte applicatif dédié, créer un utilisateur limité à cette base plutôt que
d'utiliser `root` :

```bash
mysql -u root -p <<'SQL'
CREATE USER IF NOT EXISTS 'tp4_app'@'localhost' IDENTIFIED BY 'mot_de_passe_local';
GRANT SELECT, INSERT, UPDATE, DELETE ON tp3_conventions.* TO 'tp4_app'@'localhost';
FLUSH PRIVILEGES;
SQL
```

Aucun privilège `DROP`, `CREATE`, `ALTER` ni `GRANT` n'est accordé : le compte applicatif
ne peut que lire et modifier les données, pas changer le schéma. Contrôle :

```bash
mysql -u tp4_app -p -e 'SHOW GRANTS FOR CURRENT_USER();'
mysql -u tp4_app -p -e 'DROP TABLE tp3_conventions.historique;'   # doit échouer en 1142
```

Le TP9 a utilisé le même principe avec le compte `tp9_app` : voir
`../TP9_Deploiement/preuves/compte_sql.txt`.

5. Démarrer le serveur, puis contrôler la santé et la connexion :

```bash
php -S 127.0.0.1:8000 -t public public/index.php
curl -i http://127.0.0.1:8000/api/sante
```

Un `503` signifie que la base n'est pas joignable : lire le journal PHP, puis vérifier
`.env`, le socket et les droits du compte **avant** de modifier le code.

Pour remplacer un mot de passe de démonstration, générer une empreinte bcrypt :

```bash
php tools/hacher_mot_de_passe.php 'NouveauMotDePasse'
```

## Lancement local

```bash
php -S 127.0.0.1:8000 -t public public/index.php
```

Vérification :

```bash
curl -i http://127.0.0.1:8000/api/sante
curl -i -c cookies.txt -H 'Content-Type: application/json' \
     -d '{"email":"sena.houngbo@univ.test","mot_de_passe":"Demo1234!"}' \
     http://127.0.0.1:8000/api/connexion
```

Réponse de santé attendue lorsque la base est joignable :

```json
{"statut":"ok","base":"ok","horodatage":"2026-11-18T13:25:04+00:00"}
```

Avec Apache, le `DocumentRoot` doit pointer sur `public/` ; le fichier `.htaccess`
réécrit toutes les requêtes vers `index.php`.

## Sauvegarde et restauration

Sauvegarde cohérente, sans bloquer les écritures, avec les routines et déclencheurs :

```bash
mysqldump -u root -p --single-transaction --routines --triggers \
          tp3_conventions > tp3_conventions_$(date +%F).sql
sha256sum tp3_conventions_$(date +%F).sql
```

La restauration se **teste toujours sur une base dédiée**, jamais directement sur la
base de production :

```bash
mysql -u root -p -e "CREATE DATABASE tp3_conventions_restauration \
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p tp3_conventions_restauration < tp3_conventions_2026-11-20.sql
```

Puis comparer les comptages des deux bases :

```sql
SELECT 'utilisateur' AS table_name, COUNT(*) FROM tp3_conventions.utilisateur
UNION ALL SELECT 'convention', COUNT(*) FROM tp3_conventions.convention
UNION ALL SELECT 'historique', COUNT(*) FROM tp3_conventions.historique;
```

Une sauvegarde n'est fiable qu'après une restauration réussie et des `COUNT(*)`
identiques. Résultat du TP9 : **9/9 tables identiques** (preuve :
`../TP9_Deploiement/preuves/restauration.txt`). Le test de reprise complet, y compris la
suppression volontaire d'une table, est décrit dans
`../TP9_Deploiement/README.md`.

## Routes

| Méthode | Chemin | Rôle | Accès |
|---|---|---|---|
| `GET` | `/api/sante` | Vérifier l'application et la base. | Public |
| `POST` | `/api/connexion` | Ouvrir une session. | Public |
| `POST` | `/api/deconnexion` | Fermer la session. | Session |
| `GET` | `/api/moi` | Profil connecté. | Session |
| `GET` | `/api/demandes` | Lister selon le rôle. | Session |
| `GET` | `/api/demandes/{id}` | Détail d'une demande. | Session + droits |
| `POST` | `/api/demandes` | Créer et soumettre une demande (EF-02). | Étudiant |
| `PATCH` | `/api/demandes/{id}/statut` | Valider ou refuser (EF-03). | Responsable |

Détail des corps, codes et règles : [`docs/contrat_api.md`](docs/contrat_api.md).
Tableau des six cas testés : [`docs/tp6_cas_tests.md`](docs/tp6_cas_tests.md).

## Tests et preuves

```bash
php tests/test_connexion.php     # PDO
php tests/test_sante.php         # route de santé, sans HTTP
php tests/test_routes.php        # routeur et 401/404/405
php tests/test_domain.php        # transitions, dépôt, rollback
./tests/tester_api.sh http://127.0.0.1:8000   # six cas HTTP (serveur lancé)
./tests/tester_http.sh http://127.0.0.1:8000  # en-têtes HTTP de base
```

Interface et audit :

```bash
# scénario TP7 (captures et vérification XSS)
cat ../TP7_Frontend/scenario.md
# matrice TP8 : 14 tests, autorisations, injection, hachage, CSRF
cd ../TP8_Tests && ./tests_securite.sh
```

Les sorties conservées sont dans `preuves/` :

- `sortie_api.txt` — six cas TP6 avec codes et corps JSON
- `sortie_test_domain.txt` — transitions, requêtes préparées, rollback
- `sortie_test_connexion.txt`, `sortie_test_sante.txt`, `sortie_test_sante_503.txt`, `sortie_test_routes.txt`
- `sortie_http.txt` — en-têtes HTTP réels

## Interface Web

L'interface est servie par la même application, sans duplication :

- `GET /` renvoie `public/index.html` ;
- `public/assets/` contient `app.css`, `api.js`, `rendu.js`, `app.js` et `favicon.svg` ;
- `public/preuves/` contient les pages de preuve `erreurs.html` et `xss.html` ;
- `public/index.php` laisse le serveur servir les fichiers réels et réserve les routes
  `/api/...` au routeur JSON.

L'interface reprend les maquettes `Maquette /` et propose six écrans reliés aux routes
existantes : **Connexion**, **Mes demandes**, **Nouvelle convention**, **Détail de la
convention**, **Dossiers à traiter** et **Décision de convention**. Le responsable
dispose d'une recherche par étudiant, entreprise ou intitulé et de filtres Tous /
En attente / Validés / Refusés ; la décision est un écran complet, sans fenêtre
modale, avec le motif obligatoire en cas de refus. Les données sont celles réellement
fournies par l'API ; les pièces jointes, signatures et informations de rémunération
visibles sur certaines maquettes ne sont pas prises en charge par cette version.
Les valeurs dynamiques sont rendues avec `textContent` ; `assets/rendu.js` ne contient
aucun `innerHTML`. Direction visuelle : fond ivoire, cartes blanches, accent violet,
boutons noirs, polices locales Inter et Lato. Le détail du parcours, de
l'accessibilité et des preuves TP7 est dans
[`../TP7_Frontend/README.md`](../TP7_Frontend/README.md).

## Arborescence

```text
TP4_Architecture/
├── public/
│   ├── index.php          # point d'entrée unique + fichiers statiques
│   ├── index.html         # interface (TP7)
│   ├── assets/            # CSS, JS, favicon
│   ├── preuves/           # pages de preuve erreurs et XSS
│   └── .htaccess          # réécriture Apache
├── src/
│   ├── Controllers/       # adaptation HTTP, aucune requête SQL
│   │   ├── AuthController.php
│   │   ├── DemandeController.php
│   │   └── HealthController.php
│   ├── Services/          # règles métier
│   │   ├── AuthService.php
│   │   ├── DemandeService.php
│   │   └── HealthService.php
│   ├── Repositories/      # accès aux données (PDO, SQL)
│   │   ├── Database.php
│   │   ├── DatabaseIndisponibleException.php
│   │   ├── DemandeRepository.php
│   │   └── UtilisateurRepository.php
│   ├── Support/           # routeur, requête, réponse, session, CSRF, .env
│   └── autoload.php       # autoload PSR-4 minimal
├── config/
│   ├── database.php       # paramètres lus depuis .env
│   └── routes.php         # table des routes
├── tests/                 # vérifications sans framework de test
├── tools/                 # génération d'empreintes bcrypt
├── docs/
│   ├── contrat_api.md     # contrat complet de l'API
│   ├── tp6_cas_tests.md   # tableau des six cas
│   ├── ADR-001-monolithe-php.md
│   └── justification.md
├── preuves/               # sorties de tests conservées
├── .env.example
└── .gitignore
```

## Rôle des couches

| Couche | Responsabilité | Interdits |
|---|---|---|
| `public/` | Recevoir la requête, appeler le routeur, envoyer la réponse, traduire les exceptions. | SQL, règles métier. |
| `Controllers` | Lire la requête, appeler un service, choisir le code HTTP. | SQL, calcul métier complexe. |
| `Services` | Authentification, transitions, validation, orchestration des transactions. | SQL direct, `header()`. |
| `Repositories` | Exécuter les requêtes préparées, gérer les transactions, retourner des tableaux. | Décisions HTTP, sortie HTML. |
| `Support` | Routeur, requête, réponse JSON, session, chargement de `.env`. | Règles métier. |
| `config/` | Fournir la configuration et les routes. | Secrets versionnés. |

## Sécurité

- `.env` est exclu par `.gitignore` ; seul `.env.example` est versionné, avec des valeurs factices.
- Mots de passe en bcrypt (`password_hash` / `password_verify`), jamais en clair.
- Session : cookie `HttpOnly`, `SameSite=Lax`, `use_strict_mode`, identifiant régénéré à
  la connexion.
- Requêtes préparées avec `PDO::ATTR_EMULATE_PREPARES => false` ; aucun SQL dans les contrôleurs.
- Les erreurs PDO sont journalisées côté serveur ; le client reçoit `503 BASE_INDISPONIBLE`
  ou `500 ERREUR_INTERNE` sans détail technique.
- Décision dans une transaction : `UPDATE convention` puis `INSERT historique`, rollback
  complet en cas d'échec.
- CSRF : `SameSite=Lax`, API JSON sans CORS et contrôle de `Origin` sur les écritures
  (`src/Support/Csrf.php` → `403 ORIGINE_REFUSEE`).
- Identifiants de route validés par `ctype_digit()` : `12abc` ou `1 OR 1=1` répondent
  `404` avant tout SQL.
- Rendu de l'interface par `textContent` uniquement : aucune balise reçue de l'API n'est
  interprétée.
- Aucune donnée réelle : uniquement le jeu fictif du TP3.

## Livrables TP4

- [x] Arborescence `public`, `src/Controllers`, `src/Services`, `src/Repositories`, `config`, `tests`
- [x] `.env.example`, `.gitignore` excluant `.env`, `README` avec les prérequis
- [x] Connexion PDO avec exceptions et test de connexion
- [x] Contrat des routes (`docs/contrat_api.md`)
- [x] `GET /api/sante` fonctionnelle et testée
- [x] ADR-001 (`docs/ADR-001-monolithe-php.md`)
- [x] Preuves d'exécution (`preuves/`)

## Livrables TP6

- [x] `DemandeRepository` : `findById`, `findByStudent`, `create`, `updateStatus` en requêtes préparées
- [x] Table des transitions et refus `409` des transitions interdites
- [x] Connexion : mot de passe haché, vérification, régénération de l'identifiant de session
- [x] Validation dans une transaction (statut puis historique) avec rollback
- [x] Six cas testés avec sorties : succès, 400, 401, 403, 404, 409
- [x] Tableau récapitulatif : `docs/tp6_cas_tests.md`

## Livrables TP7

- [x] Parcours des deux rôles : `../TP7_Frontend/parcours.svg` / `.png`
- [x] Formulaire accessible (étiquettes liées, aide, zone d'erreur, `aria-invalid`)
- [x] Appels `fetch` et erreurs 400, 401, 403, 404, 409, 422, 500, 503 lisibles
- [x] Liste rendue avec `textContent`, test des balises documenté
- [x] Scénario complet sur six écrans : créer, consulter, filtrer, valider, refuser, persistance (13 captures)

## Livrables TP8

- [x] Matrice de 14 tests avec attendu écrit avant : `../TP8_Tests/matrice_tests.md`
- [x] Quatre cas limites, autorisation B → A, chaîne `1 OR 1=1`
- [x] Mots de passe hachés vérifiés (8/8 bcrypt) et protection CSRF décrite
- [x] Revue de code : 4 remarques classées (`../TP8_Tests/revue_code.md`)
- [x] Recette : 5 scénarios et procès-verbal (`../TP8_Tests/recette.md`)

## Livrables TP9

- [x] Installation reproductible sur un second poste, en suivant uniquement le README
- [x] Compte SQL dédié `tp9_app` : `SELECT, INSERT, UPDATE, DELETE` sur `tp3_conventions`
- [x] Refus vérifiés de `DROP` et `CREATE` (`ERROR 1142`)
- [x] `/api/sante` à `200` et connexion étudiante fonctionnelle
- [x] Sauvegarde `mysqldump` : 23 961 octets, SHA-256 consigné
- [x] Restauration sur base de test : 9/9 tables identiques après suppression d'une table
- [x] README complété (socket, droits, sauvegarde) et ticket INC-001 reproductible

## Suite

- TP9 : livré dans `../TP9_Deploiement/` (protocole, preuves, ticket d'incident).
- TP10 : dossier de livraison et soutenance ; voir `../TP10_Soutenance/`.
