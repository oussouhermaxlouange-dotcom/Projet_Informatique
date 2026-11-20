# Scénario de démonstration — 8 minutes

**Projet informatique 2 · L3 SIL** — Plateforme de suivi des conventions  
Membres : OUSSOU Hermax, TCHEGNON Loïk, KANHONOU Ashley  
Encadreur : MAMA Tairou — répétition du 20/11/2026

## 1. Règles du scénario

- Durée cible : **8 min 00 s** ; marge de sécurité : 20 s.
- Un seul narrateur à la fois ; les deux autres préparent la preuve suivante.
- Chaque séquence se termine par une **preuve visible** : écran, ligne SQL ou fichier.
- Aucune saisie improvisée : les données sont préparées avant l'entrée du jury.
- La programmation de soutenance (EF-05) n'est pas exposée par l'API : elle est montrée
  par la vue `v_planning_soutenance` du TP3, puis annoncée en version 2. On ne fait pas
  croire que l'écran existe.

## 2. Préparation avant la soutenance

```bash
# 1. Base rechargée depuis le jeu fictif TP3
mysql -u root -p < TP3_Modele_donnees/001_schema.sql
mysql -u root -p < TP3_Modele_donnees/002_seed.sql

# 2. Application démarrée
cd TP4_Architecture
php -S 127.0.0.1:8000 -t public public/index.php

# 3. Contrôle de santé
curl -sS http://127.0.0.1:8000/api/sante

# 4. Deux profils de navigateur : étudiante et responsable
#    (ou deux fenêtres, l'une en navigation privée)
```

| Contrôle | Attendu | Fait |
|---|---|---|
| Base rechargée | 8 comptes, 6 conventions, 2 soutenances | ☐ |
| `/api/sante` | `200`, `base: ok` | ☐ |
| Connexion étudiante | `sena.houngbo@univ.test` / `Demo1234!` | ☐ |
| Connexion responsable | `responsable.pedago@univ.test` / `Demo1234!` | ☐ |
| Dump de secours | `TP9_Deploiement/preuves/tp3_conventions.sql` | ☐ |
| Vidéo de secours | 8 minutes, lue en local | ☐ |
| Rapports PDF | TP8 et TP9 ouverts dans un onglet | ☐ |
| Chronomètre | visible, remis à zéro | ☐ |

## 3. Déroulé minuté

| Temps | Séquence | Qui | Ce qui est dit | Preuve montrée |
|---|---|---|---|---|
| 0:00–1:00 | Contexte et problème | Hermax | Suivi papier et courriels : 12 jours de validation, 35 % de dossiers incomplets, 4 conflits. Le MVP centralise le dossier et l'état partagé. | Tableau des indicateurs du TP1 |
| 1:00–3:00 | Dépôt d'une demande | Loïk | Connexion étudiante, « Nouvelle convention » : entreprise, intitulé, dates, soumission. Les erreurs sont lisibles, la validation est serveur. | Écran de confirmation, puis ligne créée : `SELECT id, statut, date_depot FROM convention ORDER BY id DESC LIMIT 1;` → `SOUMISE` |
| 3:00–4:00 | Validation | Hermax | Connexion responsable, dossier filtré « En attente », décision « Valider ». La transaction écrit le statut et l'historique. | Écran « Validée », puis `SELECT statut FROM convention WHERE id = …;` et ligne d'historique |
| 4:00–5:00 | Programmation de la soutenance | Ashley | Le modèle TP3 porte salles, disponibilités et soutenances ; la vue planning donne les créneaux et la vue conflits doit rester vide. L'API n'expose pas encore EF-05 : c'est la priorité de la version 2. | `SELECT * FROM v_planning_soutenance;` (2 soutenances), `SELECT COUNT(*) FROM v_soutenances_conflits;` → `0` |
| 5:00–6:00 | Contrôle d'accès | Loïk | Session de l'étudiant B vers le dossier de A : la réponse est `403`, sans données. Le rôle et la propriété sont vérifiés côté serveur. | `curl -i` avec le cookie de B → `403 ACCES_REFUSE` |
| 6:00–8:00 | Tests et bilan | Ashley puis Hermax | 14/14 tests, 8/8 mots de passe bcrypt, restauration 9/9. Choix assumés : PHP/PDO, transaction, contrôle serveur. Version 2 : EF-05, migrations, limitation des tentatives. | `TP8_Tests/preuves/resume.txt`, `TP9_Deploiement/preuves/restauration.txt`, matrice projetée |

### Script de la preuve 403

```bash
# Session B (Ibrahim SANNI, étudiant 2)
curl -sS -c /tmp/b.txt -H 'Content-Type: application/json' \
     -d '{"email":"ibrahim.sanni@univ.test","mot_de_passe":"Demo1234!"}' \
     http://127.0.0.1:8000/api/connexion

# Accès au dossier de A (convention 1, étudiante 1)
curl -sS -i -b /tmp/b.txt http://127.0.0.1:8000/api/demandes/1
# Attendu : HTTP/1.1 403 Forbidden — {"erreur":{"code":"ACCES_REFUSE",…}}
```

Si le compte B n'existe pas dans le jeu d'essai, utiliser la session de l'étudiante A
pour appeler `PATCH /api/demandes/2/statut` : la réponse est `403 ROLE_NON_AUTORISE`.
La preuve d'autorisation reste valable : c'est le serveur qui refuse.

## 4. Répétition au chronomètre

| Passage | Durée | Écart | Décision |
|---|---|---|---|
| 1 | 9 min 10 s | +70 s | contexte réduit à 45 s, tests ramenés à 90 s |
| 2 | 8 min 05 s | +5 s | suppression d'une phrase sur les vues |
| 3 | 7 min 52 s | −8 s | marge conservée, le rythme est bon |

Le scénario retenu est celui du passage 3. Les commandes SQL sont pré-écrites dans un
fichier pour éviter les fautes de frappe et gagner du temps.

## 5. Solution de repli

| Panne | Réaction immédiate | Preuve de substitution |
|---|---|---|
| Serveur PHP arrêté | relancer `php -S` ; si échec, passer à la vidéo | vidéo de 8 min |
| Base indisponible | restaurer le dump TP9 (moins de 2 min) | `preuves/restauration.txt` |
| Réseau ou vidéoprojecteur | passer sur le poste local, rapport PDF | `TP8_Tests/tests_securite.pdf` |
| Mauvais compte ou session | changer de profil navigateur | captures TP7 `01…13.png` |
| Question sur EF-05 | montrer la vue planning et annoncer la v2 | `v_planning_soutenance` |

La vidéo de secours montre exactement le même parcours, sans montage : elle est lancée
seulement si l'application ne répond plus. Les captures et les rapports restent
accessibles hors ligne.

## 6. Répartition de la parole

| Membre | Séquences | Durée de parole |
|---|---|---|
| OUSSOU Hermax | contexte, validation, bilan technique | 3 min 00 s |
| TCHEGNON Loïk | dépôt, contrôle d'accès | 2 min 30 s |
| KANHONOU Ashley | planning, tests et sécurité | 2 min 30 s |

Chacun sait répondre aux questions de son périmètre, mais aussi expliquer le parcours
complet : aucune partie n'est isolée.

## 7. Ce qui est volontairement exclu de la démonstration

- la création d'un compte ou d'une entreprise (hors périmètre de l'interface) ;
- la programmation réelle d'une soutenance par l'API (EF-05, version 2) ;
- les rôles `ENCADREUR` et `DEVELOPPEUR` sans écran dédié ;
- les notifications et le portail entreprise (version 2).
