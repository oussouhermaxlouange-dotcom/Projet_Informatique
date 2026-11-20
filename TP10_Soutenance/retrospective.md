# Rétrospective du projet

**Projet informatique 2 · L3 SIL** — Plateforme de suivi des conventions  
Membres : OUSSOU Hermax, TCHEGNON Loïk, KANHONOU Ashley  
Encadreur : MAMA Tairou — 20/11/2026

La rétrospective répond aux trois questions du chapitre 10 : qu'est-ce qui a bien
fonctionné, qu'est-ce qui a été difficile, qu'allons-nous changer ? Elle s'appuie sur des
faits vérifiables, pas sur des impressions.

## 1. Ce qui a bien fonctionné

| Point positif | Preuve |
|---|---|
| Progression par jalons : chaque TP réutilise le précédent sans le réécrire | TP4 → TP6 → TP7 → TP8 → TP9, une seule application |
| Preuves avant affirmations : chaque résultat a une sortie conservée | 14/14 tests, 8/8 bcrypt, 9/9 tables restaurées |
| Séparation en couches tenue jusqu'au bout | aucun SQL dans les contrôleurs, services testables |
| Documentation homogène et courte | rapports 2 pages A4, noir et blanc, même modèle |
| Revue de code utile | R-01 et R-02 corrigées et couvertes par T-06 et T-10 |
| Déploiement réellement rejoué | clone Git, installation sur second poste, incident reproduit |

Le point le plus solide est la **chaîne de preuve** : une exigence renvoie à un
composant, un test et une sortie. Par exemple, la règle « refus motivé » est dans
`DemandeService`, testée par T-02, et la sortie montre `422` avec un statut inchangé.
Cette chaîne a évité les affirmations non vérifiées et a rendu la soutenance plus simple
à préparer.

Le deuxième point est la **restauration**. Beaucoup de projets se contentent d'un
`mysqldump`. Ici, la sauvegarde a été restaurée sur une base de test, une table a été
supprimée volontairement, puis le dump a été réimporté : **9/9 tables identiques**. C'est
ce test qui a révélé le risque du `DB_SOCKET` obsolète et produit le ticket INC-001.

## 2. Ce qui a été difficile

| Difficulté | Effet constaté | Ce que nous avons appris |
|---|---|---|
| Commits groupés en fin de jalon | l'historique ne montre pas qui a écrit quoi | commiter au fur et à mesure, par fonctionnalité |
| EF-05 hors périmètre de l'API | la démonstration de programmation est partielle | annoncer clairement le périmètre, montrer le modèle |
| Configuration par socket | `503` difficile à diagnostiquer | vérifier le socket avant de démarrer, lire le journal |
| Trois personnes, 25 heures | peu de temps pour les tests manuels | automatiser tôt, se répartir les preuves |
| Rapports binaires lourds | dépôt alourdi, différences illisibles | versionner les sources, pas les PDF générés |

La difficulté la plus coûteuse a été **l'historique Git**. Les commits existent
(`41e14a9` à `4179d8c`) et couvrent tous les jalons, mais ils sont signés par
l'intégrateur et regroupés. Pour le contrôle individuel, il a fallu retrouver les fichiers
de chacun et préparer une explication par module. La leçon est simple : un commit par
fonctionnalité et par auteur aurait rendu la traçabilité immédiate.

La deuxième difficulté est **le périmètre**. EF-05 (programmer une soutenance avec
contrôle des conflits) est décrite dans les exigences et portée par le modèle TP3, mais
l'API ne l'expose pas. Le choix a été de ne pas simuler une fonctionnalité inexistante :
la démonstration montre la vue `v_planning_soutenance` et annonce EF-05 en version 2.
C'est moins spectaculaire, mais c'est honnête et défendable.

## 3. Ce que nous allons changer pour la version 2

| Changement | Pourquoi | Comment le vérifier |
|---|---|---|
| Un commit par fonctionnalité et par membre | traçabilité et contrôle individuel | `git log --author`, un commit = un sujet |
| Branches courtes et revue croisée | éviter les gros merges | une branche par fonctionnalité, une revue avant merge |
| Intégration continue minimale | détecter les régressions | `php -l`, tests, `py_compile` à chaque push |
| EF-05 dans l'API | compléter le parcours métier | création de soutenance + refus `409` en cas de conflit |
| Migrations versionnées | faire évoluer le schéma sans casser | un script `005_migration_*.sql` rejouable |
| Limitation des tentatives de connexion | fermer R-04 | `429` après 5 essais en 15 minutes |
| Notifications et portail entreprise | périmètre explicitement exclu du MVP | version 2, après stabilisation |

La version 2 doit d'abord **finir le métier** : programmer une soutenance avec contrôle
de salle et d'encadreur, puis publier le planning. Ensuite seulement, les notifications et
le portail entreprise. La dette technique (R-04, migrations, CI) est prioritaire sur les
nouvelles fonctionnalités.

## 4. Bilan chiffré

| Indicateur | Valeur |
|---|---|
| Exigences fonctionnelles | 8 (4 couvertes par l'API) |
| Tests automatisés | 14/14 conformes |
| Scénarios de recette | 5/5 conformes |
| Mots de passe bcrypt | 8/8, aucun en clair |
| Tables restaurées | 9/9 après perte volontaire |
| Incident reproduit et corrigé | 1 (INC-001) |
| Rapports 2 pages | TP6, TP7, TP8, TP9, TP10 |

## 5. Un mot par membre

- **OUSSOU Hermax** : « Le plus utile a été de prouver chaque résultat. Le plus difficile
  a été de garder l'historique Git lisible ; en v2, je commite une fonctionnalité à la
  fois. »
- **TCHEGNON Loïk** : « Le modèle de données a tenu parce que les contraintes étaient dans
  la base, pas seulement dans le code. En v2, je documente chaque migration dès qu'elle
  est écrite. »
- **KANHONOU Ashley** : « Les tests ont trouvé des problèmes que la relecture seule aurait
  laissés passer. En v2, je branche la CI pour que ces tests tournent à chaque push. »

## 6. Décisions de la rétrospective

| Décision | Échéance | Responsable |
|---|---|---|
| Commiter par fonctionnalité et par membre | immédiat | tous |
| Écrire le script de migration avant toute évolution du schéma | version 2 | Hermax |
| Implémenter EF-05 avec contrôle de conflit | version 2 | Loïk |
| Ajouter la limitation des tentatives (R-04) | avant mise en ligne | Ashley |
| Brancher `php -l` et les tests en CI | version 2 | Hermax |

**Conclusion.** Le projet est livrable : le dossier est complet, les preuves sont
reproductibles et la démonstration tient en huit minutes. Les faiblesses sont connues et
nommées — historique Git groupé, EF-05 hors API, pas de migration évolutive — et chacune a
une action datée pour la version 2.
