# Fiche de revue de code — TP8

Projet informatique 2 · L3 SIL — application de gestion des stages  
Groupe : OUSSOU Hermax, TCHEGNON Loïk, KANHONOU Ashley — encadreur MAMA Tairou  
Revue du 19 novembre 2026 — périmètre : `TP4_Architecture/` (API et interface),
commit de travail local.

## 1. Méthode

La revue a porté sur les fichiers suivants : `public/index.php`,
`public/assets/{api,rendu,app}.js`, `config/routes.php`,
`src/Support/{Csrf,Session,Request,Response}.php`,
`src/Services/{AuthService,DemandeService}.php` et
`src/Repositories/DemandeRepository.php`.

Chaque remarque est classée selon l'échelle suivante :

| Niveau | Définition | Délai |
|---|---|---|
| **Bloquante** | Faille ou contournement de règle métier exploitable ; le livrable ne peut pas être rendu tel quel. | Corrigée avant remise. |
| **Majeure** | Risque réel mais non exploitable en l'état, ou défense en profondeur insuffisante. | Corrigée avant remise ou planifiée avec échéance. |
| **Mineure** | Défaut d'ergonomie, de lisibilité ou de robustesse sans impact sécurité. | Corrigée si le coût est faible. |
| **Suggestion** | Amélioration facultative. | Backlog. |

Une remarque est « corrigée » seulement si le correctif est présent dans le code
et couvert par un test de la matrice (`matrice_tests.md`).

## 2. Remarques

### R-01 — Identifiant de route converti silencieusement en entier

- **Fichier** : `config/routes.php`
- **Constat** : les routes utilisaient `(int) $parametres['id']`. En PHP,
  `(int) '12abc'` vaut `12` et `(int) '1 OR 1=1'` vaut `1`. Un identifiant
  malformé pouvait donc désigner une demande existante au lieu d'être rejeté.
- **Risque** : contournement de la validation d'entrée ; comportement
  surprenant, dépendant du transtypage implicite. La requête restait préparée,
  donc pas d'injection SQL, mais la ressource retournée n'était pas celle
  demandée.
- **Classification** : **bloquante** — corrigée.
- **Correctif** : une fonction `$identifiant` vérifie `is_string`,
  `ctype_digit` et `> 0`, sinon la route répond `404 DEMANDE_INCONNUE` **avant**
  tout appel au dépôt.

```php
$identifiant = static function (array $parametres): ?int {
    $id = $parametres['id'] ?? null;
    if (!is_string($id) || !ctype_digit($id) || (int) $id <= 0) {
        return null;
    }
    return (int) $id;
};
```

- **Vérification** : T-06 (`GET /api/demandes/1%20OR%201=1` → 404). Contrôle
  manuel complémentaire : `12abc` → 404.

### R-02 — Protection CSRF implicite seulement

- **Fichiers** : `src/Support/Session.php`, `public/index.php`
- **Constat** : la session utilise `SameSite=Lax`, ce qui bloque déjà les
  requêtes `POST` inter-sites, mais aucune vérification explicite de l'origine
  n'existait. Un navigateur ancien ou une politique de cookies assouplie
  pouvaient laisser passer une écriture forgée.
- **Risque** : validation ou refus d'une demande déclenché par un site tiers à
  l'insu du responsable connecté.
- **Classification** : **majeure** — corrigée.
- **Correctif** : classe `App\Support\Csrf`, appelée au début du front
  controller. Sur `POST`, `PATCH`, `PUT`, `DELETE`, si l'en-tête `Origin` est
  présent et ne correspond pas à `Host`, la réponse est
  `403 ORIGINE_REFUSEE`. L'API reste JSON-only, sans en-tête CORS.
- **Vérification** : T-10 (`Origin: http://evil.test` → 403).
- **Limite assumée** : pas de jeton de session par formulaire. Un jeton
  imposerait un aller-retour supplémentaire et modifierait le contrat du TP6 ;
  le choix est consigné en dette technique (§3).

### R-03 — Le message d'erreur du refus ne s'affichait jamais

- **Fichiers** : `public/index.html`, `public/assets/app.js` (écran de décision)
- **Constat** : le premier formulaire de refus utilisait un `<form method="dialog">`
  sans `novalidate`. Le `required` et le `minlength` du `<textarea>` déclenchaient
  la validation native du navigateur : la soumission était bloquée avant
  l'exécution du gestionnaire, donc le message maison « Le motif doit contenir de
  3 à 255 caractères. » restait invisible.
- **Risque** : aucun risque de sécurité, mais un critère du TP7 — « gestion
  lisible des erreurs » — n'était pas démontrable, et le message affiché
  dépendait du navigateur.
- **Classification** : **mineure** — corrigée.
- **Correctif** : la décision est devenue un écran dédié, sans dialogue. Le
  formulaire `#formulaire-decision` porte `novalidate` et le `<textarea>` n'a plus
  de `required` natif ; `decide()` vérifie la longueur du motif (3 à 255), affiche
  le message dans `#erreur-motif`, pose `aria-invalid="true"` et place le focus
  sur la zone de texte. Les boutons de décision sont dans la barre d'actions
  `.decision-bar`, sous le formulaire.
- **Vérification** : étapes 9 et 10 du scénario TP7
  (`preuves/09_refus_motif.png`, `10_refus_enregistre.png`).

### R-04 — Aucune limitation des tentatives de connexion

- **Fichier** : `src/Services/AuthService.php`
- **Constat** : `POST /api/connexion` accepte un nombre illimité d'essais. Le
  message est identique pour un compte inconnu et un mot de passe faux, et une
  empreinte factice est vérifiée dans les deux cas pour égaliser le temps de
  réponse : l'énumération de comptes est limitée, mais pas le bruteforce.
- **Risque** : devinette de mot de passe à grande vitesse sur un compte
  existant. Le mot de passe de démonstration `Demo1234!` est volontairement
  faible.
- **Classification** : **majeure** — acceptée avec plan (dette technique).
- **Justification de l'acceptation** : l'application est locale, sans accès
  réseau, avec des données fictives et un jeu de démonstration imposé. Un
  compteur d'échecs par compte et par adresse IP nécessite un stockage
  persistant (table ou cache) qui dépasse le périmètre du TP8.
- **Correctif prévu** : compteur `tentatives_connexion` (e-mail, IP, fenêtre
  glissante de 15 minutes, seuil 5) avec réponse `429` ; à défaut, délai
  progressif. Priorité haute avant toute mise en ligne réelle.

## 3. Dette technique consignée

| Point | Décision | Échéance |
|---|---|---|
| Jeton CSRF de session | Non retenu : `SameSite=Lax` + contrôle `Origin` + API JSON sans CORS. | À ajouter si un formulaire HTML classique est introduit. |
| Limitation des tentatives de connexion (R-04) | Acceptée en local. | Avant mise en ligne. |
| Cookie de session `secure=false` | Nécessaire en HTTP local ; `HttpOnly` et `SameSite=Lax` actifs. | Passer à `true` derrière HTTPS. |
| Comptes de démonstration au mot de passe commun | Jeu fictif du TP3. | Remplacer par des comptes nominatifs en production. |

## 4. Synthèse

| Réf. | Sujet | Niveau | État |
|---|---|---|---|
| R-01 | Identifiant de route non validé | Bloquante | Corrigée, testée (T-06) |
| R-02 | CSRF implicite | Majeure | Corrigée, testée (T-10) |
| R-03 | Message de refus jamais affiché | Mineure | Corrigée, testée (scénario TP7) |
| R-04 | Pas de limitation des tentatives | Majeure | Acceptée, planifiée |

Deux remarques corrigées sur quatre touchent directement la sécurité ; les deux
corrections sont couvertes par la matrice de tests. La revue n'a pas relevé de
concaténation SQL, de secret versionné ni de donnée réelle dans le dépôt.

## 5. Échange avec le groupe relecteur

Le sujet du TP8 demande d'échanger le dépôt avec un autre groupe, de relever
quatre remarques et de les classer. Les quatre remarques R-01 à R-04 ci-dessus
sont celles retenues après cet échange ; chacune porte une décision explicite
(corrigée, acceptée, planifiée) et, pour les remarques reportées, une entrée de
dette technique (§3).

Le cadre de l'échange est consigné ci-dessous, à compléter et à signer par le
groupe relecteur, comme l'annexe de la fiche de cadrage du TP1.

| Élément | Valeur |
|---|---|
| Groupe relecteur | à compléter |
| Dépôt / branche examiné | travail local `TP4_Architecture/`, non commité, 19/11/2026 |
| Périmètre relu | `public/index.php`, `public/assets/{api,rendu,app}.js`, `config/routes.php`, `src/Support/{Csrf,Session,Request,Response}.php`, `src/Services/{AuthService,DemandeService}.php`, `src/Repositories/DemandeRepository.php` |
| Remarques retenues | 4 (R-01 bloquante, R-02 majeure, R-03 mineure, R-04 majeure) |
| Remarque rejetée après discussion | aucune |

**Nom et signature du groupe relecteur :** ____________________

**Nom et signature du représentant du groupe :** ____________________

**Date de l'échange :** ____ / ____ / ________
