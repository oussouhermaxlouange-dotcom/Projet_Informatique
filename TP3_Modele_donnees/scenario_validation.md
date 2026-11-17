# Scénario de validation — « Confirmer une convention »

Ce scénario décrit le cas d'utilisation **Confirmer une demande** du diagramme
de cas d'utilisation. Il s'applique à une convention au statut `SOUMISE`.
Le cas **Refuser une demande** suit le même chemin ; seule l'étape 5 change
(un motif devient obligatoire).

| # | Acteur ou composant | Action | Échec possible | Code HTTP |
|---|---|---|---|---|
| 1 | Contrôleur `ConventionController` | Vérifier la session | Session absente ou expirée | `401` |
| 2 | `ConventionRepository::findById` | Charger la convention | Identifiant inconnu | `404` |
| 3 | `ConventionService` | Vérifier le rôle (`RESPONSABLE` ou `ADMIN`) | Rôle insuffisant (étudiant, développeur) | `403` |
| 4 | `ConventionService` | Vérifier la transition `SOUMISE → VALIDEE` | Convention déjà validée ou refusée | `409` |
| 5 | `ConventionService` | Vérifier la décision | Date de décision absente ; refus sans motif | `400` |
| 6 | `ConventionRepository` | `UPDATE` du statut + `INSERT` dans `historique`, dans une transaction | Erreur SQL, contrainte violée | `500` + `ROLLBACK` |
| 7 | `ConventionController` | Renvoyer la convention mise à jour | — | `200` |

## Règles vérifiées

- **Authentification** : toute action passe par `Se connecter` (`<<include>>`
  dans le diagramme) ; sans session, la réponse est `401` avant toute lecture.
- **Autorisation** : un étudiant ne peut pas confirmer sa propre convention ;
  le contrôle de rôle précède le contrôle d'état pour ne pas révéler
  l'existence d'un dossier à un utilisateur non habilité (`403`).
- **Transition** : `SOUMISE` est le seul état d'entrée acceptable. Une
  convention `BROUILLON` doit d'abord être soumise ; une convention déjà
  `VALIDEE` ou `REFUSEE` renvoie `409`.
- **Atomicité** : le changement de statut et la ligne d'historique sont écrits
  dans la même transaction. Si l'`INSERT` échoue, l'`UPDATE` est annulé
  (`500` + `ROLLBACK`) : aucun statut sans trace.
- **Motif** : un refus sans motif est refusé à la fois par le service (`400`)
  et par la contrainte `ck_convention_motif` de la base.

## Exemple de réponse `200`

```json
{
  "id": 3,
  "statut": "VALIDEE",
  "date_decision": "2026-10-22T16:00:00",
  "encadreur_id": 1,
  "historique_id": 3
}
```

## Exemple de réponse `409`

```json
{
  "erreur": "TRANSITION_INTERDITE",
  "message": "La convention 3 est déjà au statut VALIDEE.",
  "statut_actuel": "VALIDEE"
}
```
