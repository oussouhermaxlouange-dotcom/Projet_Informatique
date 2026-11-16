# TP1 — Fiche de cadrage du projet

**Projet informatique 2 · L3 SIL**  
**Projet fil rouge : application Web de gestion des stages et des soutenances**

| Information | Valeur |
|---|---|
| Groupe | À compléter |
| Membres | OUSSOU Hermax, TCHEGNON Loïk, KANHONOU Ashley |
| Encadreur | MAMA Tairou |
| Dépôt Git | URL à ajouter |
| Version | 1.0 — 16/11/2026 |

## 1. Problème et valeur attendue

Les demandes de stage et les soutenances sont suivies sur papier, par courriel et dans des tableurs séparés.  
Les dossiers peuvent se perdre, être incomplets ou rester sans état partagé entre les acteurs.  
Dans ce scénario, les références estimées sont 12 jours de validation, 35 % de dossiers incomplets et 4 conflits.  
Une application Web locale vise à centraliser le suivi, réduire les délais et empêcher les conflits de soutenance.  
Le projet sera réalisé en 25 heures par notre groupe de trois, avec des données fictives uniquement.

| Indicateur | Unité | Mode de mesure | Référence estimée | Cible |
|---|---|---|---:|---:|
| Délai moyen de validation | Jours ouvrés | Moyenne des dates de décision moins dates de soumission sur 20 demandes fictives | 12 jours | ≤ 3 jours |
| Dossiers incomplets à la première lecture | % | Demandes fictives incomplètes / 20, selon une liste de 6 pièces | 35 % | ≤ 10 % |
| Conflits de calendrier | Nombre / session | Compter les chevauchements de salle ou d'encadreur dans les essais | 4 | 0 accepté |

*Les références sont des estimations pédagogiques, non des mesures réelles ; vérification sur jeu fictif seulement.*

## 2. Parties prenantes

| Partie prenante | Attente principale | Dans le MVP |
|---|---|---|
| Étudiant | Déposer et suivre sa demande. | Oui |
| Secrétariat | Vérifier les pièces et planifier les soutenances. | Oui |
| Responsable pédagogique | Valider ou refuser avec un motif. | Oui |
| Encadreur | Consulter ses étudiants affectés. | Oui |
| Administrateur technique | Gérer les comptes et les accès. | Oui |

## 3. Périmètre du MVP

### Inclus — 5 éléments

1. Authentification et contrôle des rôles : protéger les dossiers.
2. Dépôt d'une demande de stage : parcours principal étudiant.
3. Validation ou refus motivé : rendre la décision explicite.
4. Affectation d'un encadreur : préparer le suivi du stage.
5. Programmation d'une soutenance avec contrôle des conflits : éviter les chevauchements.

### Exclus — 3 éléments

1. Paiement en ligne : aucun paiement requis et service externe hors budget.
2. Notifications SMS : coût et dépendance à un prestataire ; reportées en v2.
3. Portail de dépôt d'offres par les entreprises : parcours additionnel hors des 25 h.

## 4. Objectifs SMART

| Objectif | Mesure et test | Seuil | Échéance | Preuve |
|---|---|---|---|---|
| O1 — Obtenir un délai moyen de validation ≤ 3 jours ouvrés sur le jeu fictif. | Calculer la moyenne sur 10 demandes fictives à partir des dates de soumission et décision. | ≤ 3 jours ; 10/10 décisions enregistrées. | 18/12/2026 | Résultat de requête et capture. |
| O2 — Permettre le dépôt complet d'une demande fictive en moins de 5 minutes. | Chronométrer 5 essais avec un compte étudiant fictif et vérifier les 6 pièces. | 5/5 dépôts complets ; durée de chaque essai < 5 min. | 18/12/2026 | Fiche de test chronométrée. |
| O3 — Empêcher tout chevauchement de salle ou d'encadreur à la programmation. | Tester 4 créneaux libres et 4 créneaux en conflit. | 4/4 créneaux libres acceptés ; 4/4 conflits refusés ; 0 conflit enregistré. | 18/12/2026 | Résultats des 8 essais. |

## 5. Risques

Probabilité (P) et impact (I) notés de 1 à 3 ; criticité = P × I.

| Risque | P | I | Criticité | Action préventive | Repli | Propriétaire |
|---|---:|---:|---:|---|---|---|
| Serveur MySQL/MariaDB indisponible. | 2 | 3 | 6 | Installer et tester MariaDB dès la première séance. | Utiliser l'installation locale d'un autre membre. | Administrateur |
| Conflit Git en fin de projet. | 3 | 2 | 6 | Branches courtes et fusions régulières. | Réintégrer depuis le dernier commit fonctionnel. | Chef de projet |
| Utilisation accidentelle de données réelles. | 1 | 3 | 3 | Utiliser exclusivement des données fictives et vérifier les jeux avant test. | Supprimer les données, renouveler les accès et signaler l'incident. | Toute l'équipe |

## 6. Contraintes et hypothèses

**Contraintes**
- 25 heures de travail ; groupe de trois à quatre étudiants.
- PHP 8, MySQL/MariaDB, Git et navigateur ; exécution locale.
- Budget nul et données fictives uniquement.

**Hypothèses à vérifier**
- MySQL/MariaDB est disponible sur au moins un poste.
- Les scénarios de soutenance peuvent être représentés par des données fictives.
- Les fonctions retenues restent réalisables dans le temps imparti.

**Réussite :** objectifs testés, périmètre justifié et risques traités. Faire relire cette fiche par un autre groupe et consigner ses remarques dans l'annexe.

---

# Annexe — Liste des remarques du groupe relecteur

À remplir par un autre groupe après lecture de la fiche. Ne pas préremplir avec des exemples : consigner les remarques réellement reçues.

**Groupe relecteur :** à compléter  
**Date :** à compléter

| # | Point relu | Remarque / ambiguïté constatée | Décision ou correction |
|---:|---|---|---|
| 1 | Problème et indicateurs | | |
| 2 | Parties prenantes | | |
| 3 | Périmètre inclus/exclu | | |
| 4 | Objectifs SMART | | |
| 5 | Risques et contraintes | | |

**Remarques acceptées :** ____  **Reportées :** ____  **Rejetées :** ____

**Nom et signature du groupe relecteur :** ____________________  
**Nom et signature du représentant du groupe :** ____________________
