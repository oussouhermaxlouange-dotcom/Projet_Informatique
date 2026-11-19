# TP7 — Interface et intégration

Livrable du TP7 : parcours des deux rôles, formulaire accessible, appels `fetch`,
affichage sécurisé et scénario de bout en bout documenté.

L'interface n'est pas dupliquée ici : elle est servie par la même application que
l'API, dans `../TP4_Architecture/public/`. Même origine, donc même cookie de
session et aucune configuration CORS. Ce dossier contient le parcours, le
scénario et les preuves.

Groupe : OUSSOU Hermax, TCHEGNON Loïk, KANHONOU Ashley — encadreur MAMA Tairou.

## Contenu

| Fichier | Rôle |
|---|---|
| `parcours.svg` / `parcours.png` | Parcours des deux rôles : écrans, actions, échanges entre étudiante et responsable. |
| `scenario.md` | Scénario complet joué dans Chrome : créer, consulter, filtrer, valider, refuser, persistance. |
| `preuves/01_connexion.png` … `13_xss.png` | 13 captures réelles, dans l'ordre du scénario. |
| `preuves/xss_dom.html` | DOM complet de la page de preuve XSS, produit par Chrome. |
| `preuves/xss_verification.txt` | Vérification chiffrée : 0 balise créée, `data-xss` absent. |
| `build_rapport.py` | Génère le HTML depuis les preuves, puis le PDF (Chrome) et le DOCX (UNO). |
| `build_docx.py` | Construit le DOCX avec le constructeur UNO partagé `../outils/rapport_uno.py`. |
| `interface_tp7.html` / `.pdf` / `.docx` | Rapport 2 pages A4, noir et blanc, avec le schéma des parcours. |
| `README.md` | Ce document. |

L'interface elle-même est dans `../TP4_Architecture/public/` :

| Fichier | Rôle |
|---|---|
| `index.html` | Six écrans : connexion, mes demandes, nouvelle convention, détail, dossiers à traiter, décision. |
| `assets/app.css` | Feuille de style unique : fond ivoire, accent violet, cartes blanches, boutons noirs, adaptation mobile. |
| `assets/api.js` | `fetch` avec `credentials: 'same-origin'`, lecture JSON, messages d'erreur lisibles. |
| `assets/rendu.js` | Tableau étudiante, cartes du responsable et compteurs, **exclusivement** avec `textContent`. |
| `assets/app.js` | Orchestration : navigation entre écrans, session, rôles, formulaire, filtres, décisions. |
| `assets/favicon.svg` | Icône locale, aucune requête externe. |
| `preuves/erreurs.html` | Page de preuve des erreurs 400, 401 et 500. |
| `preuves/xss.html` | Page de preuve du rendu par `textContent`. |

## Les six écrans

| Écran | Rôle | Contenu et actions |
|---|---|---|
| **Connexion** | tous | Carte unique centrée : sélecteur de démonstration Étudiant / Responsable, e-mail, mot de passe, badge « Service actif », comptes repliés dans un `<details>`. |
| **Mes demandes** | étudiante | En-tête « Mes demandes » + nombre de conventions, trois compteurs (Validées, En cours de revue, Rejetées), tableau des conventions, bouton « Nouvelle demande », bouton « Actualiser ». |
| **Nouvelle convention** | étudiante | Formulaire entreprise, intitulé, deux dates, case « Soumettre la convention » ; encart « Circuit de validation » en trois étapes. |
| **Détail de la convention** | étudiante et responsable | Informations du stage, dates de dépôt et de décision, motif de refus si `REFUSEE`, barre de progression du circuit. |
| **Dossiers à traiter** | responsable | Recherche par étudiant / entreprise / intitulé, filtres Tous / En attente / Validés / Refusés, une carte par convention avec « Décider » si `SOUMISE`, sinon « Consulter ». |
| **Décision de convention** | responsable | Résumé du dossier en quatre cartes, éléments de contrôle, zone de motif, barre Annuler / Refuser la demande / Valider la convention. |

La navigation principale (Mes demandes, Nouvelle demande, Dossiers à traiter)
n'affiche que les entrées du rôle connecté ; la marque « Conventions » ramène à
l'écran d'accueil du rôle. Il n'y a pas de fenêtre modale : le détail et la
décision sont deux écrans à part entière, atteints par les boutons des listes.

## Direction visuelle

L'interface reprend les codes d'un portail administratif contemporain : fond
papier ivoire (`#faf9f2`), surfaces blanches, texte presque noir, accent violet
(`#5148dc`) réservé aux liens et aux états actifs, boutons principaux noirs.

- **Polices locales** : Inter puis Lato, déjà présentes sur le poste ; aucune
  requête vers un service externe.
- **Largeur** : contenu centré, plafonné à 1600 px, marges latérales fluides
  (`clamp`) ; en-tête et pied de page sur toute la largeur.
- **Cartes et panneaux** : bords arrondis, ombre très discrète, aucune bordure
  décorative ; les formulaires de dépôt et de décision sont posés dans des
  panneaux blancs.
- **Compteurs** : trois cartes « Validées », « En cours de revue », « Rejetées »
  côté étudiante ; le nombre de dossiers en attente est rappelé dans l'en-tête
  du responsable.
- **Statuts** : pastille colorée + libellé en toutes lettres — `Brouillon`,
  `En attente`, `Validée`, `Refusée`. La couleur ne porte jamais l'information
  seule.
- **Mobile** : navigation repliée sous la marque, cartes de compteurs en
  colonne, tableau défilable, barre de décision empilée.

## Parcours des deux rôles

`parcours.svg` présente deux couloirs et les échanges entre eux :

- **Étudiante** : connexion → « Mes demandes » (compteurs, tableau, statut) →
  « Nouvelle convention » (entreprise, intitulé, dates, soumission) → « Détail »
  (statut, date de décision ou motif de refus) → retour d'erreur lisible en cas
  de saisie invalide.
- **Responsable** : connexion → « Dossiers à traiter » (recherche, filtres,
  cartes) → « Décision de convention » (résumé, motif, valider ou refuser) →
  retour à la file, décision visible dans le détail.

Les deux flèches horizontales matérialisent le seul échange métier : la
convention `SOUMISE` part vers le responsable, la décision revient vers
l'étudiante.

## Formulaire accessible

| Point | Mise en œuvre |
|---|---|
| Étiquettes liées | Chaque champ a un `<label for="…">` et un `id` unique (`email`, `mot-de-passe`, `entreprise`, `intitule`, `date-debut`, `date-fin`, `motif`). |
| Aide contextuelle | `aria-describedby` relie le champ à son texte d'aide et à sa zone d'erreur. |
| Zone d'erreur | Zone globale `role="alert"` + `aria-live="assertive"`, et une zone `id="erreur-…"` par champ. |
| Erreur de champ | Message texte sous le champ et `aria-invalid="true"` sur le champ concerné. |
| Messages de réussite | `role="status"` (annonce polie, sans interrompre la saisie). |
| Décision | Écran dédié, sans dialogue : en cas de refus sans motif, le message s'affiche sous la zone de texte et le focus y est placé. |
| Navigation clavier | Lien d'évitement « Aller au contenu principal », `:focus-visible` visible sur tous les contrôles. |
| Couleur | Le statut est écrit en toutes lettres ; la couleur ne fait que renforcer. |
| Structure | Un seul `h1` par écran, sections titrées `h2`, tableau avec `caption` et `th scope="col"`. |
| Langue | `lang="fr"`, dates affichées au format `JJ/MM/AAAA`. |

Les formulaires utilisent `novalidate` : la validation est faite côté serveur, et
les messages affichés sont ceux de l'API. Le navigateur ne bloque donc pas la
soumission avec ses propres bulles, ce qui permet de montrer les erreurs 422
réelles.

## Gestion lisible des erreurs

`assets/api.js` traduit le statut HTTP et le corps JSON en titre + liste de
détails. Le message du serveur est préféré quand il existe.

| Code | Déclencheur | Affichage |
|---|---|---|
| 400 | Corps JSON illisible | « Le corps de la requête doit être un objet JSON valide. » |
| 401 | Session absente ou expirée | « Authentification requise. » puis retour à l'écran de connexion ; à la connexion, « E-mail ou mot de passe incorrect. » |
| 403 | Rôle ou propriétaire incorrect | « Vous n'avez pas les droits pour cette action. » |
| 404 | Convention inconnue | « Cette ressource est introuvable. » |
| 405 | Méthode non autorisée | « Cette action n'est pas autorisée sur cette ressource. » |
| 409 | Décision déjà prise | « Cette décision n'est plus possible : la demande a déjà été traitée. » |
| 422 | Validation serveur | Message global + message sous chaque champ concerné (`details` de l'API) |
| 500 | Panne interne | « Une erreur interne est survenue. Réessayez dans un instant. » |
| 503 | Base indisponible | Badge « Service indisponible » et message dans la zone d'état |
| 0 | Serveur injoignable | « Le serveur ne répond pas. Vérifiez qu'il est démarré. » |

Preuve : `preuves/12_erreurs_400_401_500.png` (les trois blocs sont rendus par
le composant commun) et `preuves/03_erreurs_422.png` (un message par champ).

## Rendu sécurisé (`textContent`)

`assets/rendu.js` ne contient aucun `innerHTML`. Chaque valeur reçue de l'API est
insérée dans un nœud créé par `document.createElement`, puis affectée à
`textContent` :

```js
const td = document.createElement('td');
td.textContent = String(valeur);
```

Deux charges hostiles ont été utilisées :

```text
<img src=x onerror="document.body.dataset.xss='image'">
<script>document.body.dataset.xss="script"></script>
```

Résultat mesuré sur `/preuves/xss.html` :

```text
Attribut data-xss sur <body> : absent
Éléments <img> créés dans le document : 0
Éléments <script> dans le tableau rendu : 0
Résultat : les deux charges apparaissent en texte ; aucune balise n'est interprétée.
```

La même charge a été envoyée à l'API par le formulaire (convention 7) : elle est
affichée littéralement dans le tableau de l'étudiante, dans le détail puis dans
les cartes du responsable (`04_demande_creee.png`, `06_detail.png`,
`07_responsable.png`). Détail complet : `preuves/xss_verification.txt` et
`preuves/xss_dom.html`.

## Scénario de bout en bout

Rejoué dans Chrome 157, sur la base TP3 rechargée. Résumé :

| # | Action | Résultat observé |
|---|---|---|
| 1 | Ouvrir l'application | Écran de connexion, badge « Service actif » |
| 2 | Connexion `sena.houngbo@univ.test` | « Mes demandes », 2 conventions, compteurs 1 / 0 / 0 |
| 3 | Ouvrir « Nouvelle demande » puis soumettre le formulaire vide | 422 « Données invalides. », 4 champs signalés |
| 4 | Déposer une convention avec `<img …>` dans l'intitulé | « Convention n° 7 enregistrée au statut En attente. », balise en texte |
| 5 | Recharger (F5) | Session conservée, convention 7 toujours présente |
| 6 | Cliquer « Consulter » sur la convention 7 | Écran de détail, balise toujours en texte |
| 7 | Connexion `responsable.pedago@univ.test` | « Dossiers à traiter », 7 dossiers, 2 en attente, filtres et recherche |
| 8 | Cliquer « Décider » sur la convention 2 | Écran de décision, résumé et zone de motif |
| 9 | Cliquer « Refuser la demande » sans motif | Message sous le champ, focus placé sur le motif, aucun appel réseau |
| 10 | Saisir un motif puis refuser | « Convention n° 2 : refusée. », motif conservé |
| 11 | Cliquer « Décider » sur la convention 7 puis valider | « Convention n° 7 : validée. », 0 en attente |
| 12 | Ouvrir `/preuves/erreurs.html` | Blocs 400, 401 et 500 rendus |
| 13 | Ouvrir `/preuves/xss.html` | Verdict « Aucune exécution », 0 balise interprétée |

Détail étape par étape, avec les captures : `scenario.md`.

## Rejouer

```bash
cd ../TP4_Architecture
php -S 127.0.0.1:8084 -t public public/index.php
```

Ouvrir `http://127.0.0.1:8084/`. Comptes : `sena.houngbo@univ.test` et
`responsable.pedago@univ.test`, mot de passe `Demo1234!`.

Les pages de preuve sont accessibles à `/preuves/erreurs.html` et
`/preuves/xss.html` ; elles ne sont pas liées depuis l'application.

Pour repartir d'une base propre :

```bash
mysql -u root --socket=/tmp/mysql-tp3-oussou.sock < ../TP3_Modele_donnees/001_schema.sql
mysql -u root --socket=/tmp/mysql-tp3-oussou.sock < ../TP3_Modele_donnees/002_seed.sql
```

## Limites connues

- L'interface couvre `ETUDIANT` et `RESPONSABLE` ; l'`ADMIN` voit la file de
  traitement mais ne peut pas décider, `ENCADREUR` consulte ses demandes sans
  décision. `DEVELOPPEUR` n'a pas d'écran dédié.
- Le jeton CSRF est traité par contrôle d'origine et `SameSite=Lax`, pas par un
  jeton de session (voir `../TP8_Tests/README.md`, dette technique).
- Les erreurs 400 et 500 sont rendues par la page de preuve à partir des corps
  de l'API : l'interface ne peut pas les provoquer volontairement sans altérer
  le serveur ou le réseau.
