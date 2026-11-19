# Procès-verbal de recette — TP8

Projet informatique 2 · L3 SIL — application de gestion des stages  
Groupe : OUSSOU Hermax, TCHEGNON Loïk, KANHONOU Ashley — encadreur MAMA Tairou  
Date de recette : 19 novembre 2026

## 1. Objet et périmètre

La recette vérifie que l'application livrée (API `TP4_Architecture/` et interface
`TP4_Architecture/public/`) satisfait les exigences EF-01 à EF-03 et ENF-01 à
ENF-02 du TP2, sur le jeu de données fictif du TP3.

L'interface compte six écrans : Connexion, Mes demandes, Nouvelle convention,
Détail de la convention, Dossiers à traiter et Décision de convention. La
décision est un écran complet, sans fenêtre modale.

Hors périmètre : déploiement sur un second poste (TP9), sauvegarde/restauration
(TP9), rôles `ENCADREUR` et `DEVELOPPEUR`, import de fichiers.

## 2. Environnement de recette

| Élément | Valeur |
|---|---|
| Système | Ubuntu 24.04 |
| PHP | 8.3, extensions `pdo_mysql` et `session` |
| Base | MySQL 8.0.46, base `tp3_conventions` |
| Jeu de données | `TP3_Modele_donnees/001_schema.sql` puis `002_seed.sql` |
| Navigateur | Chrome 157, fenêtre 1280 × 900 |
| Serveur | `php -S 127.0.0.1:8084 -t public public/index.php` |
| Comptes | `sena.houngbo@univ.test` (A), `ibrahim.sanni@univ.test` (B), `responsable.pedago@univ.test` — mot de passe `Demo1234!` |

État initial attendu : 6 conventions (1 `BROUILLON`, 2 `SOUMISE`, 3 et 4
`VALIDEE`, 5 `REFUSEE`, 6 `VALIDEE`), 8 comptes.

## 3. Scénarios de recette

### S1 — Connexion étudiante et dépôt d'une convention

| # | Action | Résultat attendu | Résultat observé | Verdict |
|---|---|---|---|---|
| 1 | Ouvrir `http://127.0.0.1:8084/` | Écran de connexion, badge « Service actif » | Conforme | OK |
| 2 | Choisir le rôle « Étudiant », saisir `sena.houngbo@univ.test` / `Demo1234!`, valider | « Mes demandes », « Connexion réussie. Bienvenue Sènami. », 2 conventions, compteurs 1 / 0 / 0 | Conforme | OK |
| 3 | Ouvrir « Nouvelle demande », remplir entreprise « Studio Kora », intitulé de 5 à 120 caractères, dates 01/03/2027 → 30/06/2027, soumettre | « Convention n° 7 enregistrée au statut En attente. », 3 lignes dans « Mes demandes » | Conforme | OK |
| 4 | Recharger la page (F5) | Session conservée, convention 7 toujours affichée | Conforme | OK |

Preuve : `TP7_Frontend/preuves/01_connexion.png`, `02_etudiante.png`,
`04_demande_creee.png`, `05_persistance.png`.

### S2 — Formulaire invalide et erreurs lisibles

| # | Action | Résultat attendu | Résultat observé | Verdict |
|---|---|---|---|---|
| 1 | Soumettre le formulaire « Nouvelle convention » vide | Message global « Données invalides. », un message sous chacun des 4 champs, `aria-invalid="true"` | Conforme | OK |
| 2 | Saisir une date de début postérieure à la date de fin, soumettre | `422`, message serveur sur le champ concerné, aucune création | Conforme | OK |
| 3 | Se connecter avec un mot de passe faux | `401`, « Votre session a expiré ou les identifiants sont incorrects. », pas de session ouverte | Conforme | OK |

Preuve : `TP7_Frontend/preuves/03_erreurs_422.png`,
`TP7_Frontend/preuves/12_erreurs_400_401_500.png`.

### S3 — Validation d'une convention par le responsable

| # | Action | Résultat attendu | Résultat observé | Verdict |
|---|---|---|---|---|
| 1 | Se connecter comme `responsable.pedago@univ.test` | Écran « Dossiers à traiter », 7 dossiers, 2 en attente, filtres Tous / En attente / Validés / Refusés, bouton « Décider » sur les `SOUMISE` seulement | Conforme | OK |
| 2 | Cliquer « Décider » sur la convention 7, puis « Valider la convention » | « Convention n° 7 : validée. », statut `Validée`, bouton remplacé par « Consulter », 1 en attente | Conforme | OK |
| 3 | Rejouer la validation de la convention 3 (déjà validée) par l'API | `409 TRANSITION_INTERDITE`, statut inchangé | Conforme | OK |

Preuve : `TP7_Frontend/preuves/07_responsable.png`,
`TP7_Frontend/preuves/11_validation.png`, `preuves/sorties.tsv` T-03.

### S4 — Refus motivé

| # | Action | Résultat attendu | Résultat observé | Verdict |
|---|---|---|---|---|
| 1 | Cliquer « Décider » sur la convention 2, puis « Refuser la demande » sans motif | Écran de décision maintenu, message « Le motif doit contenir de 3 à 255 caractères. », focus placé sur le motif, aucun appel réseau | Conforme | OK |
| 2 | Saisir « Période incompatible avec le calendrier de la filière », puis « Refuser la demande » | « Convention n° 2 : refusée. », statut `Refusée`, motif conservé et visible dans le détail | Conforme | OK |
| 3 | Rejouer un refus sans motif par l'API | `422 VALIDATION`, statut toujours `SOUMISE` en base | Conforme | OK |

Preuve : `TP7_Frontend/preuves/09_refus_motif.png`,
`TP7_Frontend/preuves/10_refus_enregistre.png`, `preuves/sorties.tsv` T-02.

### S5 — Autorisations, injection et rendu sécurisé

| # | Action | Résultat attendu | Résultat observé | Verdict |
|---|---|---|---|---|
| 1 | Session B, `GET /api/demandes/1` | `403 ACCES_REFUSE`, aucun contenu du dossier de A | Conforme | OK |
| 2 | Session responsable, `GET /api/demandes/1%20OR%201=1` | `404 DEMANDE_INCONNUE` | Conforme | OK |
| 3 | `POST /api/connexion` avec `Origin: http://evil.test` | `403 ORIGINE_REFUSEE`, aucune session | Conforme | OK |
| 4 | Déposer un intitulé contenant `<img src=x onerror=…>`, afficher le tableau étudiante, le détail et les cartes du responsable | Balise affichée en texte, `data-xss` absent, 0 élément `img` créé | Conforme | OK |
| 5 | Contrôler les empreintes en base | 8/8 bcrypt, 0 mot de passe en clair | Conforme | OK |

Preuve : `preuves/sorties.tsv` T-05, T-06, T-10, T-11,
`preuves/hachages.tsv`, `TP7_Frontend/preuves/xss_verification.txt`.

## 4. Synthèse

| Scénario | Exigences couvertes | Verdict |
|---|---|---|
| S1 — Connexion et dépôt | EF-01, EF-02, EF-06 | Conforme |
| S2 — Erreurs lisibles | EF-02, ENF-02 | Conforme |
| S3 — Validation | EF-03, ENF-01 | Conforme |
| S4 — Refus motivé | EF-03 | Conforme |
| S5 — Sécurité | ENF-01, ENF-02 | Conforme |

**5 scénarios sur 5 conformes.** Les 14 tests automatisés de
`tests_securite.sh` sont également conformes (`preuves/resume.txt`).

## 5. Réserves et suites

| Réf. | Réserve | Incidence | Suite |
|---|---|---|---|
| R-04 | Pas de limitation des tentatives de connexion | Brute force possible en local | À corriger avant mise en ligne (`revue_code.md`) |
| — | Rôles `ENCADREUR` et `DEVELOPPEUR` sans écran dédié | Aucun impact sur les parcours recettés | Backlog TP10 |
| — | Jeton CSRF de session non implémenté | Couverture assurée par `SameSite=Lax` + contrôle `Origin` | Backlog si formulaire HTML classique |

Aucune réserve ne bloque la réception du livrable TP7/TP8.

## 6. Signatures

| Rôle | Nom | Date | Signature |
|---|---|---|---|
| Membre du groupe (recette) | OUSSOU Hermax | 19/11/2026 | |
| Membre du groupe (recette) | TCHEGNON Loïk | 19/11/2026 | |
| Membre du groupe (recette) | KANHONOU Ashley | 19/11/2026 | |
| Encadreur (visa) | MAMA Tairou | | |

Mention à apposer : « Reçu le livrable TP7/TP8, 5 scénarios sur 5 conformes,
réserves R-04 et backlog consignés. »
