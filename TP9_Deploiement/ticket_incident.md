# Ticket d'incident INC-001

**Projet informatique 2 · L3 SIL** — Plateforme de suivi des conventions  
Ouvert le 20/11/2026 · Traité le 20/11/2026 · Statut : **résolu et vérifié**

| Champ | Valeur |
|---|---|
| Identifiant | INC-001 |
| Titre | `/api/sante` renvoie `503` après réinstallation : socket MySQL obsolète |
| Sévérité | Majeure (application inaccessible, aucune perte de données) |
| Environnement | Poste 2, PHP 8.5.12, MySQL 8.0.46, Linux |
| Composant | `config/database.php`, `src/Repositories/Database.php`, `.env` |
| Détecté par | Contrôle de santé après installation (`curl /api/sante`) |
| Reproductibilité | 100 % (3 essais sur 3) |

## 1. Résumé

Après l'installation sur le second poste, l'application démarre et la page de connexion
s'affiche, mais **toute requête à l'API** échoue. La route de santé répond
`503 Service Unavailable` avec `{"statut":"indisponible","base":"erreur"}`. Le journal
PHP indique `SQLSTATE[HY000] [2002] No such file or directory`. La cause est un
`DB_SOCKET` recopié d'un ancien poste : le fichier socket n'existe plus sur ce poste.

## 2. Configuration fautive

```ini
APP_ENV=local
APP_DEBUG=false
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=tp3_conventions
DB_USER=tp9_app
DB_PASSWORD=Tp9Demo!2026
DB_SOCKET=/tmp/mysql-tp3-oussou.sock
```

```text
$ ls -l /tmp/mysql-tp3-oussou.sock
ls: impossible d'accéder à '/tmp/mysql-tp3-oussou.sock' : Aucun fichier ou dossier de ce type
```

## 3. Étapes de reproduction

1. Partir d'une installation fonctionnelle (base importée, compte `tp9_app` créé).
2. Dans `.env`, renseigner un `DB_SOCKET` qui ne correspond à aucun socket réel, par
   exemple `/tmp/mysql-tp3-oussou.sock`.
3. Démarrer le serveur :

   ```bash
   php -S 127.0.0.1:8100 -t public public/index.php
   ```

4. Appeler la route de santé :

   ```bash
   curl -i http://127.0.0.1:8100/api/sante
   ```

5. Rejouer une seconde fois pour confirmer que l'échec est déterministe.

## 4. Résultat attendu / observé

| | Attendu | Observé |
|---|---|---|
| Code HTTP | `200` | `503` |
| Corps JSON | `{"statut":"ok","base":"ok",…}` | `{"statut":"indisponible","base":"erreur",…}` |
| Journal PHP | aucune erreur | `Connexion PDO impossible : SQLSTATE[HY000] [2002] No such file or directory` |
| Données | intactes | intactes (aucune écriture tentée) |

Réponse réelle :

```http
HTTP/1.1 503 Service Unavailable
Content-Type: application/json; charset=utf-8
Cache-Control: no-store
X-Content-Type-Options: nosniff

{"statut":"indisponible","base":"erreur","horodatage":"2026-11-20T08:32:01+00:00"}
```

## 5. Analyse de la cause

`config/database.php` lit `DB_SOCKET` et, s'il est non vide, l'utilise à la place de
`host`/`port` dans le DSN PDO. Un `DB_SOCKET` recopié d'un autre poste est donc
**prioritaire sur des valeurs `host`/`port` correctes**. Le fichier absent fait échouer
la connexion au niveau du système (`[2002]`), avant même l'authentification. Le message
client reste générique — comportement voulu — mais le journal serveur donne la cause
exacte.

Facteurs aggravants :

- le README ne demandait pas de vérifier l'existence du socket avant de le renseigner ;
- le bloc `.env` exemple du README ne mentionnait pas `DB_SOCKET` ;
- aucun contrôle de santé n'était prévu juste après l'installation.

## 6. Correction appliquée

```bash
test -S /tmp/opencode/mysql_tp9/run/mysql.sock && echo "socket présent"
sed -i 's#^DB_SOCKET=.*#DB_SOCKET=/tmp/opencode/mysql_tp9/run/mysql.sock#' .env
```

Vérification :

```http
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8

{"statut":"ok","base":"ok","horodatage":"2026-11-20T08:32:11+00:00"}
```

La correction ne touche ni le code applicatif ni le schéma : elle répare la
configuration du poste.

## 7. Prévention

| Action | Responsable | Échéance |
|---|---|---|
| Ajouter `DB_SOCKET` au bloc `.env` du README et la règle « socket prioritaire » | OUSSOU Hermax | fait le 20/11/2026 |
| Ajouter `test -S "$DB_SOCKET"` avant démarrage | TCHEGNON Loïk | fait le 20/11/2026 |
| Documenter la lecture du journal PHP en cas de `503` | KANHONOU Ashley | fait le 20/11/2026 |
| Contrôler `/api/sante` après chaque installation | tous | systématique |

## 8. Preuves jointes

- `preuves/incident_reproduction.txt` — configuration fautive, réponse `503`, journal
  PHP, puis correction et réponse `200` ;
- `preuves/installation.txt` — installation saine de référence ;
- `preuves/compte_sql.txt` — compte applicatif utilisé lors de l'incident.
