# TP6 — tableau des six cas testés

Preuves brutes : [`../preuves/sortie_api.txt`](../preuves/sortie_api.txt)  
Script : [`../tests/tester_api.sh`](../tests/tester_api.sh)

## Protocole

```bash
# 1. Repartir du jeu d'essai TP3 (6 demandes, 8 comptes)
mysql -u root -p < ../TP3_Modele_donnees/001_schema.sql
mysql -u root -p < ../TP3_Modele_donnees/002_seed.sql

# 2. Lancer le serveur
php -S 127.0.0.1:8000 -t public public/index.php

# 3. Exécuter les six cas et conserver la sortie
./tests/tester_api.sh http://127.0.0.1:8000 | tee preuves/sortie_api.txt
```

Comptes utilisés : `sena.houngbo@univ.test` (étudiant) et
`responsable.pedago@univ.test` (responsable), mot de passe `Demo1234!`.

## Tableau des cas

| # | Cas | Requête | Attendu | Obtenu | Verdict |
|---:|---|---|---:|---:|---|
| 1 | Succès | `PATCH /api/demandes/7/statut` `{"statut":"VALIDEE"}` (responsable) | 200 | 200 | OK |
| 1 bis | Persistance | `GET /api/demandes/7` (responsable) | 200, `statut = VALIDEE` | 200, `VALIDEE` | OK |
| 2 | Corps invalide | `POST /api/demandes` corps `{"entreprise_id":` (étudiant) | 400 | 400 | OK |
| 3 | Sans session | `POST /api/demandes` sans cookie | 401 | 401 | OK |
| 4 | Rôle insuffisant | `PATCH /api/demandes/2/statut` (étudiant) | 403 | 403 | OK |
| 5 | Demande inconnue | `PATCH /api/demandes/999999/statut` (responsable) | 404 | 404 | OK |
| 6 | Transition interdite | `PATCH /api/demandes/4/statut` `REFUSEE` (déjà `VALIDEE`) | 409 | 409 | OK |

Contrôles complémentaires dans le même script : `422` (champs absents ou incohérents)
et `401` (mot de passe faux). Bilan de la sortie conservée : **14/14 réponses conformes**.

## Détail des réponses

**Cas 1 — succès.** La demande 7 est créée en `SOUMISE`, puis validée : `200` et
`"statut": "VALIDEE"`, `"date_decision"` renseignée. La relecture `GET` renvoie le même
statut : la persistance en base est prouvée, pas seulement la réponse HTTP.

**Cas 2 — 400.** Le JSON tronqué est refusé avant toute lecture métier :

```json
{"erreur":{"code":"JSON_INVALIDE","message":"Le corps de la requête doit être un objet JSON valide."}}
```

**Cas 3 — 401.** Aucun cookie de session :

```json
{"erreur":{"code":"NON_AUTHENTIFIE","message":"Authentification requise."}}
```

**Cas 4 — 403.** Un étudiant ne peut pas décider, même sur sa propre demande :

```json
{"erreur":{"code":"ROLE_NON_AUTORISE","message":"Seul le responsable pédagogique peut décider d’une demande."}}
```

**Cas 5 — 404.** Identifiant absent :

```json
{"erreur":{"code":"DEMANDE_INCONNUE","message":"Demande inconnue."}}
```

**Cas 6 — 409.** La demande 4 est déjà `VALIDEE` ; la transition vers `REFUSEE` est
refusée avec le détail des transitions possibles :

```json
{"erreur":{"code":"TRANSITION_INTERDITE","message":"Transition VALIDEE vers REFUSEE interdite.",
 "details":{"statut_actuel":"VALIDEE","statut_demande":"REFUSEE","transitions_possibles":[]}}}
```

## Transaction et rollback

Après le cas 1, la base contient deux lignes d'historique pour la demande 7 :

| `ancien_statut` | `nouveau_statut` | `auteur_id` |
|---|---|---|
| `NULL` | `SOUMISE` | 1 (étudiant) |
| `SOUMISE` | `VALIDEE` | 6 (responsable) |

Le test `tests/test_domain.php` vérifie le rollback : la mise à jour de statut est
exécutée dans une transaction, une exception est levée juste après, puis la demande est
relue. Le statut et le motif sont inchangés — la transaction n'a rien laissé en base.

## Ce que chaque cas démontre

| Critère TP6 | Preuve |
|---|---|
| Requêtes préparées et couches respectées | `DemandeRepository` (SQL) → `DemandeService` (règles) → `DemandeController` (HTTP) ; `preuves/sortie_test_domain.txt`. |
| Table des transitions et 409 | Cas 6 + tests unitaires des transitions. |
| Connexion, mot de passe haché, session régénérée | Préparation de `sortie_api.txt` : l'identifiant de session change à la connexion ; `password_verify()` vérifié dans `test_domain.php`. |
| Transaction statut puis historique, rollback | Cas 1 (deux lignes d'historique) + test de rollback. |
| Codes HTTP cohérents avec preuves | Tableau ci-dessus et `preuves/sortie_api.txt`. |
