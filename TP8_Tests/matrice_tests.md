# Matrice de tests — TP8

Projet informatique 2 · L3 SIL — application de gestion des stages  
Groupe : OUSSOU Hermax, TCHEGNON Loïk, KANHONOU Ashley — encadreur MAMA Tairou  
Date d'exécution : 18 novembre 2026 — MySQL 8.0.46, PHP 8.3, API réelle

## 1. Méthode

Chaque ligne a été écrite **avant** l'exécution : l'attendu et le code HTTP
attendu figurent dans le script `tests_securite.sh` sous forme de paramètres du
cas. Le script recharge la base depuis `../TP3_Modele_donnees/001_schema.sql`
puis `002_seed.sql`, démarre l'API sur `127.0.0.1:8086`, joue les cas et compare
le code obtenu à l'attendu. Une différence rend la ligne non conforme et le
script renvoie un code de sortie non nul.

Deux contrôles vont au-delà du code HTTP :

- **état de la base** : après un refus sans motif ou une validation répétée, le
  statut de la demande est relu en SQL et doit être inchangé ;
- **comptage** : une création invalide ne doit pas augmenter le nombre de lignes
  de `convention`.

Colonnes : `T-xx` = numéro du cas ; « Attendu » = valeur écrite avant
exécution ; « Observé » = valeur réellement obtenue ; « Preuve » = ligne du
fichier de sorties.

## 2. Matrice (14 cas)

| Test | Exigence | Données | Attendu (écrit avant) | Observé | Preuve |
|---|---|---|---|---|---|
| T-01 | EF-03 | `PATCH /api/demandes/999/statut` avec `{"statut":"VALIDEE"}`, session responsable | **404**, code `DEMANDE_INCONNUE`, aucune écriture | 404 `DEMANDE_INCONNUE` | `preuves/sorties.tsv` T-01 |
| T-02 | EF-03 | `PATCH /api/demandes/2/statut` avec `{"statut":"REFUSEE"}` **sans motif** | **422** `VALIDATION`, statut en base toujours `SOUMISE` | 422, statut `SOUMISE` | `preuves/sorties.tsv` T-02 |
| T-03 | EF-03 | `PATCH /api/demandes/3/statut` avec `{"statut":"VALIDEE"}` sur une demande déjà `VALIDEE` | **409** `TRANSITION_INTERDITE`, statut inchangé | 409, statut `VALIDEE` | `preuves/sorties.tsv` T-03 |
| T-04 | EF-02 | `POST /api/demandes` avec `"date_debut":"2027-02-30"` | **422** `VALIDATION`, aucune ligne créée | 422, champ `date_debut` signalé | `preuves/sorties.tsv` T-04 |
| T-05 | ENF-01 | Session étudiante B (`ibrahim.sanni@…`), `GET /api/demandes/1` (dossier de l'étudiante A) | **403** `ACCES_REFUSE`, aucun contenu du dossier | 403 `ACCES_REFUSE` | `preuves/sorties.tsv` T-05 |
| T-06 | ENF-01 | `GET /api/demandes/1%20OR%201=1`, session responsable | **404** `DEMANDE_INCONNUE`, aucune ligne retournée | 404, corps `DEMANDE_INCONNUE` | `preuves/sorties.tsv` T-06 |
| T-07 | ENF-01 | `GET /api/demandes` **sans cookie de session** | **401** `NON_AUTHENTIFIE` | 401 `NON_AUTHENTIFIE` | `preuves/sorties.tsv` T-07 |
| T-08 | ENF-01 | Session étudiante A, `PATCH /api/demandes/2/statut` avec `{"statut":"VALIDEE"}` | **403** `ROLE_NON_AUTORISE` | 403 `ROLE_NON_AUTORISE` | `preuves/sorties.tsv` T-08 |
| T-09 | ENF-01 | `POST /api/connexion` avec `"email":"' OR '1'='1"` | **422** : l'e-mail est rejeté avant tout SQL | 422, champ `email` signalé | `preuves/sorties.tsv` T-09 |
| T-09b | ENF-01 | `POST /api/connexion` avec `"mot_de_passe":"' OR '1'='1"` | **401** `IDENTIFIANTS_INVALIDES`, aucune session | 401 `IDENTIFIANTS_INVALIDES` | `preuves/sorties.tsv` T-09b |
| T-10 | ENF-01 | `POST /api/connexion` avec `Origin: http://evil.test` | **403** `ORIGINE_REFUSEE`, aucune session créée | 403 `ORIGINE_REFUSEE` | `preuves/sorties.tsv` T-10 |
| T-11 | ENF-02 | `POST /api/demandes` avec `"intitule":"<script>alert(1)</script>"` | **201**, valeur stockée telle quelle (l'échappement est du ressort de l'affichage) | 201, demande créée | `preuves/sorties.tsv` T-11 |
| T-12 | ENF-02 | `POST /api/demandes` avec `"intitule":"   "` | **422**, nombre de `convention` inchangé | 422, base inchangée | `preuves/sorties.tsv` T-12 |
| T-13 | ENF-01 | `SELECT mot_de_passe_hash FROM utilisateur` (8 comptes) | **8/8** empreintes `$2y$` de 60 caractères, **0** mot de passe en clair | 8/8 bcrypt, 0 en clair | `preuves/hachages.tsv` |

Résultat : **14 tests exécutés, 14 conformes**. Synthèse dans
`preuves/resume.txt`.

## 3. Les quatre cas limites exigés

| Cas limite | Test | Réponse | Ce que le test prouve |
|---|---|---|---|
| Demande inexistante | T-01 | 404 | Aucun accès à une ressource absente, aucune création implicite. |
| Refus sans motif | T-02 | 422 + statut inchangé | La règle métier « motif obligatoire » est portée par le serveur, pas seulement par l'interface ; l'absence d'écriture est vérifiée en base. |
| Validation répétée | T-03 | 409 + statut inchangé | Les états `VALIDEE` et `REFUSEE` sont terminaux ; la table des transitions fait foi. |
| Date invalide | T-04 | 422 | Le 30 février est refusé par la validation serveur, pas seulement par le champ `type="date"` du navigateur. |

## 4. Autorisation et injection

- **Étudiante B vers dossier de A (T-05)** : la session de B est valide, la
  demande 1 existe, et la réponse est malgré tout `403 ACCES_REFUSE` sans corps
  utile. Le contrôle est fait dans `DemandeService` après lecture, sur
  `etudiant_utilisateur_id`.
- **Étudiante A qui tente de décider (T-08)** : `403 ROLE_NON_AUTORISE` ; le
  rôle est vérifié côté serveur à chaque requête, jamais à partir d'un paramètre
  client.
- **Chaîne `1 OR 1=1` (T-06, T-09, T-09b)** : comme identifiant de route, elle
  est rejetée par `ctype_digit()` avant tout appel au dépôt (`404`). Dans le
  champ e-mail, elle est rejetée par `FILTER_VALIDATE_EMAIL` (`422`) ; dans le
  mot de passe, `password_verify()` échoue (`401`). Aucun de ces chemins ne
  construit de SQL par concaténation : les requêtes sont préparées avec
  `PDO::ATTR_EMULATE_PREPARES => false`.

## 5. Mots de passe et CSRF

- **Hachage** : les 8 comptes du jeu d'essai portent une empreinte bcrypt
  (`$2y$10$…`, 60 caractères). Le contrôle `mot_de_passe_hash = 'Demo1234!'`
  renvoie 0 ligne. Détail : `preuves/hachages.tsv`.
- **CSRF** : cookie de session `SameSite=Lax`, API JSON sans CORS, et contrôle
  explicite de l'en-tête `Origin` sur `POST`, `PATCH`, `PUT`, `DELETE`
  (`src/Support/Csrf.php`). Une écriture venue d'un autre site reçoit
  `403 ORIGINE_REFUSEE` avant le routeur. Un client sans navigateur (`curl`) est
  dispensé du contrôle d'origine mais reste soumis à l'authentification.

## 6. Reproduire

```bash
cd TP8_Tests
./tests_securite.sh
```

Le script recharge la base, démarre l'API sur le port 8086, écrit
`preuves/sorties.tsv`, `preuves/hachages.tsv` et `preuves/resume.txt`, puis
affiche :

```text
Tests exécutés : 14
Conformes      : 14 / 14
Empreintes     : 8 / 8 en bcrypt, 0 en clair
Base           : 7 conventions, 10 lignes d'historique
```
