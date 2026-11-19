# Scénario de bout en bout — TP7

Démonstration réalisée dans Chrome (157) sur l'application servie par
`php -S 127.0.0.1:8084 -t public public/index.php`, base `tp3_conventions`
rechargée depuis `TP3_Modele_donnees/001_schema.sql` et `002_seed.sql`.

Captures conservées dans `preuves/` ; les noms sont cités à chaque étape.

## 1. Écrans de l'interface

| Écran | Rôle | Contenu |
|---|---|---|
| Connexion | tous | Carte unique : sélecteur de rôle de démonstration, e-mail, mot de passe, badge « Service actif », comptes repliés. |
| Mes demandes | étudiante | Trois compteurs (validées, en cours de revue, rejetées), tableau des conventions, bouton « Consulter ». |
| Nouvelle convention | étudiante | Formulaire entreprise, intitulé, dates, case de soumission ; encart « Circuit de validation ». |
| Détail de la convention | étudiante et responsable | Informations du stage, date de dépôt, date de décision ou motif de refus, progression du circuit. |
| Dossiers à traiter | responsable | Recherche, filtres Tous / En attente / Validés / Refusés, une carte par convention avec « Décider » ou « Consulter ». |
| Décision de convention | responsable | Résumé du dossier, éléments de contrôle, zone de motif, barre Annuler / Refuser / Valider. |

Les compteurs de la liste étudiante portent sur les conventions transmises ; une
convention au statut `BROUILLON` apparaît dans le tableau mais n'est pas comptée
dans les trois décisions.

## 2. Protocole

| # | Action | Attendu | Observé | Preuve |
|---|---|---|---|---|
| 1 | Ouvrir `http://127.0.0.1:8084/` | Écran de connexion, badge « Service actif » | Conforme | `01_connexion.png` |
| 2 | Choisir le rôle « Étudiant », se connecter avec `sena.houngbo@univ.test` / `Demo1234!` | « Mes demandes », deux conventions du jeu d'essai | « Connexion réussie. Bienvenue Sènami. », 2 lignes, compteurs 1/0/0 | `02_etudiante.png` |
| 3 | Ouvrir « Nouvelle demande », soumettre le formulaire vide | 422 : message global + un message par champ | « Données invalides. », 4 champs signalés | `03_erreurs_422.png` |
| 4 | Déposer une convention dont l'intitulé contient `<img src=x onerror=…>` | 201, statut En attente, balise affichée en texte | « Convention n° 7 enregistrée au statut En attente. », 3 lignes | `04_demande_creee.png` |
| 5 | Recharger la page (F5) | Session conservée, convention 7 toujours là | « Mes demandes », 3 lignes, aucune exécution | `05_persistance.png` |
| 6 | Cliquer « Consulter » sur la convention 7 | Détail du dossier, balise toujours en texte | « Convention n° 7 », statut En attente, intitulé littéral | `06_detail.png` |
| 7 | Se déconnecter, choisir « Responsable », se connecter comme `responsable.pedago@univ.test` | « Dossiers à traiter », 7 dossiers, 2 en attente | Conforme, un bouton « Décider » sur chaque `SOUMISE` | `07_responsable.png` |
| 8 | Cliquer « Décider » sur la convention 2 | Écran de décision, résumé et motif | Conforme | `08_decision.png` |
| 9 | Cliquer « Refuser la demande » sans motif | Message sous le champ, aucun appel réseau | « Le motif doit contenir de 3 à 255 caractères. » | `09_refus_motif.png` |
| 10 | Saisir « Période incompatible avec le calendrier de la filière » puis refuser | 200, statut Refusée, motif conservé | « Convention n° 2 : refusée. », 1 en attente | `10_refus_enregistre.png` |
| 11 | Cliquer « Décider » sur la convention 7 puis « Valider la convention » | 200, statut Validée | « Convention n° 7 : validée. », 0 en attente | `11_validation.png` |

Après l'étape 11, la base contient 7 conventions : la 7 est `VALIDEE`, la 2 est
`REFUSEE` avec le motif « Période incompatible avec le calendrier de la
filière ». Le détail de la convention 2 affiche la décision et le motif.

## 3. Gestion des erreurs

| Code | Déclencheur | Affichage |
|---|---|---|
| 400 | Corps JSON illisible | « Le corps de la requête doit être un objet JSON valide. » |
| 401 | Session absente ou expirée | « Authentification requise. », retour à l'écran de connexion |
| 422 | Validation serveur | Message global + message sous chaque champ concerné |
| 403 | Rôle ou propriétaire incorrect | « Vous n'avez pas les droits pour cette action. » |
| 409 | Décision déjà prise | « Cette décision n'est plus possible… » |
| 500 | Panne interne | « Une erreur interne est survenue. Réessayez dans un instant. » |
| 503 | Base indisponible | Badge « Service indisponible » et message dans `zone-erreur` |

Les trois premiers cas sont rendus par le composant commun `assets/api.js` :
`12_erreurs_400_401_500.png`. La capture `03_erreurs_422.png` montre le détail
par champ produit par le serveur (clés `entreprise_id`, `intitule`,
`date_debut`, `date_fin`).

## 4. Test des balises (XSS)

Deux charges ont été utilisées :

- `<img src=x onerror="document.body.dataset.xss='image'">` ;
- `<script>document.body.dataset.xss="script"></script>`.

La première a été envoyée à l'API par le formulaire (convention 7). Le tableau
puis l'écran de détail l'affichent en texte, sans créer d'élément :
`04_demande_creee.png`, `06_detail.png`, `07_responsable.png`.

La page `public/preuves/xss.html` rejoue les deux charges avec le composant de
rendu de l'application et affiche le verdict :

```text
Attribut data-xss sur <body> : absent
Éléments <img> créés dans le document : 0
Éléments <script> dans le tableau rendu : 0
Résultat : les deux charges apparaissent en texte ; aucune balise n'est interprétée.
```

Détail : `preuves/xss_verification.txt` et DOM complet
`preuves/xss_dom.html`.

## 5. Reproduire

```bash
cd TP4_Architecture
php -S 127.0.0.1:8084 -t public public/index.php
```

Puis ouvrir `http://127.0.0.1:8084/`. Les pages de preuve sont accessibles à
`/preuves/erreurs.html` et `/preuves/xss.html` ; elles ne sont pas liées depuis
l'application.

La base peut être remise à zéro à tout moment :

```bash
mysql -u root --socket=/tmp/mysql-tp3-oussou.sock < ../TP3_Modele_donnees/001_schema.sql
mysql -u root --socket=/tmp/mysql-tp3-oussou.sock < ../TP3_Modele_donnees/002_seed.sql
```

Les scripts `TP8_Tests/tests_securite.sh` et `TP6_API/tests_api.sh` rechargent
eux-mêmes la base avant chaque exécution.
