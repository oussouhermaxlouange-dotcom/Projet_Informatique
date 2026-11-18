# ADR-001 — Monolithe modulaire PHP sans framework

**Date :** 17/11/2026  
**Statut :** accepté  
**Décideurs :** OUSSOU Hermax, TCHEGNON Loïk, KANHONOU Ashley

## Contexte

Groupe de trois étudiants, 25 heures de projet, application locale en PHP 8 avec MySQL/MariaDB.
Le socle doit être compris et repris par chaque membre, sans temps de formation à un framework.

## Décision

Construire un monolithe modulaire PHP 8 sans framework, avec un point d'entrée unique
(`public/index.php`), un routeur minimal, quatre couches (`Controllers`, `Services`,
`Repositories`, `Support`) et PDO en requêtes préparées.

## Conséquences

- Positives : aucune dépendance à installer, déploiement local immédiat, lecture directe du code.
- Négatives : le routage, la validation et la gestion des erreurs sont écrits à la main et
  doivent être testés ; pas d'outillage fourni par un framework.
- Règle maintenue : le SQL reste dans `src/Repositories`, jamais dans les contrôleurs ;
  les secrets restent dans `.env`, exclu de Git.

## Alternatives écartées

- **Framework complet (Laravel, Symfony)** : trop de surface à apprendre pour 25 heures.
- **Micro-framework (Slim)** : dépendance Composer et configuration supplémentaire pour un
  besoin de trois routes.
