# Contrat d'API — TP6

Application Web de gestion des stages et des soutenances  
Base locale : `http://127.0.0.1:8000`  
Format : JSON UTF-8 (`Content-Type: application/json; charset=utf-8`)

## 1. Modèle et vocabulaire

Une **demande de stage** est stockée dans la table `convention` du modèle TP3
(`TP3_Modele_donnees/001_schema.sql`), avec le journal `historique` :

| Vocabulaire API | Table / colonne |
|---|---|
| Demande | `convention` |
| Identifiant | `convention.id` |
| Statut | `convention.statut` : `BROUILLON`, `SOUMISE`, `VALIDEE`, `REFUSEE` |
| Motif de refus | `convention.motif_refus` |
| Historique | `historique` (une ligne par changement de statut) |

Le nom de route reste `demandes` (langage métier) ; le dépôt s'appelle
`DemandeRepository`. Aucune requête SQL n'est écrite dans les contrôleurs.

## 2. Authentification

L'API utilise une session PHP côté serveur :

- Cookie `SESSID_TP6`, `HttpOnly`, `SameSite=Lax`, sans expiration (session navigateur).
- `session.use_strict_mode` : un identifiant inconnu est refusé.
- `session_regenerate_id(true)` à la connexion : l'identifiant change, ce qui empêche
  la fixation de session.
- Les mots de passe sont stockés en bcrypt ; la vérification utilise `password_verify()`.
- Comptes de démonstration : mot de passe commun `Demo1234!`
  (`sena.houngbo@univ.test`, `responsable.pedago@univ.test`, etc.).

Les routes protégées répondent `401 NON_AUTHENTIFIE` sans session valide.

**Protection CSRF.** Trois barrières : cookie `SameSite=Lax`, API JSON sans en-tête CORS,
et contrôle explicite de `Origin` sur `POST`, `PATCH`, `PUT` et `DELETE`
(`src/Support/Csrf.php`). Si `Origin` est présent et ne correspond pas à `Host`, la
réponse est `403 ORIGINE_REFUSEE` avant le routeur. Un client sans navigateur (`curl`,
script de test) n'envoie pas `Origin` : il reste soumis à l'authentification par session.

## 3. Enveloppe d'erreur

```json
{
  "erreur": {
    "code": "VALIDATION",
    "message": "Données invalides.",
    "details": { "entreprise_id": "Entreprise inconnue." }
  }
}
```

`details` est facultatif ; il n'est présent que pour les erreurs de validation
ou de transition.

## 4. Routes

### 4.1 `GET /api/sante`

Vérifie que l'application répond et que la base est joignable (`SELECT 1`).

- Authentification : aucune.
- Succès `200` :

```json
{ "statut": "ok", "base": "ok", "horodatage": "2026-11-18T13:25:04+00:00" }
```

- Base injoignable : `503` avec `"statut": "indisponible"`, `"base": "erreur"`.

### 4.2 `POST /api/connexion`

Ouvre une session.

```json
{ "email": "sena.houngbo@univ.test", "mot_de_passe": "Demo1234!" }
```

- Succès `200` :

```json
{
  "utilisateur": {
    "id": 1,
    "email": "sena.houngbo@univ.test",
    "role": "ETUDIANT",
    "nom": "HOUNGBO",
    "prenom": "Sènami",
    "etudiant_id": 1,
    "encadreur_id": null
  }
}
```

- `400` corps JSON illisible ; `401 IDENTIFIANTS_INVALIDES` ; `403 COMPTE_INACTIF` ;
  `422 VALIDATION` si l'e-mail ou le mot de passe est absent/mal formé.

### 4.3 `POST /api/deconnexion`

Détruit la session. Succès `200` : `{ "statut": "deconnecte" }`.

### 4.4 `GET /api/moi`

Retourne l'utilisateur de la session courante. `200` avec la même enveloppe que la
connexion, ou `401 NON_AUTHENTIFIE`.

### 4.5 `GET /api/demandes`

Liste les demandes visibles par le rôle connecté :

| Rôle | Portée |
|---|---|
| `ETUDIANT` | Ses propres demandes (`findByStudent`). |
| `ENCADREUR` | Les demandes qu'il encadre. |
| `RESPONSABLE`, `ADMIN` | Toutes les demandes. |

Succès `200` :

```json
{ "demandes": [ { "id": 2, "statut": "SOUMISE", "entreprise": "Données et Territoires", "...": "..." } ] }
```

Erreurs : `401 NON_AUTHENTIFIE`, `403 ROLE_NON_AUTORISE`, `403 PROFIL_MANQUANT`.

### 4.6 `GET /api/demandes/{id}`

Détail d'une demande.

- `200` : `{ "demande": { ... } }`
- `404 DEMANDE_INCONNUE` ; `403 ACCES_REFUSE` si un étudiant demande la fiche d'un autre.
- L'identifiant doit être un entier positif écrit en chiffres (`ctype_digit`). `12abc`
  ou `1 OR 1=1` répondent `404` **avant** tout appel au dépôt : aucune requête SQL n'est
  construite avec la valeur reçue.

### 4.7 `POST /api/demandes`

Crée une demande pour l'étudiant connecté, éventuellement soumise immédiatement.

```json
{
  "entreprise_id": 1,
  "encadreur_id": null,
  "intitule": "Suivi des tournées de collecte",
  "date_debut": "2027-02-01",
  "date_fin": "2027-05-31",
  "soumettre": true
}
```

| Champ | Type | Obligatoire | Règle |
|---|---|---|---|
| `entreprise_id` | entier > 0 | oui | L'entreprise doit exister. |
| `encadreur_id` | entier > 0 ou `null` | non | L'encadreur doit exister s'il est fourni. |
| `intitule` | chaîne | oui | 5 à 120 caractères. |
| `date_debut` | `AAAA-MM-JJ` | oui | Date valide. |
| `date_fin` | `AAAA-MM-JJ` | oui | Postérieure à `date_debut`. |
| `soumettre` | booléen | non (`false`) | `true` : statut `SOUMISE` + `date_depot` + historique. |

- Succès `201` : `{ "demande": { "id": 7, "statut": "SOUMISE", "...": "..." } }`
- Erreurs : `400` JSON illisible ; `401` sans session ; `403 ROLE_NON_AUTORISE` si le rôle
  n'est pas `ETUDIANT` ; `403 PROFIL_MANQUANT` sans fiche étudiant ; `422 VALIDATION`
  (détails par champ) ; `503 BASE_INDISPONIBLE`.
- Aucune écriture si une validation échoue.

### 4.8 `PATCH /api/demandes/{id}/statut`

Décision du responsable pédagogique.

```json
{ "statut": "VALIDEE" }
```

```json
{ "statut": "REFUSEE", "motif": "Dossier incomplet : convention non signée." }
```

| Champ | Type | Obligatoire | Règle |
|---|---|---|---|
| `statut` | chaîne | oui | `VALIDEE` ou `REFUSEE` uniquement. |
| `motif` | chaîne | si `REFUSEE` | 3 à 255 caractères ; ignoré pour une validation. |

- Succès `200` : `{ "demande": { "id": 7, "statut": "VALIDEE", "date_decision": "..." } }`
- Effet : `UPDATE convention` puis `INSERT historique` dans **la même transaction** ;
  rollback complet si l'une des deux écritures échoue.
- Erreurs : `400` JSON illisible ; `401` sans session ; `403 ROLE_NON_AUTORISE` (seul
  `RESPONSABLE`) ; `404 DEMANDE_INCONNUE` ; `409 TRANSITION_INTERDITE` ; `422 VALIDATION`
  (statut inconnu, motif absent) ; `503 BASE_INDISPONIBLE`.

## 5. Table des transitions

| Statut actuel | Transitions autorisées |
|---|---|
| `BROUILLON` | `SOUMISE` |
| `SOUMISE` | `VALIDEE`, `REFUSEE` |
| `VALIDEE` | aucune (terminal) |
| `REFUSEE` | aucune (terminal) |

Toute autre demande répond `409 TRANSITION_INTERDITE` avec les transitions possibles
dans `details`, sans modifier la base.

## 6. Codes d'erreur

| Code d'erreur | HTTP | Cause |
|---|---:|---|
| `JSON_INVALIDE` | 400 | Corps absent ou non conforme à un objet JSON. |
| `NON_AUTHENTIFIE` | 401 | Session absente ou expirée. |
| `IDENTIFIANTS_INVALIDES` | 401 | E-mail inconnu ou mot de passe faux. |
| `ROLE_NON_AUTORISE` | 403 | Rôle insuffisant pour l'action. |
| `PROFIL_MANQUANT` | 403 | Compte sans fiche étudiant/encadreur. |
| `COMPTE_INACTIF` | 403 | Compte désactivé. |
| `ACCES_REFUSE` | 403 | Ressource appartenant à un autre utilisateur. |
| `ORIGINE_REFUSEE` | 403 | Écriture reçue avec un en-tête `Origin` étranger à l'application. |
| `ROUTE_INCONNUE` | 404 | Chemin inconnu. |
| `DEMANDE_INCONNUE` | 404 | Identifiant absent de `convention`. |
| `METHODE_NON_AUTORISEE` | 405 | Méthode HTTP non prévue pour ce chemin. |
| `TRANSITION_INTERDITE` | 409 | Transition absente de la table ci-dessus. |
| `VALIDATION` | 422 | Champ manquant, type incorrect ou valeur hors limites. |
| `ERREUR_INTERNE` | 500 | Erreur inattendue (détail journalisé seulement). |
| `BASE_INDISPONIBLE` | 503 | Connexion PDO impossible. |

## 7. Forme d'une demande

```json
{
  "id": 7,
  "etudiant_id": 1,
  "entreprise_id": 1,
  "encadreur_id": null,
  "intitule": "Suivi des tournées de collecte",
  "statut": "VALIDEE",
  "motif_refus": null,
  "date_depot": "2026-11-18 13:25:04",
  "date_decision": "2026-11-18 13:25:10",
  "date_debut": "2027-02-01",
  "date_fin": "2027-05-31",
  "etudiant_utilisateur_id": 1,
  "etudiant": "Sènami HOUNGBO",
  "entreprise": "Studio Kora"
}
```

Les dates sont exprimées en UTC (le front controller fixe `date_default_timezone_set('UTC')`).

## 8. Interface Web

L'application sert aussi l'interface dans `public/` (même origine que l'API) :

- `GET /` renvoie `public/index.html` ;
- `GET /assets/...`, `/preuves/...` renvoient les fichiers réels (CSS, JS, SVG, HTML) ;
- tout le reste passe par le front controller et le routeur JSON.

Avec le serveur intégré de PHP, `public/index.php` renvoie `false` pour un fichier
existant, ce qui laisse le serveur le servir directement. Avec Apache, `.htaccess`
laisse également passer les fichiers existants (`!-f`).

L'interface appelle les routes ci-dessus avec `fetch` (`credentials: 'same-origin'`) et
construit les tableaux avec `textContent`. Détail du parcours et des preuves :
`../TP7_Frontend/README.md`.

## 9. Preuves

- Six cas demandés (succès, 400, 401, 403, 404, 409) : `preuves/sortie_api.txt`.
- Détail de chaque cas : `docs/tp6_cas_tests.md`.
- Tests unitaires : `preuves/sortie_test_domain.txt`, `sortie_test_routes.txt`.
- Connexion PDO : `preuves/sortie_test_connexion.txt`.
- Base injoignable (503) : `preuves/sortie_test_sante_503.txt`.
- Interface et scénario TP7 : `../TP7_Frontend/preuves/`.
- Matrice et audit TP8 : `../TP8_Tests/preuves/sorties.tsv`.
