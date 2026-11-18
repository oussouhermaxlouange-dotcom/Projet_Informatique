# API de gestion des stages — TP4 à TP6

**Projet informatique 2 · L3 SIL**  
Application Web de gestion des stages et des soutenances  
Membres : OUSSOU Hermax, TCHEGNON Loïk, KANHONOU Ashley  
Encadreur : MAMA Tairou — version 2.0 — 18/11/2026

## Objectif

Ce dossier contient le socle technique (TP4) et l'API des demandes (TP6) : arborescence
en couches, configuration locale, connexion PDO, authentification par session, création
et décision d'une demande avec table des transitions et transaction.

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
```

Sur un poste où MySQL n'écoute qu'en socket Unix, renseigner `DB_SOCKET` et laisser
`DB_HOST` / `DB_PORT` inchangés : le socket est prioritaire.

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

Aucun privilège `DROP`, `ALTER` ni `GRANT` n'est accordé : le compte applicatif ne peut
que lire et modifier les données, pas changer le schéma.

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

Les sorties conservées sont dans `preuves/` :

- `sortie_api.txt` — six cas TP6 avec codes et corps JSON
- `sortie_test_domain.txt` — transitions, requêtes préparées, rollback
- `sortie_test_connexion.txt`, `sortie_test_sante.txt`, `sortie_test_sante_503.txt`, `sortie_test_routes.txt`
- `sortie_http.txt` — en-têtes HTTP réels

## Arborescence

```text
TP4_Architecture/
├── public/
│   ├── index.php          # point d'entrée unique
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
│   ├── Support/           # routeur, requête, réponse, session, .env
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

## Suite

- TP7 : interface et intégration (pages étudiant et responsable, appels `fetch`,
  affichage avec `textContent`).
