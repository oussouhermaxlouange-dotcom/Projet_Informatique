# Résumé du projet — TP1 à TP6

**Projet informatique 2 · L3 SIL**  
Application Web de gestion des stages et des soutenances  
Membres : OUSSOU Hermax, TCHEGNON Loïk, KANHONOU Ashley  
Encadreur : MAMA Tairou  
Version : 2.1 — 18/11/2026

Ce document récapitule l'ensemble du travail réalisé : les livrables, les décisions
techniques, les tests et les preuves conservées. Le livrable TP6 (rapport et
preuves) est dans `TP6_API/` ; l'application reste dans `TP4_Architecture/`.

---

## 1. Vue d'ensemble

| TP | Sujet | Livrable principal | État |
|---|---|---|---|
| TP1 | Fiche de cadrage | `TP1_Fiche_cadrage.md` + `.docx` | Terminé |
| TP2 | Exigences et traçabilité | `TP2_Exigences.md` + `.docx` | Terminé |
| TP3 | Modèle UML et schéma SQL | `TP3_Modele_donnees/` (rapport DOCX/PDF + scripts SQL) | Terminé |
| TP4 | Squelette technique et contrat d'API | `TP4_Architecture/` | Terminé |
| TP5 | Dépôt Git et organisation d'équipe | Dépôt Git avec 3 commits | Partiel (voir §6) |
| TP6 | API des demandes | `TP6_API/` (rapport HTML/PDF/DOCX + preuves) et `TP4_Architecture/` (code) | Terminé |

Fil rouge : application locale de suivi des demandes de stage et des soutenances,
avec des données fictives uniquement, réalisée en 25 heures par un groupe de trois.

---

## 2. TP1 — Fiche de cadrage

Fichiers : `TP1_Fiche_cadrage.md`, `TP1_Fiche_cadrage.docx`.

Contenu produit :

- problème et valeur attendue : suivi papier/courriel/tableurs, dossiers perdus,
  absence d'état partagé ; références estimées à 12 jours de validation, 35 % de
  dossiers incomplets et 4 conflits ;
- parties prenantes et rôles ;
- périmètre du MVP : 5 éléments inclus, 3 exclus ;
- objectifs SMART et indicateurs mesurables ;
- risques, contraintes et hypothèses ;
- annexe avec les remarques du groupe relecteur.

---

## 3. TP2 — Exigences et matrice de traçabilité

Fichiers : `TP2_Exigences.md`, `TP2_Exigences.docx`.

Contenu produit :

- **8 exigences fonctionnelles** (EF-01 à EF-08), chacune avec acteur, priorité
  MoSCoW et précondition/résultat attendu ;
- **3 exigences non fonctionnelles mesurables** (ENF-01 à ENF-03) :
  contrôle d'accès, validation serveur, sauvegarde/restauration ;
- user stories et critères d'acceptation ;
- périmètre minimal pour 25 heures ;
- **matrice de traçabilité** exigence → composant → test (T-01 à T-11).

Exigences couvertes par l'API du TP6 : EF-01 (connexion), EF-02 (création),
EF-03 (décision), EF-06 (consultation de ses demandes).

---

## 4. TP3 — Modèle UML et schéma SQL

Dossier : `TP3_Modele_donnees/`.

### 4.1 Diagrammes

- **Cas d'utilisation** : 4 acteurs, 9 cas, diagramme construit en SVG
  (`cas_utilisation.svg`), rendu PNG et variante PlantUML.
  Le vocabulaire retenu est « cas d'utilisation » (et non « cas usage »).
- **Classes** : 9 classes avec multiplicités (`classes.puml`, `classes.png`).

### 4.2 Base de données

- `001_schema.sql` : base `tp3_conventions`, 9 tables, contraintes et 4 vues.
- `002_seed.sql` : jeu fictif — 8 comptes, 3 étudiants, 2 encadreurs,
  2 entreprises, 3 salles, 6 conventions, 4 disponibilités, 2 soutenances,
  9 lignes d'historique. Mot de passe commun : `Demo1234!`.
- `003_verification.sql` : comptages, statuts, indicateurs, planning, délais,
  conflits et journal.
- `004_tests_contraintes.sql` : insertions invalides (refus sans motif, e-mail
  incorrect, entreprise inconnue, période inversée, doublon, chevauchement).

### 4.3 Tables du modèle

`utilisateur`, `etudiant`, `encadreur`, `entreprise`, `salle`, `convention`,
`disponibilite`, `soutenance`, `historique`.

Règles portées par la base :

- un compte a au plus une fiche étudiant et une fiche encadreur (`UNIQUE`) ;
- une convention est déposée par un étudiant, accueillie par une entreprise et
  encadrée par zéro ou un encadreur ;
- cycle `BROUILLON → SOUMISE → VALIDEE | REFUSEE`, avec motif obligatoire en cas
  de refus et date de décision obligatoire pour une décision ;
- `date_fin > date_debut`, capacité de salle bornée, durée de soutenance bornée ;
- une convention donne au plus une soutenance ; l'encadreur de la soutenance est
  celui de la convention (clé étrangère composite).

### 4.4 Vues

- `v_conventions_sans_encadreur` : conventions validées non affectées ;
- `v_soutenances_conflits` : chevauchements de salle ou d'encadreur ;
- `v_planning_soutenance` : planning lisible ;
- `v_delai_publication` : délai décision → publication du planning.

### 4.5 Rapport et scénario

- `TP3_Modele_donnees.docx` / `.pdf` : rapport en noir et blanc (diagrammes,
  tables, scénario, scripts, résultats), généré par `build_docx.py`.
- `scenario_validation.md` : scénario « Confirmer une convention », avec les
  codes HTTP attendus (401, 403, 404, 409, 400, 500 + rollback).

C'est ce modèle (`tp3_conventions`, `convention`, `historique`) qui sert de
référence à l'application des TP4 et TP6.

---

## 5. TP4 — Squelette technique et contrat d'API

Dossier : `TP4_Architecture/`.

### 5.1 Arborescence

```text
TP4_Architecture/
├── public/            # point d'entrée unique + .htaccess
├── src/
│   ├── Controllers/   # adaptation HTTP
│   ├── Services/      # règles métier
│   ├── Repositories/  # PDO et SQL
│   ├── Support/       # routeur, requête, réponse, session, .env
│   └── autoload.php   # autoload PSR-4 sans Composer
├── config/            # database.php, routes.php
├── tests/             # tests sans framework
├── docs/              # contrat, ADR, justification, cas de tests
├── preuves/           # sorties conservées
├── tools/             # génération d'empreintes bcrypt
├── .env.example
└── .gitignore
```

### 5.2 Livrables TP4

- configuration par `.env` (exclu de Git) et `.env.example` versionné ;
- connexion PDO avec `ERRMODE_EXCEPTION`, `EMULATE_PREPARES = false`, timeout 3 s ;
- test de connexion réel ;
- route `GET /api/sante` qui exécute un `SELECT 1` et répond `200` ou `503` ;
- contrat d'API complet ;
- ADR-001 : monolithe modulaire PHP 8 sans framework.

### 5.3 ADR-001

Décision : monolithe modulaire PHP 8, point d'entrée unique, quatre couches,
PDO en requêtes préparées, aucune dépendance externe.

Conséquences acceptées : routage, validation et gestion d'erreurs écrits à la
main, donc à tester ; pas d'outillage de framework.

---

## 6. TP5 — Dépôt Git et organisation d'équipe

État actuel :

- dépôt Git initialisé à la racine ;
- trois commits : `41e14a9` (TP1), `d7eaf5a` (TP2), `51b04fe` (TP3) ;
- TP4 et TP6 sont présents dans le dossier de travail mais **pas encore commités**.

Non formalisé à ce stade : tableau Kanban, conventions de branches courtes,
revues de code écrites. À compléter si le rendu TP5 est demandé séparément.

---

## 7. TP6 — API des demandes

Implémenté dans `TP4_Architecture/` (même application, pas de duplication).
Les preuves, le script de rejeu et le rapport sont regroupés dans `TP6_API/`.

### 7.1 Réponse aux cinq points du sujet

| Point du sujet | Réalisation |
|---|---|
| `DemandeRepository` avec `findById`, `findByStudent`, `create`, `updateStatus` | `src/Repositories/DemandeRepository.php`, toutes en requêtes préparées ; ajout de `findByEncadreur`, `findAll`, `ajouterHistorique`, `transaction` |
| Table des transitions, refus `409` | constante `TRANSITIONS` dans `src/Services/DemandeService.php` ; `BROUILLON → SOUMISE`, `SOUMISE → VALIDEE \| REFUSEE`, états finaux terminaux |
| Connexion : mot de passe haché, vérification, régénération de session | `AuthService` + `Session` : bcrypt, `password_verify`, `session_regenerate_id(true)`, cookie `HttpOnly`/`SameSite=Lax`, `use_strict_mode` |
| Transaction statut puis historique, rollback | `DemandeRepository::transaction()` : `UPDATE convention` puis `INSERT historique`, rollback complet sur exception |
| Six cas testés avec sorties | `TP6_API/tests_api.sh` → `TP6_API/preuves/sorties.tsv` : 14 cas, 14 conformes (six cas officiels S5–S10 + préparation et contrôles S1–S4, S11–S14) |

### 7.2 Routes de l'API

| Méthode | Chemin | Rôle | Accès |
|---|---|---|---|
| `GET` | `/api/sante` | Vérifier l'application et la base | Public |
| `POST` | `/api/connexion` | Ouvrir une session | Public |
| `POST` | `/api/deconnexion` | Fermer la session | Session |
| `GET` | `/api/moi` | Profil connecté | Session |
| `GET` | `/api/demandes` | Lister selon le rôle | Session |
| `GET` | `/api/demandes/{id}` | Détail d'une demande | Session + droits |
| `POST` | `/api/demandes` | Créer et soumettre une demande | Étudiant |
| `PATCH` | `/api/demandes/{id}/statut` | Valider ou refuser | Responsable |

### 7.3 Règles métier

- une demande est stockée dans la table `convention` (vocabulaire métier
  « demande » côté API) ;
- création : entreprise existante, intitulé de 5 à 120 caractères, dates
  `AAAA-MM-JJ` avec `date_fin > date_debut`, `soumettre` booléen ;
- `soumettre = true` → statut `SOUMISE`, `date_depot` et ligne d'historique ;
- décision réservée au rôle `RESPONSABLE` ;
- refus : motif obligatoire de 3 à 255 caractères ;
- un étudiant ne voit et ne modifie que ses propres demandes ;
- une demande `VALIDEE` ou `REFUSEE` ne peut plus changer d'état (`409`).

### 7.4 Codes HTTP et codes d'erreur

`400 JSON_INVALIDE`, `401 NON_AUTHENTIFIE` / `IDENTIFIANTS_INVALIDES`,
`403 ROLE_NON_AUTORISE` / `PROFIL_MANQUANT` / `COMPTE_INACTIF` / `ACCES_REFUSE`,
`404 ROUTE_INCONNUE` / `DEMANDE_INCONNUE`, `405 METHODE_NON_AUTORISEE`,
`409 TRANSITION_INTERDITE`, `422 VALIDATION`, `500 ERREUR_INTERNE`,
`503 BASE_INDISPONIBLE`.

### 7.5 Sécurité

- mots de passe en bcrypt, jamais en clair ;
- session régénérée à la connexion, identifiant inconnu refusé ;
- requêtes préparées avec émulation désactivée ;
- aucun SQL dans les contrôleurs ;
- erreurs techniques journalisées côté serveur, message générique côté client ;
- `.env` ignoré par Git, seul `.env.example` est versionné ;
- aucune donnée réelle.

### 7.6 Livrable `TP6_API/`

| Fichier | Contenu |
|---|---|
| `tests_api.sh` | Recharge `tp3_conventions` depuis les scripts TP3, démarre l'API sur le port 8082, rejoue S1–S14, écrit les preuves |
| `preuves/sorties.tsv` | Un cas par ligne : attendu, requête, code obtenu, conformité, corps JSON complet |
| `preuves/etat_base.tsv` | 7 demandes après les cas (1 `BROUILLON`, 2 `REFUSEE`, 4 `VALIDEE`) et 12 lignes d'historique |
| `preuves/capture_api.png` | Capture réelle de `GET /api/sante` |
| `build_rapport.py` | Génère HTML + PDF (Chrome) depuis les TSV |
| `build_docx.py` | Génère le DOCX via UNO, même mise en page que le rapport TP3 |
| `api_demandes.html` / `.pdf` / `.docx` | Rapport noir et blanc, 2 pages : objet, routes, transitions, six cas, état de la base, sécurité, justification, preuves |
| `README.md` | Prérequis, commandes, description des cas |

Résultat conservé : **14 cas exécutés, 14 conformes**, sur MySQL 8.0.46 et l'API
réelle. Les six cas officiels sont S5 (200), S6 (400), S7 (401), S8 (403),
S9 (404) et S10 (409) ; S1–S4 préparent les sessions et la demande, S11–S14
couvrent le refus motivé, les listes par rôle et l'entreprise inconnue (422).

---

## 8. Tests et preuves

| Fichier | Ce qu'il vérifie | Résultat |
|---|---|---|
| `tests/test_connexion.php` | Connexion PDO à `tp3_conventions` | OK |
| `tests/test_sante.php` | Route de santé : structure et cohérence 200/503 | OK |
| `tests/test_routes.php` | Routeur : 200, 404, 405, 401 | OK |
| `tests/test_domain.php` | Transitions, lectures préparées, rollback, 403/409/422 | OK |
| `tests/tester_api.sh` | Six cas HTTP + contrôles complémentaires | 14/14 |
| `tests/tester_http.sh` | En-têtes et corps HTTP réels | OK |

Preuves conservées dans `TP4_Architecture/preuves/` :

- `sortie_api.txt` — six cas TP6 (succès, 400, 401, 403, 404, 409) ;
- `sortie_test_domain.txt` — domaine et rollback ;
- `sortie_test_connexion.txt` — connexion PDO ;
- `sortie_test_sante.txt` et `sortie_test_sante_503.txt` — base joignable / injoignable ;
- `sortie_test_routes.txt` — routeur ;
- `sortie_http.txt` — en-têtes HTTP.

Tableau détaillé des six cas : `TP4_Architecture/docs/tp6_cas_tests.md`.

### 8.1 Preuves du livrable `TP6_API/`

| Fichier | Ce qu'il montre | Résultat |
|---|---|---|
| `tests_api.sh` | Rejeu complet sur base rechargée (S1–S14) | 14/14 |
| `preuves/sorties.tsv` | Codes HTTP et corps JSON réels, un cas par ligne | 14 lignes conformes |
| `preuves/etat_base.tsv` | État de `convention` et d'`historique` après les cas | 7 demandes, 12 historiques |
| `preuves/capture_api.png` | `GET /api/sante` dans un navigateur | 200 |
| `api_demandes.pdf` | Rapport noir et blanc | 2 pages A4 |
| `api_demandes.docx` | Version éditable, tableaux non coupés | 2 pages A4 |

---

## 9. État du dépôt

```text
41e14a9  Commit TP1 Hermax
d7eaf5a  feat: Commit TP2
51b04fe  Commit TP3
```

- Les dossiers `TP4_Architecture/` (TP4 + TP6), `TP6_API/` (rapport et preuves) et `RESUME_PROJET.md` ne sont pas encore commités.
- Le dossier `TP6/` est le travail d'un autre groupe, ajouté comme modèle : il n'est pas modifié.
- Le fichier `.env` local est ignoré par Git (vérifié).
- Le serveur de test PHP a été arrêté ; aucune donnée réelle n'est utilisée.

---

## 10. Reste à faire

| TP | Contenu |
|---|---|
| TP5 | Formaliser les branches, le Kanban et les revues ; commiter TP4 et TP6. |
| TP7 | Interface et intégration : parcours étudiant et responsable, formulaires accessibles, `fetch`, affichage avec `textContent`. |
| TP8 | Plan de tests complet et audit de sécurité (XSS, injections, sessions). |
| TP9 | Déploiement local et sauvegarde/restauration. |
| TP10 | Préparation de la soutenance et démonstration. |

---

## 11. Commandes utiles

```bash
# Base de données (jeu d'essai TP3)
mysql -u root -p < TP3_Modele_donnees/001_schema.sql
mysql -u root -p < TP3_Modele_donnees/002_seed.sql

# Application
cd TP4_Architecture
cp .env.example .env        # puis renseigner les identifiants
php -S 127.0.0.1:8000 -t public public/index.php

# Vérifications
php tests/test_connexion.php
php tests/test_sante.php
php tests/test_routes.php
php tests/test_domain.php
./tests/tester_api.sh http://127.0.0.1:8000

# Livrable TP6 (rejeu + rapport)
cd ../TP6_API
./tests_api.sh              # recharge la base, démarre l'API sur 8082, rejoue 14 cas
python3 build_rapport.py    # HTML, PDF (Chrome), DOCX (LibreOffice/UNO)
```

Comptes de démonstration (mot de passe `Demo1234!`) :
`sena.houngbo@univ.test` (étudiant), `sylvain.kiki@univ.test` (encadreur),
`responsable.pedago@univ.test` (responsable), `admin.siege@univ.test` (admin).
