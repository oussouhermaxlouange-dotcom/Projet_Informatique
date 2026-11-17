# TP3 — UML et modélisation des données

Plateforme de suivi des conventions de stage et des soutenances — Projet
informatique 2, L3 SIL.

Le dossier contient le modèle UML corrigé (cas d'utilisation et classes), le
schéma relationnel MySQL, un jeu d'essai fictif et les sorties de vérification.
Le rapport `TP3_Modele_donnees.docx` (et son aperçu PDF) rassemble le tout en
noir et blanc.

## Fichiers

| Fichier | Contenu |
|---|---|
| `TP3_Modele_donnees.docx` | Rapport à rendre : diagrammes, tables, scénario, scripts et résultats. |
| `TP3_Modele_donnees.pdf` | Aperçu du rapport. |
| `cas_utilisation.svg` / `cas_utilisation.png` | Diagramme de cas d'utilisation corrigé (4 acteurs, 9 cas), source SVG et rendu PNG. |
| `cas_utilisation.puml` | Variante PlantUML équivalente du diagramme de cas d'utilisation. |
| `classes.puml` / `classes.png` | Diagramme de classes (9 classes, multiplicités). |
| `001_schema.sql` | Création de la base `tp3_conventions`, des 9 tables, contraintes et 4 vues. |
| `002_seed.sql` | Jeu fictif : 8 comptes, 3 étudiants, 2 encadreurs, 2 entreprises, 3 salles, 6 conventions, 4 disponibilités, 2 soutenances, 9 historiques. |
| `003_verification.sql` | Comptages, statuts, indicateurs, planning, délais, conflits et journal. |
| `004_tests_contraintes.sql` | Insertions invalides : refus sans motif, email incorrect, entreprise inconnue, période inversée, doublon et chevauchement. |
| `sortie_verification.txt` | Sortie brute de `003_verification.sql`. |
| `sortie_tests_contraintes.txt` | Sortie brute de `004_tests_contraintes.sql`. |
| `scenario_validation.md` | Scénario « Confirmer une convention » et codes HTTP. |
| `build_docx.py` | Script de génération du rapport DOCX via LibreOffice UNO. |

## Modèle retenu

Le schéma compte neuf tables : `utilisateur`, `etudiant`, `encadreur`,
`entreprise`, `salle`, `convention`, `disponibilite`, `soutenance` et
`historique`.

Règles portées par la base :

- un compte a au plus une fiche étudiant et une fiche encadreur (`UNIQUE`) ;
- une convention est déposée par un étudiant, accueillie par une entreprise et
  encadrée par zéro ou un encadreur ;
- une convention validée peut rester sans encadreur : la vue
  `v_conventions_sans_encadreur` sert d'indicateur d'affectation ;
- une convention donne au plus une soutenance ; l'encadreur de la soutenance
  est celui de la convention (clé étrangère composite) ;
- les doublons exacts salle/créneau et encadreur/créneau sont interdits par des
  clés `UNIQUE` ; les chevauchements de durée sont détectés par
  `v_soutenances_conflits` ;
- un refus sans motif, une décision sans date ou une période inversée sont
  rejetés par des contraintes `CHECK` ;
- chaque changement de statut laisse une ligne dans `historique`.

## Rejouer la base

```bash
mysql -u root < 001_schema.sql
mysql -u root < 002_seed.sql
mysql -u root --table < 003_verification.sql
mysql -u root --force --table < 004_tests_contraintes.sql
```

Les scripts créent et utilisent la base `tp3_conventions` ; aucune autre base
n'est modifiée. `001_schema.sql` supprime les vues puis les tables dans l'ordre
inverse des dépendances : le dossier est rejouable sur une base vide.

Le mot de passe commun des comptes fictifs est `Demo1234!` ; seul son hash est
stocké. Les adresses en `@univ.test` et les noms sont inventés : ne pas importer
de données réelles.

## Régénérer les diagrammes

Le diagramme de cas d'utilisation est produit à partir de `cas_utilisation.svg` : le
SVG est capturé en PNG haute résolution, puis le rapport est régénéré. La
variante `cas_utilisation.puml` décrit le même contenu pour PlantUML :

```bash
java -jar plantuml.jar -tpng classes.puml cas_utilisation.puml
```

Une correction du modèle se fait dans la source du diagramme, puis le PNG et le
DOCX sont régénérés.

## Résultat attendu des vérifications

- 8 utilisateurs, 3 étudiants, 2 encadreurs, 2 entreprises, 3 salles ;
- 6 conventions : 1 brouillon, 1 soumise, 3 validées, 1 refusée ;
- 1 convention validée sans encadreur ;
- 2 soutenances planifiées, 0 conflit de salle ou d'encadreur ;
- délais de publication de 4 et 5 jours, conformes à la cible de 5 jours.
