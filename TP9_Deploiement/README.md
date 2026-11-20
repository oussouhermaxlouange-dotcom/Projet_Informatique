# TP9 — Déploiement, compte SQL dédié et sauvegarde

**Projet informatique 2 · L3 SIL**  
Application Web de gestion des stages et des soutenances  
Membres : OUSSOU Hermax, TCHEGNON Loïk, KANHONOU Ashley  
Encadreur : MAMA Tairou — 20/11/2026

## Objectif

Installer l'application sur un second poste en suivant **uniquement** le README, créer un
compte SQL à droits limités, vérifier la page de santé, produire une sauvegarde
`mysqldump`, la restaurer sur une base de test et rédiger un ticket d'incident
reproductible.

Ce dossier contient :

| Fichier | Contenu |
|---|---|
| `README.md` | Ce document : protocole, résultats et étapes manquantes du README |
| `ticket_incident.md` | Ticket INC-001 complet et reproductible |
| `preuves/installation.txt` | Préparation de l'instance, import SQL, santé et connexion |
| `preuves/compte_sql.txt` | Droits de `tp9_app` et refus `ERROR 1142` |
| `preuves/sauvegarde.txt` | Commande, taille et empreinte SHA-256 du dump |
| `preuves/restauration.txt` | Comparaison des `COUNT(*)` et test de perte |
| `preuves/incident_reproduction.txt` | Incident `503`, journal PHP et correction `200` |
| `preuves/tp3_conventions.sql` | Sauvegarde réelle de la base (23 961 octets) |
| `deploiement_tp9.html` / `.pdf` / `.docx` | Rapport 2 pages A4, noir et blanc |
| `build_rapport.py`, `build_docx.py` | Génération du rapport |

## 1. Protocole d'installation

Le second poste est un clone Git réel du dépôt, dans un dossier isolé, installé en
suivant **uniquement** le README du clone :

```bash
git clone file:///home/oussou-hermax/Images/Projets informatique\ 2 \
          /tmp/opencode/tp9_poste2_git
cd /tmp/opencode/tp9_poste2_git/TP4_Architecture
cp .env.example .env
# renseigner DB_USER, DB_PASSWORD et DB_SOCKET
php -S 127.0.0.1:8098 -t public public/index.php
```

Le clone est propre (`git status --short` vide), sur le commit `4179d8c`, et contient
170 fichiers. Le serveur MySQL de démonstration est une instance isolée, pour ne pas
toucher la base principale du poste :

```bash
mysqld --no-defaults --datadir=/tmp/opencode/mysql_tp9/data \
       --socket=/tmp/opencode/mysql_tp9/run/mysql.sock --port=3309 \
       --bind-address=127.0.0.1 --mysqlx=0
```

| Étape | Commande / contrôle | Résultat obtenu |
|---|---|---|
| 1. Prérequis | `php -v`, `php -m \| grep pdo_mysql` | PHP 8.5.12, `pdo_mysql` présent |
| 2. Configuration | `cp .env.example .env` puis édition | fichier en `chmod 600` |
| 3. Base | import `001_schema.sql` puis `002_seed.sql` | 8 utilisateurs, 6 conventions |
| 4. Compte dédié | `CREATE USER 'tp9_app'@'localhost'` | droits limités à `tp3_conventions` |
| 5. Lancement | `php -S 127.0.0.1:8098 …` | serveur démarré |
| 6. Santé | `curl -i /api/sante` | `200` `{"statut":"ok","base":"ok"}` |
| 7. Connexion | `POST /api/connexion` | `200`, rôle `ETUDIANT` |
| 8. Lecture | `GET /api/demandes` avec cookie | `200`, demandes de l'étudiante |

Preuve : `preuves/installation.txt`.

## 2. Compte SQL à droits limités

Le compte applicatif ne doit jamais être `root`. Le compte créé est
`tp9_app@localhost`, avec un mot de passe propre et **quatre** droits seulement, sur
la seule base du projet :

```sql
CREATE USER 'tp9_app'@'localhost' IDENTIFIED BY 'Tp9Demo!2026';
GRANT SELECT, INSERT, UPDATE, DELETE ON tp3_conventions.* TO 'tp9_app'@'localhost';
FLUSH PRIVILEGES;
```

Aucun privilège `DROP`, `CREATE`, `ALTER`, `GRANT` ni `FILE`. Le contrôle réel :

```text
GRANT SELECT, INSERT, UPDATE, DELETE ON `tp3_conventions`.* TO `tp9_app`@`localhost`

$ DROP TABLE tp3_conventions.historique;
ERROR 1142 (42000): DROP command denied to user 'tp9_app'@'localhost' for table 'historique'

$ CREATE TABLE tp3_conventions.essai (id INT);
ERROR 1142 (42000): CREATE command denied to user 'tp9_app'@'localhost' for table 'essai'
```

Après les deux refus, `historique` contient toujours ses 9 lignes. Preuve :
`preuves/compte_sql.txt`.

## 3. Sauvegarde

```bash
mysqldump -u root --socket=/tmp/opencode/mysql_tp9/run/mysql.sock \
          --single-transaction --routines --triggers \
          tp3_conventions > preuves/tp3_conventions.sql
```

| Indicateur | Valeur |
|---|---|
| Code de sortie | `0` |
| Taille | 23 961 octets (24 Kio) |
| Lignes | 467 |
| SHA-256 | `a67aacad019f174a9cd58133bb4502c3a14fc4c17fac9ea2a134ce9ca4d37182` |

`--single-transaction` garantit un instantané cohérent sans bloquer les écritures ;
`--routines` et `--triggers` conservent les objets de programmation. Preuve :
`preuves/sauvegarde.txt`.

## 4. Restauration vérifiée

La restauration se fait **sur une base de test**, jamais sur la base de production :

```bash
mysql -u root --socket=… -e "CREATE DATABASE tp3_conventions_restauration …"
mysql -u root --socket=… tp3_conventions_restauration < preuves/tp3_conventions.sql
```

Comparaison des `COUNT(*)` entre la base source et la base restaurée :

| Table | Source | Restaurée | Verdict |
|---|---|---|---|
| `utilisateur` | 8 | 8 | OK |
| `etudiant` | 3 | 3 | OK |
| `encadreur` | 2 | 2 | OK |
| `entreprise` | 2 | 2 | OK |
| `salle` | 3 | 3 | OK |
| `convention` | 6 | 6 | OK |
| `disponibilite` | 4 | 4 | OK |
| `soutenance` | 2 | 2 | OK |
| `historique` | 9 | 9 | OK |

**9/9 tables identiques.** Le test de perte supprime ensuite `historique` dans la base
de test (`table absente`), réimporte le dump et retrouve **9/9 tables identiques**.
Preuve : `preuves/restauration.txt`.

## 5. Étapes manquantes du README (et corrections apportées)

Le README du TP4 a été suivi à la lettre. Quatre manques ont été relevés puis corrigés
dans `TP4_Architecture/README.md` :

| Manque constaté | Conséquence | Correction apportée |
|---|---|---|
| `DB_SOCKET` absent du bloc `.env` exemple | socket obligatoire non découvert | variable ajoutée, avec règle « socket prioritaire » |
| Aucun contrôle de l'existence du socket | `503` difficile à diagnostiquer | commande `test -S` et lecture du journal PHP |
| Aucune procédure de sauvegarde/restauration | reprise après perte impossible | section dédiée avec `mysqldump` et restauration sur base de test |
| Aucune vérification des droits du compte | risque de compte trop permissif | contrôle `SHOW GRANTS` et test de refus `DROP` |

## 6. Incident

L'incident INC-001 (`ticket_incident.md`) reproduit un `503` causé par un `DB_SOCKET`
obsolète : le fichier socket n'existe plus, PDO répond
`SQLSTATE[HY000] [2002] No such file or directory`, la route de santé renvoie
`503 BASE_INDISPONIBLE`. Le diagnostic, la correction et la prévention sont détaillés
dans le ticket et rejoués dans `preuves/incident_reproduction.txt`.

## 7. Livrables TP9

- [x] Installation sur un second poste en suivant uniquement le README
- [x] Compte SQL dédié `tp9_app` avec droits `SELECT, INSERT, UPDATE, DELETE`
- [x] Import SQL, serveur démarré, `/api/sante` à `200`
- [x] Sauvegarde `mysqldump` avec taille et empreinte
- [x] Suppression d'une table sur base de test, restauration, `COUNT(*)` comparés
- [x] README d'installation complété
- [x] Ticket d'incident reproductible
