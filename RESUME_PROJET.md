# Résumé du projet — TP1 à TP8

**Projet informatique 2 · L3 SIL**  
Application Web de gestion des stages et des soutenances  
Membres : OUSSOU Hermax, TCHEGNON Loïk, KANHONOU Ashley  
Encadreur : MAMA Tairou  
Version : 2.3 — 19/11/2026

Ce document récapitule l'ensemble du travail réalisé : les livrables, les décisions
techniques, les tests et les preuves conservées. Les livrables documentaires sont dans
`TP6_API/`, `TP7_Frontend/` et `TP8_Tests/` ; l'application (API et interface) reste
dans `TP4_Architecture/`.

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
| TP7 | Interface et intégration | `TP7_Frontend/` (parcours, scénario, preuves, rapport) et `TP4_Architecture/public/` (code) | Terminé |
| TP8 | Plan de tests et audit de sécurité | `TP8_Tests/` (matrice, revue, recette, preuves, rapport) | Terminé |

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
├── public/            # point d'entrée unique, interface (index.html, assets/), .htaccess
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
- TP4, TP6, TP7 et TP8 sont présents dans le dossier de travail mais **pas encore
  commités** ; le travail est laissé non commité à la demande du groupe.

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

## 8. TP7 — Interface et intégration

L'interface est servie par l'application elle-même, dans
`TP4_Architecture/public/` : même origine que l'API, donc même cookie de session,
sans duplication ni CORS. Les preuves et le rapport sont dans `TP7_Frontend/`.

### 8.1 Réponse aux cinq points du sujet

| Point du sujet | Réalisation |
|---|---|
| Dessiner les parcours des deux rôles | `TP7_Frontend/parcours.svg` / `.png` : deux couloirs, écrans, actions et échanges. |
| Formulaire de dépôt avec étiquettes liées et zone d'erreur | `public/index.html` : `label for`, `aria-describedby`, `role="alert"`, une zone `erreur-…` par champ. |
| Appels `fetch`, erreurs 400, 401, 500 lisibles | `public/assets/api.js` : `fetch` en `same-origin`, table des messages, titre + détails ; page de preuve `preuves/erreurs.html`. |
| Liste avec `textContent`, test des balises | `public/assets/rendu.js` : aucun `innerHTML` ; `preuves/xss.html` et `xss_verification.txt` (0 balise créée, `data-xss` absent). |
| Scénario complet | `TP7_Frontend/scenario.md` : créer, consulter, filtrer, valider, refuser, persistance, avec 13 captures. |

### 8.2 Écrans et rôles

| Rôle | Écrans | Actions |
|---|---|---|
| `ETUDIANT` | Connexion, « Mes demandes », « Nouvelle convention », « Détail » | Créer une convention (entreprise, intitulé, dates), suivre statut, date de décision et motif. |
| `RESPONSABLE` | Connexion, « Dossiers à traiter », « Décision de convention », « Détail » | Rechercher et filtrer par statut, valider ou refuser avec motif obligatoire ; décision reportée dans le détail de l'étudiante. |
| `ADMIN` | « Dossiers à traiter », « Détail » | Consultation de tous les dossiers, sans bouton de décision. |
| `ENCADREUR` | « Mes demandes », « Détail » | Consultation des demandes qu'il encadre, sans décision. |

Direction visuelle : portail administratif contemporain, fond papier ivoire
(`#faf9f2`), surfaces blanches, accent violet (`#5148dc`) pour les liens et les
états actifs, boutons principaux noirs. Contenu centré sur 1600 px au maximum,
sans bordure décorative autour des cartes ; trois compteurs (validées, en cours
de revue, rejetées) ouvrent « Mes demandes », le nombre de dossiers en attente
est rappelé côté responsable. Polices locales (Inter, Lato), aucune requête
externe.

### 8.3 Accessibilité et erreurs

- étiquettes liées à chaque champ, aide et zone d'erreur reliées par `aria-describedby` ;
- zone globale `role="alert"` + `aria-live="assertive"`, messages de réussite en
  `role="status"` ;
- `aria-invalid="true"` sur le champ fautif, message texte sous le champ ;
- lien d'évitement, `:focus-visible` sur tous les contrôles ; la décision est un
  écran dédié (sans dialogue) et le focus est placé sur le motif en cas de refus
  non motivé ;
- statut écrit en toutes lettres ; la couleur ne fait que renforcer ;
- `novalidate` sur les formulaires : les messages affichés sont ceux de l'API (422).

Codes traités : `400`, `401` (retour à la connexion), `403`, `404`, `405`, `409`,
`422`, `500`, `503`, plus le cas « serveur injoignable ».

### 8.4 Rendu sécurisé

Les valeurs reçues de l'API sont insérées dans des nœuds créés par
`document.createElement`, puis affectées à `textContent`. Deux charges hostiles
(`<img onerror=…>` et `<script>…</script>`) ont été envoyées par le formulaire et
rejouées sur `/preuves/xss.html` : aucune balise n'est interprétée, `data-xss` reste
absent. Preuve : `TP7_Frontend/preuves/xss_verification.txt` et `xss_dom.html`.

### 8.5 Livrable `TP7_Frontend/`

| Fichier | Contenu |
|---|---|
| `parcours.svg` / `.png` | Parcours des deux rôles |
| `scenario.md` | Scénario de bout en bout, protocole, commandes de rejeu |
| `preuves/01…13.png` | 13 captures réelles, de la connexion au test XSS |
| `preuves/xss_verification.txt`, `xss_dom.html` | Contrôle chiffré et DOM complet |
| `README.md` | Contenu, accessibilité, erreurs, limites |
| `interface_tp7.html` / `.pdf` / `.docx` | Rapport 2 pages A4, noir et blanc, avec le schéma des parcours |

---

## 9. TP8 — Plan de tests et audit de sécurité

Les tests s'exécutent contre l'API réelle, sur une base rechargée depuis le jeu
d'essai TP3. Preuves et documents dans `TP8_Tests/`.

### 9.1 Réponse aux cinq points du sujet

| Point du sujet | Réalisation |
|---|---|
| Matrice d'au moins huit lignes, attendu écrit avant | `TP8_Tests/matrice_tests.md` : 14 lignes (test, exigence, données, attendu, observé, preuve) ; l'attendu est un paramètre du script. |
| Quatre cas limites | T-01 demande inexistante (404), T-02 refus sans motif (422 + statut inchangé), T-03 validation répétée (409 + statut inchangé), T-04 date invalide (422). |
| Autorisation et injection | T-05 étudiante B → dossier A (403) ; T-06 `1 OR 1=1` en identifiant (404) ; T-09/T-09b dans les champs de connexion (422/401). |
| Mots de passe hachés et CSRF | T-13 : 8/8 empreintes bcrypt, 0 en clair ; CSRF : `SameSite=Lax` + API sans CORS + contrôle `Origin` (403 `ORIGINE_REFUSEE`). |
| Quatre remarques de revue classées | `TP8_Tests/revue_code.md` : R-01 bloquante corrigée, R-02 majeure corrigée, R-03 mineure corrigée, R-04 majeure acceptée et planifiée. |

### 9.2 Résultats

- **14 tests exécutés, 14 conformes** (`preuves/sorties.tsv`, `preuves/resume.txt`) ;
- **8/8 mots de passe en bcrypt**, longueur 60, aucun en clair (`preuves/hachages.tsv`) ;
- **5 scénarios de recette sur 5 conformes** (`recette.md`).

| Thème | Tests | Attendu |
|---|---|---|
| Cas limites | T-01 à T-04 | 404, 422, 409, 422 |
| Autorisation | T-05, T-07, T-08 | 403, 401, 403 |
| Injection | T-06, T-09, T-09b | 404, 422, 401 |
| CSRF | T-10 | 403 `ORIGINE_REFUSEE` |
| Données hostiles | T-11, T-12 | 201 stocké tel quel, 422 sans écriture |
| Mots de passe | T-13 | 8/8 bcrypt, 0 en clair |

### 9.3 Corrections issues de la revue

| Réf. | Constat | Niveau | État |
|---|---|---|---|
| R-01 | `(int)` acceptait `12abc` et `1 OR 1=1` ; validation par `ctype_digit` | Bloquante | Corrigée, testée T-06 |
| R-02 | CSRF implicite (`SameSite=Lax` seul) ; ajout du contrôle `Origin` | Majeure | Corrigée, testée T-10 |
| R-03 | Formulaire de refus sans `novalidate`, message maison masqué | Mineure | Corrigée, testée au scénario TP7 |
| R-04 | Pas de limitation des tentatives de connexion | Majeure | Acceptée en local, planifiée (429, 5 essais/15 min) |

### 9.4 Livrable `TP8_Tests/`

| Fichier | Contenu |
|---|---|
| `tests_securite.sh` | Recharge la base, démarre l'API sur 8086, rejoue les 14 tests, écrit les preuves |
| `matrice_tests.md` | Matrice complète et quatre cas limites détaillés |
| `revue_code.md` | 4 remarques classées, correctifs et dette technique |
| `recette.md` | 5 scénarios, réserves, signatures |
| `preuves/sorties.tsv`, `hachages.tsv`, `resume.txt` | Sorties réelles |
| `tests_securite.html` / `.pdf` / `.docx` | Rapport 2 pages A4, noir et blanc |
| `README.md` | Contenu, rejeu, sécurité, limites |

---

## 10. Tests et preuves

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

### 10.1 Preuves du livrable `TP6_API/`

| Fichier | Ce qu'il montre | Résultat |
|---|---|---|
| `tests_api.sh` | Rejeu complet sur base rechargée (S1–S14) | 14/14 |
| `preuves/sorties.tsv` | Codes HTTP et corps JSON réels, un cas par ligne | 14 lignes conformes |
| `preuves/etat_base.tsv` | État de `convention` et d'`historique` après les cas | 7 demandes, 12 historiques |
| `preuves/capture_api.png` | `GET /api/sante` dans un navigateur | 200 |
| `api_demandes.pdf` | Rapport noir et blanc | 2 pages A4 |
| `api_demandes.docx` | Version éditable, tableaux non coupés | 2 pages A4 |

---

## 11. État du dépôt

```text
41e14a9  Commit TP1 Hermax
d7eaf5a  feat: Commit TP2
51b04fe  Commit TP3
```

- Les dossiers `TP4_Architecture/` (TP4 + TP6 + interface TP7), `TP6_API/`, `TP7_Frontend/`, `TP8_Tests/`, `outils/` et `RESUME_PROJET.md` ne sont pas encore commités.
- Le dossier `TP6/` est le travail d'un autre groupe, ajouté comme modèle : il n'est pas modifié.
- Le fichier `.env` local est ignoré par Git (vérifié).
- Le serveur de test PHP a été arrêté ; aucune donnée réelle n'est utilisée.

---

## 12. Reste à faire

| TP | Contenu |
|---|---|
| TP5 | Formaliser les branches, le Kanban et les revues ; commiter TP4, TP6, TP7 et TP8. |
| TP9 | Déploiement local, compte SQL dédié et sauvegarde/restauration. |
| TP10 | Préparation de la soutenance et démonstration. |

---

## 13. Commandes utiles

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

# Interface TP7
cd ../TP4_Architecture
php -S 127.0.0.1:8084 -t public public/index.php   # puis http://127.0.0.1:8084/

# Livrable TP8 (matrice + audit)
cd ../TP8_Tests
./tests_securite.sh         # recharge la base, démarre l'API sur 8086, rejoue 14 tests
python3 build_rapport.py    # HTML, PDF (Chrome), DOCX (LibreOffice/UNO)
```

Comptes de démonstration (mot de passe `Demo1234!`) :
`sena.houngbo@univ.test` (étudiant), `sylvain.kiki@univ.test` (encadreur),
`responsable.pedago@univ.test` (responsable), `admin.siege@univ.test` (admin).
