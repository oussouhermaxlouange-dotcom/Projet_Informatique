# Dossier de livraison — liste de contrôle

**Projet informatique 2 · L3 SIL**  
Plateforme de suivi des conventions de stage et des soutenances  
Membres : OUSSOU Hermax, TCHEGNON Loïk, KANHONOU Ashley  
Encadreur : MAMA Tairou — 20/11/2026

La liste ci-dessous reprend les huit éléments attendus au chapitre 10. Chaque ligne
indique le livrable, son emplacement, la vérification effectuée et son état.

| # | Élément | Emplacement | Vérification | État |
|---|---|---|---|---|
| 1 | Dépôt Git et historique | racine du projet, `origin` GitHub | `git log`, `git status`, clone de contrôle | Conforme |
| 2 | Fiche de cadrage | `TP1_Fiche_cadrage.md` / `.docx` | problème, acteurs, périmètre, objectifs SMART, risques | Conforme |
| 3 | Exigences et matrice de traçabilité | `TP2_Exigences.md` / `.docx` | 8 EF, 3 ENF, matrice exigence → composant → test | Conforme |
| 4 | Diagrammes UML | `TP3_Modele_donnees/` | cas d'utilisation (4 acteurs, 9 cas), classes (9), SVG/PNG/PUML | Conforme |
| 5 | Schéma SQL | `TP3_Modele_donnees/001_schema.sql` | 9 tables, clés étrangères, contraintes, 4 vues | Conforme |
| 6 | Scripts SQL versionnés et jeu d'essai | `TP3_Modele_donnees/002…004_*.sql` | seed, vérifications, tests de contraintes | Conforme, réserve migration |
| 7 | Plan de tests et fiche de recette | `TP8_Tests/` | 14/14 tests, 5/5 scénarios, revue de code | Conforme |
| 8 | README d'installation et ADR | `TP4_Architecture/` + `TP9_Deploiement/` | installation reproductible, ADR-001, sauvegarde/restauration | Conforme |

## 1. Dépôt Git et historique

- Dépôt initialisé à la racine, remote `origin` :
  `https://github.com/oussouhermaxlouange-dotcom/Projet_Informatique.git`.
- Dernier commit : `4179d8c` — « feat: ajout TP7, TP8, maquettes et mise à jour des
  rapports ».
- Commits de jalon : `41e14a9` (TP1), `d7eaf5a` (TP2), `51b04fe` (TP3), `ab5239c`
  (TP4/TP6), `7d03f0c` et `4179d8c` (TP7/TP8).
- `.env`, les captures temporaires et les journaux sont exclus par `.gitignore`.
- Contrôle : un clone neuf contient 170 fichiers et son `git status --short` est vide
  (preuve : `TP9_Deploiement/preuves/installation.txt`).

Réserve assumée : les commits sont groupés par jalon et non par membre. Le détail est
traité dans `questions_individuales.md` et dans la rétrospective.

## 2. Fiche de cadrage

`TP1_Fiche_cadrage.md` et `.docx` :

- problème : suivi papier, courriels et tableurs ; dossiers perdus, aucun état partagé ;
- références : 12 jours de validation, 35 % de dossiers incomplets, 4 conflits ;
- parties prenantes et rôles : étudiant, responsable pédagogique, encadreur, secrétariat ;
- périmètre MVP : 5 éléments inclus, 3 exclus ;
- objectifs SMART et indicateurs mesurables ;
- risques, contraintes, hypothèses et relecture.

## 3. Exigences et matrice de traçabilité

`TP2_Exigences.md` et `.docx` :

- EF-01 à EF-08 avec acteur, priorité MoSCoW, précondition et résultat attendu ;
- ENF-01 à ENF-03 : contrôle d'accès, validation serveur, sauvegarde/restauration ;
- user stories et critères d'acceptation ;
- matrice exigence → composant → test (T-01 à T-11).

Les exigences couvertes par l'API sont EF-01, EF-02, EF-03 et EF-06. EF-05
(programmation de soutenance) reste hors API et est traitée en version 2 ; le modèle et
le jeu d'essai TP3 en fournissent cependant les données.

## 4. Diagrammes UML

`TP3_Modele_donnees/` :

- cas d'utilisation : 4 acteurs, 9 cas, `cas_utilisation.svg`, `.png`, variante PlantUML ;
- classes : 9 classes avec multiplicités, `classes.puml` et `classes.png` ;
- cohérence vérifiée avec les 9 tables du schéma.

## 5. Schéma SQL

`001_schema.sql` crée la base `tp3_conventions` et les 9 tables : `utilisateur`,
`etudiant`, `encadreur`, `entreprise`, `salle`, `convention`, `disponibilite`,
`soutenance`, `historique`.

Règles portées par la base :

- un compte a au plus une fiche étudiant et une fiche encadreur (`UNIQUE`) ;
- une convention est déposée par un étudiant, accueillie par une entreprise et encadrée
  par zéro ou un encadreur ;
- cycle `BROUILLON → SOUMISE → VALIDEE | REFUSEE`, motif obligatoire en cas de refus ;
- `date_fin > date_debut`, capacité de salle bornée, durée de soutenance bornée ;
- une convention donne au plus une soutenance ; l'encadreur de la soutenance est celui de
  la convention (clé étrangère composite).

Quatre vues : `v_conventions_sans_encadreur`, `v_soutenances_conflits`,
`v_planning_soutenance`, `v_delai_publication`.

## 6. Scripts SQL versionnés et jeu d'essai

| Script | Rôle |
|---|---|
| `001_schema.sql` | Création du schéma, des contraintes et des vues |
| `002_seed.sql` | Jeu fictif : 8 comptes, 3 étudiants, 2 encadreurs, 2 entreprises, 3 salles, 6 conventions, 4 disponibilités, 2 soutenances, 9 historiques |
| `003_verification.sql` | Comptages, statuts, indicateurs, planning, délais, conflits, journal |
| `004_tests_contraintes.sql` | Insertions invalides : refus sans motif, e-mail incorrect, entreprise inconnue, période inversée, doublon, chevauchement |

**Réserve honnête** : le projet n'a pas de migration évolutive. Les scripts sont
numérotés et rejouables, mais une évolution de schéma exigerait un cinquième script de
migration. Ce point est inscrit en version 2 dans la rétrospective.

## 7. Plan de tests et fiche de recette

`TP8_Tests/` :

- `matrice_tests.md` : 14 tests, attendu écrit avant exécution ;
- `tests_securite.sh` : recharge la base, démarre l'API et rejoue les cas ;
- `preuves/sorties.tsv` : 14/14 conformes ;
- `preuves/hachages.tsv` : 8/8 mots de passe bcrypt, aucun en clair ;
- `revue_code.md` : 4 remarques classées, 3 corrigées, 1 acceptée et planifiée ;
- `recette.md` : 5 scénarios conformes, réserves et signatures.

## 8. README d'installation et ADR

- `TP4_Architecture/README.md` : prérequis, `.env`, import SQL, compte dédié, santé,
  sauvegarde et restauration.
- `TP4_Architecture/.env.example` : modèle sans secret.
- `TP4_Architecture/docs/ADR-001-monolithe-php.md` : monolithe modulaire PHP 8, quatre
  couches, PDO en requêtes préparées, aucune dépendance externe.
- `TP9_Deploiement/README.md` : installation sur un second poste par clone Git, compte
  `tp9_app`, dump et restauration vérifiée 9/9, ticket INC-001.

## Vérification finale avant dépôt

```bash
git status --short                 # aucun fichier indésirable
git log -1 --oneline               # commit de livraison
php -l public/index.php            # syntaxe du point d'entrée
php tests/test_connexion.php       # base joignable
curl -sS http://127.0.0.1:8000/api/sante   # 200, base ok
python3 -m py_compile TP9_Deploiement/build_rapport.py
```

| Contrôle | Résultat attendu | Résultat |
|---|---|---|
| Clone neuf | 170 fichiers, statut propre | OK |
| `/api/sante` | `200`, `base: ok` | OK |
| Matrice TP8 | 14/14 | OK |
| Restauration TP9 | 9/9 tables | OK |
| Mots de passe | 8/8 bcrypt | OK |

**Verdict : dossier complet pour la soutenance.** La seule réserve est l'absence de
migration évolutive et de commit par membre ; elle est assumée et planifiée en version 2.
