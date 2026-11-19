# Design QA — frontend TP4

final result: passed

## Cible et preuves

- Maquette de décision : [`Maquette /Traiter la demande.png`](../Maquette%20%2FTraiter%20la%20demande.png), 1280 × 1023 px.
- Capture navigateur : [`design-qa/review-viewport.png`](design-qa/review-viewport.png), capture à 1280 × 1025 px CSS, 1280 × 1025 pixels (1×).
- Comparaison plein écran : [`design-qa/comparison-decision.png`](design-qa/comparison-decision.png). La maquette et l’application sont présentées côte à côte; la capture de l’application est recadrée de 2 px en hauteur pour aligner les cadres.
- Captures complémentaires : connexion, liste étudiante, détail, file du responsable et vues mobiles dans [`design-qa/`](design-qa/).

La comparaison du parcours de décision reprend la même hiérarchie visuelle : navigation, titre et statut, résumé en cartes, zone d’examen, motif de décision et barre d’actions. L’interface utilise le fond ivoire, les surfaces blanches, le texte sombre et les états vert, ambre et rouge de la maquette.

## Surfaces vérifiées

- **Typographie :** sans sérif de système, avec hiérarchie nette entre titres, libellés et métadonnées. La famille n’est pas exactement identifiée à celle de l’image source, mais poids, contraste et tailles restent proches et lisibles.
- **Mise en page :** les quatre cartes de résumé et les deux panneaux reprennent la composition de la maquette. La barre de décision reste visible avec un viewport de 1280 × 1025.
- **Couleurs :** papier ivoire, cartes blanches, boutons noirs et badges de statut colorés cohérents avec la référence.
- **Images et icônes :** aucune illustration n’est attendue. Les petites icônes de ligne présentes dans la maquette ne sont pas reprises; elles sont décoratives et leur absence ne gêne pas la lecture. Aucun substitut en dessin CSS ou glyphe n’a été ajouté.
- **Contenu :** les champs affichés correspondent aux données disponibles dans l’API. Les pièces jointes, signatures, tuteur et rémunération ne sont pas simulés; un message de portée l’indique sur l’écran de décision.
- **Accessibilité :** navigation sémantique, lien de saut, libellés associés, messages d’erreur accessibles, focus visible et statuts écrits en toutes lettres.
- **Responsive :** formulaires étudiant et liste responsable examinés à 390 px. Le document ne déborde pas horizontalement; les cartes s’empilent et les actions restent accessibles.

## Interactions observées

- Connexion avec les comptes pédagogiques étudiant et responsable.
- Consultation des demandes, ouverture d’un détail, navigation vers le formulaire étudiant et retour à la liste.
- Filtre responsable par nom : « Sènami » réduit les sept cartes à trois.
- Le filtre « En attente » affiche un état vide explicite quand aucun dossier ne correspond.
- Console navigateur : aucune erreur JavaScript pendant ces parcours; le `401` de `/api/moi` sans session est attendu.

Le jeu de données courant ne contient aucune demande au statut `SOUMISE` (0 en attente). La maquette d’écran de décision a donc été présentée visuellement avec des valeurs de démonstration, sans envoyer de décision ni modifier les données. Le rendu et les commandes de décision sont visibles, mais le succès réel de la validation ou du refus reste à confirmer lorsqu’un dossier soumis sera disponible.

## Historique des ajustements

1. **Débordement mobile** : une valeur de test XSS longue élargissait une carte responsable. Ajout de retours à la ligne et de contraintes de largeur; les vues mobiles tiennent désormais dans 390 px.
2. **Cadre desktop** : le pied de page dépassait légèrement la hauteur de la référence et la ligne de santé répétait le badge de connexion. Ajustement de la hauteur minimale des écrans et affichage de l’état de santé seulement en cas d’erreur. La capture finale montre le pied de page dans le viewport.

## Limites résiduelles

- **P3 — icônes décoratives :** la référence en utilise dans les cartes de résumé; elles sont absentes ici. Une bibliothèque d’icônes dédiée pourra les ajouter lors d’un prochain affinage.
- La décision réelle n’a pas été exécutée, faute de demande en attente dans le jeu local; voir la limite de vérification ci-dessus.

Aucun écart visuel P0, P1 ou P2 ne reste après les comparaisons plein écran desktop et mobile.
