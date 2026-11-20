# TP10 — Dossier de livraison et soutenance

**Projet informatique 2 · L3 SIL**  
Application Web de gestion des stages et des soutenances  
Membres : OUSSOU Hermax, TCHEGNON Loïk, KANHONOU Ashley  
Encadreur : MAMA Tairou — 20/11/2026

## Contenu du dossier

| Fichier | Rôle |
|---|---|
| `dossier_livraison.md` | Liste de contrôle des 8 éléments, avec emplacement, vérification et état |
| `scenario_demonstration.md` | Scénario minuté de 8 minutes, preuves par séquence, répétition et repli |
| `questions_individuales.md` | Règle métier, requête, test et commit pour chaque membre |
| `retrospective.md` | Point positif, difficulté, changements pour la version 2 |
| `soutenance_tp10.html` / `.pdf` / `.docx` | Rapport 2 pages A4, noir et blanc |
| `build_rapport.py`, `build_docx.py` | Génération du rapport |

## 1. Dossier de livraison

Les huit éléments vérifiés :

1. dépôt Git et historique ;
2. fiche de cadrage TP1 ;
3. exigences et matrice de traçabilité TP2 ;
4. diagrammes UML TP3 ;
5. schéma SQL TP3 ;
6. scripts SQL versionnés et jeu d'essai ;
7. plan de tests et fiche de recette TP8 ;
8. README d'installation et ADR TP4/TP9.

Le dossier est complet. Deux réserves sont assumées et documentées : l'absence de
migration évolutive (les scripts sont numérotés et rejouables, mais aucune évolution de
schéma n'a encore eu lieu) et l'historique Git groupé par jalon plutôt que par membre.
Les deux sont inscrites dans la rétrospective.

## 2. Démonstration de 8 minutes

| Temps | Séquence | Preuve |
|---|---|---|
| 0:00–1:00 | Contexte et problème | indicateurs du TP1 |
| 1:00–3:00 | Dépôt d'une demande | ligne `SOUMISE` en base |
| 3:00–4:00 | Validation | statut `VALIDEE` + historique |
| 4:00–5:00 | Programmation de la soutenance | `v_planning_soutenance`, conflits à 0 |
| 5:00–6:00 | Contrôle d'accès | `403 ACCES_REFUSE` |
| 6:00–8:00 | Tests et bilan | 14/14, 8/8 bcrypt, 9/9 restaurées |

La programmation de soutenance (EF-05) n'est pas exposée par l'API : elle est montrée par
la vue de planning du TP3, puis annoncée en version 2. Le scénario ne simule pas une
fonctionnalité inexistante.

## 3. Solution de repli

- vidéo locale de 8 minutes, sans montage ;
- 13 captures TP7 et preuves TP8/TP9 ;
- dump TP9 restauré en moins de 2 minutes ;
- rapports PDF ouverts hors ligne ;
- second profil de navigateur pour la preuve `403`.

Détail et procédure : `scenario_demonstration.md`.

## 4. Questions individuelles

Chaque membre prépare quatre réponses :

| Membre | Règle métier | Requête | Test | Commit |
|---|---|---|---|---|
| Hermax | refus sans motif → `422` | `UPDATE convention …` préparée | T-02 | `ab5239c` |
| Loïk | une convention → au plus une soutenance | `v_planning_soutenance` | contraintes TP3 | `bd0ed02` |
| Ashley | bcrypt + contrôle `Origin` | `SELECT … WHERE email = :email` | T-13, T-10 | `4179d8c` |

Les réponses complètes, les relances et la grille d'auto-évaluation sont dans
`questions_individuales.md`.

## 5. Rétrospective

- **Point positif** : chaîne de preuve exigence → composant → test → sortie ;
  restauration 9/9 après perte volontaire.
- **Difficulté** : commits groupés en fin de jalon, EF-05 hors API, socket MySQL
  obsolète.
- **Version 2** : un commit par fonctionnalité et par membre, CI minimale, EF-05 avec
  contrôle de conflit, migrations versionnées, limitation des tentatives.

Détail : `retrospective.md`.

## 6. Régénérer le rapport

```bash
cd TP10_Soutenance
python3 build_rapport.py
# HTML, PDF (Chrome headless) et DOCX (LibreOffice/UNO)
pdfinfo soutenance_tp10.pdf | grep Pages   # attendu : 2
```

## 7. Vérifications avant la soutenance

```bash
git status --short
git log -1 --oneline
mysql -u root -p < TP3_Modele_donnees/001_schema.sql
mysql -u root -p < TP3_Modele_donnees/002_seed.sql
cd TP4_Architecture && php -S 127.0.0.1:8000 -t public public/index.php
curl -sS http://127.0.0.1:8000/api/sante
```

Checklist détaillée et verdict : `dossier_livraison.md`.
