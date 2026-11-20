# Questions individuelles — préparation orale

**Projet informatique 2 · L3 SIL** — Plateforme de suivi des conventions  
Membres : OUSSOU Hermax, TCHEGNON Loïk, KANHONOU Ashley  
Encadreur : MAMA Tairou — 20/11/2026

Le contrôle oral est individuel. Chaque membre doit savoir expliquer **une règle
métier**, **une requête**, **un test** et **un commit** de sa contribution. Les réponses
ci-dessous tiennent en 30 à 45 secondes ; les relances servent à vérifier que le code est
compris, pas seulement récité.

## 0. Convention de lecture de l'historique Git

L'historique est centralisé : les commits sont signés par l'intégrateur du groupe, mais
chaque membre sait quels fichiers il a produits et dans quel commit ils ont été
intégrés. La question porte donc sur le **contenu** du commit, pas sur la signature.

| Commit | Auteur Git | Contenu utile |
|---|---|---|
| `41e14a9` | OUSSOU Hermax | Fiche de cadrage TP1 |
| `d7eaf5a` | OUSSOU Hermax | Exigences TP2 |
| `51b04fe` | OUSSOU Hermax | Modèle TP3 |
| `bd0ed02` | Loik940 | Correction du diagramme de cas d'utilisation TP3 |
| `ab5239c` | OUSSOU Hermax | Socle TP4 et API TP6 |
| `7d03f0c` | OUSSOU Hermax | Interface TP7 et dossier TP8 |
| `4179d8c` | OUSSOU Hermax | Rapports TP7/TP8, maquettes, résumé |

**À dire si le jury demande « votre commit »** : « Le commit `ab5239c` contient le module
que j'ai écrit ; voici le fichier et la fonction, je peux expliquer chaque ligne. » Ne
jamais revendiquer un commit que l'on ne sait pas expliquer.

---

## 1. OUSSOU Hermax — API, décisions et déploiement

### Q1. Règle métier : que se passe-t-il si un responsable refuse sans motif ?

**Réponse.** Le serveur refuse la décision avec `422 VALIDATION` et aucun statut n'est
écrit. La règle est portée par `DemandeService::changerStatut()` : pour `REFUSEE`, le
motif est obligatoire, de 3 à 255 caractères ; pour `VALIDEE`, le motif reste `NULL`.
La décision est ensuite faite dans une transaction : `UPDATE convention` puis
`INSERT historique`, avec rollback si l'une des deux écritures échoue.

**Fichier.** `src/Services/DemandeService.php`, lignes 182 à 231.

### Q2. Requête : montrez la mise à jour du statut.

**Réponse.**

```sql
UPDATE convention
   SET statut = :statut,
       motif_refus = :motif,
       date_decision = :date_decision
 WHERE id = :id
```

Elle est préparée dans `DemandeRepository::updateStatus()`. Les valeurs sont passées
séparément du texte SQL, donc une chaîne comme `1 OR 1=1` ne peut pas changer la requête.
`rowCount() === 1` vérifie qu'une ligne a réellement été modifiée.

**Fichier.** `src/Repositories/DemandeRepository.php`, lignes 134 à 153.

### Q3. Test : quel test prouve la règle du refus sans motif ?

**Réponse.** Le test **T-02** : `PATCH /demandes/2/statut` avec `REFUSEE` et sans motif.
Attendu : `422` et statut inchangé en base. Le script relit la ligne après l'appel ; le
statut est toujours `SOUMISE`. Le test est écrit avant exécution dans
`TP8_Tests/matrice_tests.md` et sa sortie est dans `preuves/sorties.tsv`.

### Q4. Commit : que contient `ab5239c` et que prouve-t-il ?

**Réponse.** `ab5239c` — « Commit du TP4 et TP6 » — contient le socle en couches, la
connexion PDO, les contrôleurs, `DemandeService`, `DemandeRepository`, le contrat d'API et
les preuves des six cas. Il prouve que l'API ne met pas de SQL dans les contrôleurs et que
les décisions passent par le service et la transaction.

**Relances.**

- *Pourquoi une transaction ?* Pour éviter un statut validé sans ligne d'historique.
- *Où est vérifié le rôle ?* Côté serveur, dans `AuthService::exigerRole()`, à chaque
  requête ; jamais dans un paramètre client.
- *Que renvoie une transition interdite ?* `409 TRANSITION_INTERDITE`, sans écriture.

---

## 2. TCHEGNON Loïk — modèle de données et interface

### Q1. Règle métier : combien de soutenances pour une convention ?

**Réponse.** Au plus une. La table `soutenance` porte une clé étrangère `convention_id`
unique, et l'encadreur de la soutenance doit être celui de la convention via une clé
étrangère composite `(convention_id, encadreur_id)`. La base empêche donc un doublon ou un
encadreur incohérent, même si l'application se trompe.

**Fichier.** `TP3_Modele_donnees/001_schema.sql`, table `soutenance`.

### Q2. Requête : comment obtient-on le planning lisible ?

**Réponse.** La vue `v_planning_soutenance` joint `soutenance`, `convention`, `salle`,
`etudiant` et `utilisateur` pour afficher la date, la salle, l'étudiant, l'encadreur et
l'intitulé. Elle est utilisée pour la démonstration de la programmation, car l'API
n'expose pas encore EF-05.

```sql
SELECT * FROM v_planning_soutenance ORDER BY date_heure;
```

**Fichier.** `TP3_Modele_donnees/001_schema.sql`, vue `v_planning_soutenance`.

### Q3. Test : comment vérifie-t-on le chevauchement ou le doublon ?

**Réponse.** `004_tests_contraintes.sql` tente des insertions invalides : une deuxième
soutenance pour la même convention, un encadreur différent de celui de la convention, un
chevauchement de salle ou d'encadreur. Chaque insertion doit échouer ; la vue
`v_soutenances_conflits` doit rester vide sur le jeu d'essai. Preuve :
`003_verification.sql` et la sortie des tests de contraintes.

### Q4. Commit : que contient `bd0ed02` et pourquoi est-il le vôtre ?

**Réponse.** `bd0ed02` — « Corrige le TP3 : diagramme de cas d'utilisation et rapport » —
corrige le vocabulaire et le diagramme de cas d'utilisation : 4 acteurs, 9 cas, lien avec
les exigences. Il prouve que le modèle présenté correspond aux tables et aux écrans, et
pas seulement à un schéma théorique.

**Relances.**

- *Pourquoi une clé composite ?* Pour que l'encadreur de la soutenance soit celui de la
  convention, sans contrôle applicatif supplémentaire.
- *Que se passe-t-il si la salle est pleine ?* La capacité est bornée par contrainte ; le
  créneau est refusé.
- *Pourquoi la vue conflits ?* Elle rend les chevauchements visibles avant la publication.

---

## 3. KANHONOU Ashley — tests, sécurité et recette

### Q1. Règle métier : comment un mot de passe est-il stocké et vérifié ?

**Réponse.** Jamais en clair. Le jeu d'essai contient des empreintes bcrypt de 60
caractères, produites par `password_hash()`. La connexion récupère l'empreinte par
`SELECT`, puis `password_verify()` compare. Si l'e-mail est inconnu, une empreinte factice
est utilisée pour que le temps de réponse reste comparable et ne révèle pas l'existence du
compte.

**Fichiers.** `src/Services/AuthService.php`, lignes 34 à 72 ;
`TP8_Tests/preuves/hachages.tsv`.

### Q2. Requête : quelle requête lit le compte, et pourquoi est-elle sûre ?

**Réponse.**

```sql
SELECT u.id, u.email, u.mot_de_passe_hash, u.role, u.nom, u.prenom, u.actif, …
FROM utilisateur u
WHERE u.email = :email
LIMIT 1
```

Requête préparée, paramètre lié : une chaîne `' OR '1'='1` reste une valeur d'e-mail et ne
devient pas du SQL. La validation `FILTER_VALIDATE_EMAIL` intervient avant l'appel.

**Fichier.** `src/Repositories/UtilisateurRepository.php`, lignes 15 à 45.

### Q3. Test : quels tests couvrent le hachage et le CSRF ?

**Réponse.** **T-13** vérifie que les 8 comptes ont une empreinte bcrypt de longueur 60 et
qu'aucun mot de passe n'est en clair : 8/8 conformes. **T-10** envoie une écriture avec
`Origin: http://evil.test` : réponse `403 ORIGINE_REFUSEE`, avant le routeur. Le contrôle
est dans `src/Support/Csrf.php`.

### Q4. Commit : quel commit porte le dossier de tests ?

**Réponse.** `4179d8c` — « feat: ajout TP7, TP8, maquettes et mise à jour des rapports » —
intègre `TP8_Tests/matrice_tests.md`, `revue_code.md`, `recette.md`, le script
`tests_securite.sh` et les preuves. Il prouve que les 14 tests et les 5 scénarios de recette
ont été exécutés, pas seulement décrits.

**Relances.**

- *Pourquoi `SameSite=Lax` ne suffit-il pas ?* Parce qu'il ne bloque pas toutes les
  écritures inter-sites ; on ajoute un contrôle explicite de `Origin`.
- *Quelle remarque de revue reste ouverte ?* R-04, limitation des tentatives : acceptée en
  local, à implémenter avant mise en ligne.
- *Pourquoi 14 tests et non 8 ?* Les 8 exigences du sujet sont couvertes, plus 6 contrôles
  de sécurité et de cohérence.

---

## 4. Questions transverses (tout le groupe)

| Question | Réponse courte |
|---|---|
| Pourquoi PHP sans framework ? | Déploiement immédiat, aucune dépendance, code lisible et testable ; ADR-001. |
| Pourquoi PDO plutôt que `mysqli` ? | Requêtes préparées natives, exceptions, compatibilité MySQL/MariaDB. |
| Où sont les règles métier ? | Dans `Services`, jamais dans les contrôleurs ni dans le HTML. |
| Comment est prouvée la restauration ? | Dump TP9 restauré sur base de test, 9/9 tables identiques après suppression d'`historique`. |
| Quelle est la limite principale ? | EF-05 (programmation de soutenance) n'est pas exposée par l'API ; elle est en version 2. |
| Pourquoi des données fictives ? | Consigne du sujet : aucune donnée personnelle réelle. |

## 5. Grille d'auto-évaluation

| Critère | 0 | 1 | 2 | Notre visée |
|---|---|---|---|---|
| Règle métier | fausse | partielle | exacte et située dans le code | 2 |
| Requête | non comprise | lue | préparée, paramètres et sécurité expliqués | 2 |
| Test | inconnu | cité | attendu, observé et preuve | 2 |
| Commit | introuvable | hash seul | hash, fichiers et contenu | 2 |

Chaque membre s'entraîne à répondre sans lire ses notes, puis à ouvrir le fichier cité et
à montrer la ligne exacte. Un code que l'on ne sait pas expliquer ne compte pas.
