# Justification — TP4 et TP6

1. Le code sépare `public`, `Controllers`, `Services`, `Repositories`, `Support` et `config` :
   chaque couche a une responsabilité unique et le SQL reste confiné aux dépôts.
2. La connexion PDO utilise `ERRMODE_EXCEPTION`, `EMULATE_PREPARES = false` et un délai de 3 s ;
   `tests/test_connexion.php` prouve la connexion à `tp3_conventions`.
3. `GET /api/sante` exécute un vrai `SELECT 1` et répond `200` ou `503` ; les preuves HTTP sont
   conservées dans `preuves/sortie_http.txt`.
4. Le contrat de l'API est écrit avant le code métier (`docs/contrat_api.md`), puis tenu à jour
   au TP6 avec les codes réellement renvoyés.
5. `.env` est exclu de Git et seul `.env.example` est versionné ; les erreurs PDO sont
   journalisées côté serveur et le client reçoit un message générique.

## TP6 — API des demandes

6. `DemandeRepository` expose `findById`, `findByStudent`, `findByEncadreur`, `findAll`,
   `create` et `updateStatus`, toutes en requêtes préparées. Le service ne manipule que des
   tableaux ; aucun SQL ne remonte dans les contrôleurs.
7. La table des transitions est une constante de `DemandeService` :
   `BROUILLON → SOUMISE`, `SOUMISE → VALIDEE | REFUSEE`, les états finaux n'ont aucune sortie.
   Toute autre demande lève `409 TRANSITION_INTERDITE` avec les transitions possibles.
8. L'authentification utilise `password_hash` / `password_verify` (bcrypt) et une session PHP
   dont l'identifiant est régénéré à la connexion (`session_regenerate_id(true)`).
   Le cookie est `HttpOnly`, `SameSite=Lax`, et `session.use_strict_mode` refuse un identifiant
   inconnu. Aucun mot de passe, aucun rôle n'est stocké côté navigateur.
9. La décision est atomique : `updateStatus` puis `ajouterHistorique` dans une transaction.
   Si l'une des écritures échoue, `DemandeRepository::transaction()` annule tout ; le test
   `tests/test_domain.php` le vérifie en provoquant une exception après la mise à jour.
10. Les six cas demandés (succès, 400, 401, 403, 404, 409) sont rejoués par
    `tests/tester_api.sh` et la sortie est conservée dans `preuves/sortie_api.txt`
    (14/14 réponses conformes). Le tableau de correspondance est dans
    `docs/tp6_cas_tests.md`.
