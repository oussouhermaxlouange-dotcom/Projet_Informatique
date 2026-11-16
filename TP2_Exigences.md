# TP2 — Exigences et matrice de traçabilité

**Projet informatique 2 · L3 SIL**  
**Projet : application Web de gestion des stages et des soutenances**

| Information | Valeur |
|---|---|
| Groupe | À compléter |
| Membres | OUSSOU Hermax, TCHEGNON Loïk, KANHONOU Ashley |
| Encadreur | MAMA Tairou |
| Version | 1.0 — 16/11/2026 |
| Environnement | PHP 8, MySQL/MariaDB, application locale, données fictives |

**MoSCoW :** Must = indispensable ; Should = souhaitable ; Could = facultatif. Les exigences décrivent le comportement attendu, pas une fonctionnalité déjà réalisée.

## 1. Exigences fonctionnelles

| ID | Exigence testable | Acteur | Priorité | Précondition et résultat attendu |
|---|---|---|---|---|
| EF-01 | Se connecter avec un compte existant. | Tous les rôles | Must | Compte actif ; identifiants valides ouvrent une session correspondant au rôle. Identifiants invalides : accès refusé. |
| EF-02 | Créer et soumettre une demande de stage avec les champs et pièces obligatoires. | Étudiant | Must | Étudiant connecté ; demande complète enregistrée au statut SOUMISE. Champ ou pièce obligatoire manquante : rejet, demande non soumise. |
| EF-03 | Valider une demande soumise ou la refuser avec un motif. | Responsable pédagogique | Must | Responsable connecté et demande au statut SOUMISE ; statut mis à jour et décision historisée. Refus sans motif : rejet. |
| EF-04 | Affecter un encadreur à une demande validée. | Secrétariat | Must | Demande VALIDEE et encadreur existant ; affectation enregistrée. Demande non validée : affectation refusée. |
| EF-05 | Programmer la soutenance d'une demande validée et affectée, sans chevauchement de salle ou d'encadreur. | Secrétariat | Must | Demande éligible et créneau libre ; soutenance enregistrée. Créneau déjà pris : refus sans créer de soutenance. |
| EF-06 | Consulter l'état de ses demandes. | Étudiant | Should | Étudiant connecté ; seules ses demandes et leur état sont affichés. |
| EF-07 | Rechercher un dossier par nom d'étudiant ou statut. | Secrétariat | Should | Secrétariat connecté ; résultats correspondent au critère fourni. Aucun résultat : liste vide, sans erreur serveur. |
| EF-08 | Consulter l'historique des décisions d'une demande. | Responsable pédagogique | Could | Responsable autorisé à lire le dossier ; décisions affichées dans l'ordre chronologique. |

## 2. Exigences non fonctionnelles mesurables

| ID | Exigence | Critère de vérification |
|---|---|---|
| ENF-01 | Toute lecture ou modification d'un dossier vérifie l'authentification, le rôle et le droit sur ce dossier côté serveur. | Tester chaque rôle autorisé et non autorisé ainsi qu'une requête anonyme ; refus HTTP 401/403 et aucune donnée de dossier dans la réponse non autorisée. |
| ENF-02 | Tous les champs obligatoires et valeurs métier sont validés côté serveur avant écriture en base. | Pour chaque formulaire, tester champ absent, format invalide et valeur hors limites ; réponse HTTP 422 et aucune écriture invalide. |
| ENF-03 | La sauvegarde de la base doit pouvoir être restaurée dans un environnement de test. | Créer une sauvegarde puis la restaurer ; comparer le nombre de lignes des tables métier avant/après et vérifier la présence des données fictives. |

## 3. User stories et critères d'acceptation

### US-01 — Soumettre une demande (EF-02)

En tant qu'étudiant, je veux soumettre une demande de stage complète afin que le secrétariat puisse la traiter.

- **Given** un étudiant connecté et une demande renseignée avec les pièces obligatoires.  
  **When** il soumet la demande.  
  **Then** la demande est enregistrée au statut SOUMISE et devient consultable par les rôles autorisés.
- **Given** un étudiant connecté et une demande sans une pièce obligatoire.  
  **When** il tente de la soumettre.  
  **Then** le serveur répond 422, indique le champ ou la pièce manquante et ne soumet pas la demande.

### US-02 — Décider d'une demande (EF-03)

En tant que responsable pédagogique, je veux valider une demande complète ou la refuser avec un motif afin de formaliser la décision.

- **Given** une demande au statut SOUMISE et un responsable connecté.  
  **When** le responsable valide la demande.  
  **Then** le statut devient VALIDEE et la décision est ajoutée à l'historique.
- **Given** une demande au statut VALIDEE.  
  **When** le responsable tente de la refuser.  
  **Then** le serveur répond 409, le statut reste VALIDEE et l'historique reste inchangé.

## 4. Périmètre minimal pour 25 heures

Le socle prioritaire comprend les exigences Must EF-01 à EF-05 : connexion, soumission, décision, affectation et programmation. Elles correspondent au parcours de bout en bout du MVP cadré au TP1.

- **ENF-01 et ENF-02** sont des critères de qualité obligatoires sur toutes les fonctions livrées ; ils ne sont pas reportés.
- **ENF-03** est vérifié par une sauvegarde/restauration manuelle simple, sans développer d'interface d'administration de sauvegarde.
- **EF-06 et EF-07 (Should)** sont faits seulement après le socle, si le temps restant le permet ; sinon reportés en v2.
- **EF-08 (Could)** est reportée en v2 pour préserver le temps de réalisation et de test du parcours prioritaire.

Paiement, SMS et portail entreprise restent hors périmètre ; seuls des comptes et dossiers fictifs seront utilisés.

## 5. Matrice de traçabilité

**Statut initial : À faire.** Une exigence ne sera déclarée réalisée qu'après exécution du test associé et conservation de sa preuve.

| Exigence | Composant cible | Test / preuve attendue | Statut |
|---|---|---|---|
| EF-01 | Authentification / contrôleur de session | T-01 : connexion valide et invalide pour les rôles prévus ; session/rôle vérifiés. | À faire |
| EF-02 | Formulaire et service de demandes | T-02 : demande complète enregistrée SOUMISE ; demande incomplète rejetée en 422, sans écriture. | À faire |
| EF-03 | Service de décision | T-03 : validation change le statut et ajoute l'historique ; transition invalide rejetée en 409. | À faire |
| EF-04 | Service d'affectation | T-04 : affecter un dossier validé ; vérifier qu'un dossier non validé est refusé. | À faire |
| EF-05 | Service de planning / vérification des conflits | T-05 : 4 créneaux libres acceptés, 4 conflits refusés ; vérifier 0 conflit enregistré. | À faire |
| EF-06 | Vue étudiant / service de demandes | T-06 : deux étudiants fictifs ; chacun ne voit que ses demandes et leurs états. | À faire |
| EF-07 | Recherche du secrétariat | T-07 : rechercher par nom puis statut ; résultats conformes, aucun résultat sans erreur. | À faire |
| EF-08 | Historique des décisions | T-08 : plusieurs décisions fictives affichées dans l'ordre chronologique au rôle autorisé. | À faire |
| ENF-01 | Middleware / contrôle d'accès | T-09 : tests anonymes et par rôle ; 401/403, aucune donnée retournée sans droit. | À faire |
| ENF-02 | Validation serveur des formulaires | T-10 : valeurs absentes, mal formées et hors limites ; 422 et base inchangée. | À faire |
| ENF-03 | Procédure de sauvegarde SQL | T-11 : sauvegarder puis restaurer ; comparer le nombre de lignes et contrôler les données fictives. | À faire |

**Preuves à conserver :** résultats des tests, captures ou sorties de requêtes et référence du commit correspondant.
