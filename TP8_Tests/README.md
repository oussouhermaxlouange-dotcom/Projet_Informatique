# TP8 — Plan de tests et audit de sécurité

Livrable du TP8 : matrice de tests renseignée, preuves d'exécution, revue de
code et procès-verbal de recette. Les tests s'exécutent contre l'API réelle de
`../TP4_Architecture/` ; le code n'est pas dupliqué ici.

Groupe : OUSSOU Hermax, TCHEGNON Loïk, KANHONOU Ashley — encadreur MAMA Tairou.

## Contenu

| Fichier | Rôle |
|---|---|
| `tests_securite.sh` | Recharge la base TP3, démarre l'API sur le port 8086 et rejoue 14 tests (cas limites, autorisations, injection, hachage, CSRF). Écrit les preuves. |
| `matrice_tests.md` | Matrice complète : test, exigence, données, attendu écrit avant, observé, preuve. |
| `revue_code.md` | Fiche de revue : 4 remarques classées (bloquante, majeure, mineure) avec correctif et vérification. |
| `recette.md` | Procès-verbal : 5 scénarios, résultats, réserves, signatures. |
| `preuves/sorties.tsv` | Un test par ligne : exigence, cas, attendu, requête, code obtenu, conformité, corps JSON. |
| `preuves/hachages.tsv` | Contrôle des 8 empreintes de mots de passe (algorithme, longueur). |
| `preuves/resume.txt` | Synthèse : nombre de tests, conformité, état de la base. |
| `build_rapport.py` | Génère le HTML depuis les TSV, puis le PDF (Chrome) et le DOCX (UNO). |
| `build_docx.py` | Construit le DOCX avec le constructeur UNO partagé `../outils/rapport_uno.py`. |
| `tests_securite.html` / `.pdf` / `.docx` | Rapport 2 pages A4, noir et blanc. |
| `README.md` | Ce document. |

## Prérequis

| Logiciel | Version | Vérification |
|---|---|---|
| PHP | 8.1+ avec `pdo` et `pdo_mysql` | `php -m \| grep pdo_mysql` |
| MySQL / MariaDB | MySQL 8 | `mysql --version` |
| curl | 7.x | `curl --version` |
| Bash | 4+ | `bash --version` |

Le script lit `DB_SOCKET`, `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` et
`DB_PASSWORD` dans `../TP4_Architecture/.env` ; à défaut il utilise les valeurs
par défaut (`127.0.0.1:3306`, base `tp3_conventions`, utilisateur `root`).

## Rejouer les tests

```bash
cd TP8_Tests
./tests_securite.sh
```

Le script :

1. recharge `tp3_conventions` depuis `../TP3_Modele_donnees/001_schema.sql`
   puis `002_seed.sql` — la base repart d'un état connu ;
2. démarre `php -S 127.0.0.1:8086` sur `TP4_Architecture/public` ;
3. ouvre trois sessions (responsable, étudiante A, étudiante B) ;
4. exécute T-01 à T-13 et compare chaque code HTTP à l'attendu écrit dans le
   script ; deux cas relisent en plus le statut en base, un cas compare le
   nombre de lignes avant/après ;
5. écrit `preuves/sorties.tsv`, `preuves/hachages.tsv` et
   `preuves/resume.txt` ;
6. renvoie un code de sortie non nul si un test n'est pas conforme.

Résultat conservé :

```text
Tests exécutés : 14
Conformes      : 14 / 14
Empreintes     : 8 / 8 en bcrypt, 0 en clair
Base           : 7 conventions, 10 lignes d'historique
```

## Couverture

| Thème | Tests | Attendu |
|---|---|---|
| Cas limites | T-01, T-02, T-03, T-04 | 404, 422, 409, 422 |
| Autorisation | T-05, T-07, T-08 | 403, 401, 403 |
| Injection | T-06, T-09, T-09b | 404, 422, 401 |
| CSRF | T-10 | 403 `ORIGINE_REFUSEE` |
| Données hostiles | T-11, T-12 | 201 stocké tel quel, 422 sans écriture |
| Mots de passe | T-13 | 8/8 bcrypt, 0 en clair |

Les quatre cas limites exigés sont T-01 (demande inexistante), T-02 (refus sans
motif), T-03 (validation répétée) et T-04 (date invalide). Le détail des données
et des réponses est dans `matrice_tests.md`.

## Protection CSRF retenue

Trois barrières, aucune configuration CORS :

1. **Cookie de session `SameSite=Lax`** (`src/Support/Session.php`) : le
   navigateur n'envoie pas le cookie sur une requête `POST` inter-sites.
2. **API JSON sans CORS** : aucune en-tête `Access-Control-Allow-Origin`, donc
   un site tiers ne peut pas lire les réponses ni envoyer de JSON « simple »
   sans pré-vérification.
3. **Contrôle explicite de `Origin`** (`src/Support/Csrf.php`) : sur `POST`,
   `PATCH`, `PUT` et `DELETE`, si l'en-tête `Origin` est présent et diffère de
   `Host`, la réponse est `403 ORIGINE_REFUSEE` avant le routeur.

Un client sans navigateur (`curl`, script de test) n'envoie pas `Origin` : il
reste soumis à l'authentification par session. Un jeton CSRF de session n'a pas
été ajouté pour ne pas modifier le contrat du TP6 ; c'est consigné en dette
technique dans `revue_code.md`.

## Mots de passe

Les 8 comptes du jeu d'essai portent une empreinte bcrypt `$2y$10$…` de 60
caractères, produite par `password_hash()`. La vérification utilise
`password_verify()`. Le contrôle SQL
`SELECT COUNT(*) FROM utilisateur WHERE mot_de_passe_hash = 'Demo1234!'`
renvoie 0. Détail : `preuves/hachages.tsv`.

## Revue et recette

- `revue_code.md` : R-01 (identifiant de route converti en entier, bloquante,
  corrigée), R-02 (CSRF implicite, majeure, corrigée), R-03 (message de refus
  jamais affiché, mineure, corrigée), R-04 (pas de limitation des tentatives,
  majeure, acceptée avec plan). Le §5 consigne le cadre de l'échange avec le
  groupe relecteur, à compléter et à signer.
- `recette.md` : 5 scénarios (dépôt, erreurs, validation, refus, sécurité),
  tous conformes, avec le tableau de signatures à faire viser.

## Limites connues

- La limitation des tentatives de connexion n'est pas implémentée (R-04).
- Le cookie de session est `secure=false` en HTTP local ; à passer à `true`
  derrière HTTPS.
- Les tests s'exécutent sur une base locale rechargée : ils ne mesurent pas la
  charge ni la concurrence.
- Aucune donnée réelle n'est utilisée.
