# TP6 — API des demandes de stage

Livrable du TP6 : preuves d'exécution, script rejouable et rapport (HTML, PDF,
DOCX) de l'API des demandes. Le code de l'API n'est pas dupliqué ici : il reste
dans `../TP4_Architecture/` (couches contrôleur, service, dépôt).

Groupe : OUSSOU Hermax, TCHEGNON Loïk, KANHONOU Ashley — encadreur MAMA Tairou.

## Contenu

| Fichier | Rôle |
|---|---|
| `tests_api.sh` | Recharge la base TP3, démarre l'API sur le port 8082 et rejoue les 14 cas. Écrit les preuves. |
| `preuves/sorties.tsv` | Un cas par ligne : numéro, libellé, attendu, requête, code obtenu, conformité, corps JSON complet. |
| `preuves/etat_base.tsv` | État des 7 demandes (`convention`) et nombre de lignes d'`historique` après les cas. |
| `preuves/capture_api.png` | Capture réelle de `GET /api/sante` dans un navigateur. |
| `build_rapport.py` | Génère le rapport depuis les TSV : HTML puis PDF (Chrome) et DOCX. |
| `build_docx.py` | Construit le DOCX avec l'API UNO de LibreOffice (même mise en page que le rapport TP3). |
| `api_demandes.html` | Rapport source, noir et blanc, A4. |
| `api_demandes.pdf` | Rapport 2 pages (impression / dépôt). |
| `api_demandes.docx` | Rapport éditable 2 pages. |

## Prérequis

| Logiciel | Version | Vérification |
|---|---|---|
| PHP | 8.1+ avec `pdo` et `pdo_mysql` | `php -m \| grep pdo_mysql` |
| MySQL / MariaDB | MySQL 8 | `mysql --version` |
| curl | 7.x | `curl --version` |
| Python | 3.10+ | `python3 --version` |
| Chrome / Chromium | — | pour le PDF (`google-chrome`) |
| LibreOffice | 7.x | pour le DOCX (`soffice`) |

L'application doit avoir un fichier `TP4_Architecture/.env` valide : le script
lit `DB_SOCKET`, `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` et `DB_PASSWORD`
dans ce fichier (ou utilise les valeurs par défaut de `.env.example`).

## Rejouer les tests

```bash
cd TP6_API
./tests_api.sh
```

Le script :

1. recharge `tp3_conventions` depuis `../TP3_Modele_donnees/001_schema.sql`
   puis `002_seed.sql` (base repart d'un état connu) ;
2. démarre `php -S 127.0.0.1:8082` sur `TP4_Architecture/public` ;
3. exécute S1 à S14 et compare chaque code HTTP à l'attendu ;
4. écrit `preuves/sorties.tsv` et `preuves/etat_base.tsv`, puis la capture
   `preuves/capture_api.png` ;
5. affiche `conformes : 14 / 14` et renvoie un code de sortie non nul en cas
   d'écart.

Après une exécution, la demande créée porte l'id 7 (dernier insert du jeu
d'essai) : S5 la valide, S10 cible la demande 4 déjà `VALIDEE`, S11 refuse la
demande 2. Ces numéros sont donc stables tant que le script recharge la base.

## Les six cas exigés

| Cas | Attendu | Vérifie |
|---|---|---|
| S5 | 200 | Validation d'une demande `SOUMISE` par le responsable |
| S6 | 400 | Corps JSON illisible (`JSON_INVALIDE`) |
| S7 | 401 | Requête sans session (`NON_AUTHENTIFIE`) |
| S8 | 403 | Étudiante qui tente de valider (`ROLE_NON_AUTORISE`) |
| S9 | 404 | Demande inexistante (`DEMANDE_INCONNUE`) |
| S10 | 409 | Transition interdite depuis `VALIDEE` (`TRANSITION_INTERDITE`) |

S1 à S4 préparent les sessions et la demande ; S11 à S14 couvrent le refus
motivé, les deux listes par rôle et l'entreprise inconnue (`422 VALIDATION`).

## Régénérer le rapport

```bash
cd TP6_API
python3 build_rapport.py
```

- `api_demandes.html` : construit depuis `preuves/sorties.tsv` et
  `preuves/etat_base.tsv` (aucune valeur recopiée à la main) ;
- `api_demandes.pdf` : Chrome headless, A4, 2 pages ;
- `api_demandes.docx` : `build_docx.py` via UNO. Le script démarre LibreOffice
  sur le port 2002 s'il n'écoute pas déjà, puis le referme.

Si Chrome est absent, le PDF n'est pas régénéré ; si LibreOffice est absent, le
DOCX n'est pas régénéré. Les deux cas affichent un message, sans interrompre le
reste.

## Résultat conservé

14 cas exécutés, 14 conformes, sur MySQL 8.0.46 et l'API réelle. Base après les
cas : 7 demandes (1 `BROUILLON`, 2 `REFUSEE`, 4 `VALIDEE`) et 12 lignes
d'`historique`. Détail complet dans `preuves/sorties.tsv`.
