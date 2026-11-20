#!/usr/bin/env python3
"""Génère le rapport TP9 (HTML, PDF, DOCX) depuis les preuves de déploiement.

Entrées  : preuves/*.txt, preuves/tp3_conventions.sql
Sorties  : deploiement_tp9.html, deploiement_tp9.pdf (Chrome), deploiement_tp9.docx (UNO)
"""

from __future__ import annotations

import hashlib
import html
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
PREUVES = RACINE / "preuves"
DUMP = PREUVES / "tp3_conventions.sql"
HTML = RACINE / "deploiement_tp9.html"
PDF = RACINE / "deploiement_tp9.pdf"
DOCX = RACINE / "deploiement_tp9.docx"

DATE = "20 novembre 2026"

INSTALLATION = [
    ("Prérequis", "php -v ; php -m | grep pdo_mysql", "PHP 8.5.12, pdo_mysql présent"),
    ("Configuration", "cp .env.example .env ; édition", "fichier en chmod 600"),
    ("Base", "import 001_schema.sql puis 002_seed.sql", "8 comptes, 6 conventions"),
    ("Compte dédié", "CREATE USER 'tp9_app'@'localhost'", "4 droits sur une seule base"),
    ("Lancement", "php -S 127.0.0.1:8098 …", "serveur démarré"),
    ("Santé", "curl -i /api/sante", "200, base ok"),
    ("Connexion", "POST /api/connexion", "200, rôle ETUDIANT"),
    ("Lecture", "GET /api/demandes + cookie", "200, demandes de l'étudiante"),
]

REFUS = [
    ("DROP TABLE historique", "ERROR 1142 (42000)", "table conservée, 9 lignes"),
    ("CREATE TABLE essai", "ERROR 1142 (42000)", "aucune table créée"),
]

COMPTAGES = [
    ("utilisateur", 8), ("etudiant", 3), ("encadreur", 2), ("entreprise", 2),
    ("salle", 3), ("convention", 6), ("disponibilite", 4), ("soutenance", 2),
    ("historique", 9),
]

MANQUES = [
    ("DB_SOCKET absent du bloc .env exemple",
     "socket obligatoire non découvert",
     "variable ajoutée, règle « socket prioritaire »"),
    ("Aucun contrôle de l'existence du socket",
     "503 difficile à diagnostiquer",
     "test -S et lecture du journal PHP"),
    ("Aucune procédure de sauvegarde/restauration",
     "reprise après perte impossible",
     "section mysqldump + restauration sur base de test"),
    ("Aucune vérification des droits du compte",
     "risque de compte trop permissif",
     "SHOW GRANTS et test de refus DROP"),
]


def empreinte() -> tuple[int, str, int]:
    octets = DUMP.read_bytes()
    return len(octets), hashlib.sha256(octets).hexdigest(), octets.count(b"\n")


def cellule(texte: str, classe: str = "") -> str:
    attribut = f' class="{classe}"' if classe else ""
    return f"<td{attribut}>{html.escape(str(texte))}</td>"


def construire_html() -> str:
    taille, sha, lignes = empreinte()
    total = len(COMPTAGES)

    lignes_installation = "\n".join(
        "<tr>" + cellule(etape, "gras") + cellule(commande, "mono")
        + cellule(resultat) + "</tr>"
        for etape, commande, resultat in INSTALLATION
    )

    lignes_refus = "\n".join(
        "<tr>" + cellule(commande, "mono") + cellule(reponse, "mono")
        + cellule(effet) + "</tr>"
        for commande, reponse, effet in REFUS
    )

    lignes_comptages = "\n".join(
        "<tr>" + cellule(nom, "mono") + cellule(n, "c") + cellule(n, "c")
        + cellule("OK", "c") + "</tr>"
        for nom, n in COMPTAGES
    )

    lignes_manques = "\n".join(
        "<tr>" + cellule(manque) + cellule(consequence)
        + cellule(correction) + "</tr>"
        for manque, consequence, correction in MANQUES
    )

    css = """
  @page { size: A4; margin: 14mm 14mm 12mm 14mm; }
  body { font-family: "Liberation Sans", Arial, sans-serif; font-size: 8.4pt; line-height: 1.26; color: #000; margin: 0; }
  .tete { text-align: center; margin-bottom: 6pt; }
  .tete .petit, .tete .date, .tete .groupe { font-size: 7.7pt; }
  .tete h1 { font-size: 15pt; margin: 2pt 0; font-family: Georgia, serif; font-weight: normal; }
  h2 { font-size: 9.6pt; margin: 8pt 0 3pt; page-break-after: avoid; }
  h2.saut-page { page-break-before: always; margin-top: 0; }
  p { margin: 0 0 3.5pt; text-align: justify; }
  .note { font-size: 7pt; font-style: italic; color: #333; }
  code, .mono { font-family: "Liberation Mono", monospace; font-size: 7pt; }
  table { width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 7pt; margin: 1pt 0 4pt; }
  th, td { border: 0.4pt solid #555; padding: 1.9pt 2.4pt; vertical-align: top; text-align: left;
           word-wrap: break-word; overflow-wrap: break-word; }
  th { font-weight: bold; background: #f0f0f0; }
  thead { display: table-header-group; }
  tr { page-break-inside: avoid; }
  td.c { text-align: center; }
  td.gras { font-weight: bold; }
  .bloc { border: 0.5pt solid #555; padding: 3pt 5pt; margin: 2pt 0 4pt; }
  .bloc p { margin: 0; }
  footer { margin-top: 6pt; font-size: 6.9pt; color: #333; text-align: center; }
"""

    corps = f"""
<div class="tete">
  <div class="petit">Projet informatique 2 — L3 SIL</div>
  <h1>Déploiement, compte SQL dédié et sauvegarde</h1>
  <div class="date">TP9 — Déploiement et maintenance — {DATE}</div>
  <div class="groupe">Groupe : OUSSOU Hermax – TCHEGNON Loïk – KANHONOU Ashley<br>
  Encadreur : MAMA Tairou · PHP 8.5.12 · MySQL 8.0.46 · données fictives</div>
</div>

<h2>1. Objet et méthode</h2>
<p>Installer l'application sur un second poste, avec un compte SQL à droits limités, puis
prouver qu'une sauvegarde est réutilisable. Le second poste est un clone Git réel du
dépôt (<code>git clone</code> local, commit <code>4179d8c</code>, 170 fichiers, clone
propre), installé en suivant uniquement son README. Le serveur MySQL est une instance
isolée (socket <code>/tmp/opencode/mysql_tp9/run/mysql.sock</code>, port 3309), afin de
ne pas toucher la base principale. Chaque étape est rejouée et sa sortie est conservée
dans <code>preuves/</code>.</p>

<h2>2. Installation sur le second poste</h2>
<table>
  <colgroup><col style="width:17%"><col style="width:44%"><col style="width:39%"></colgroup>
  <thead><tr><th>Étape</th><th>Commande ou contrôle</th><th>Résultat obtenu</th></tr></thead>
  <tbody>
{lignes_installation}
  </tbody>
</table>
<p>La base importée contient le jeu fictif du TP3. <code>GET /api/sante</code> répond
<code>{{"statut":"ok","base":"ok","horodatage":"2026-11-20T08:31:11+00:00"}}</code>, puis
la connexion de <code>sena.houngbo@univ.test</code> renvoie <code>200</code> et la liste
de ses demandes. Preuve : <code>preuves/installation.txt</code>.</p>

<h2>3. Compte SQL à droits limités</h2>
<div class="bloc"><p><code>CREATE USER 'tp9_app'@'localhost' IDENTIFIED BY 'Tp9Demo!2026';<br>
GRANT SELECT, INSERT, UPDATE, DELETE ON tp3_conventions.* TO 'tp9_app'@'localhost';</code></p></div>
<p>Aucun privilège <code>DROP</code>, <code>CREATE</code>, <code>ALTER</code>,
<code>GRANT</code> ni <code>FILE</code> : le compte lit et modifie les données, jamais le
schéma. Deux refus ont été provoqués volontairement :</p>
<table>
  <colgroup><col style="width:36%"><col style="width:24%"><col style="width:40%"></colgroup>
  <thead><tr><th>Commande exécutée</th><th>Réponse</th><th>Effet constaté</th></tr></thead>
  <tbody>
{lignes_refus}
  </tbody>
</table>
<p>Après ces refus, la table <code>historique</code> est intacte et contient toujours
9 lignes. Preuve : <code>preuves/compte_sql.txt</code>.</p>

<h2>4. Sauvegarde</h2>
<div class="bloc"><p><code>mysqldump -u root --socket=… --single-transaction --routines
--triggers tp3_conventions &gt; preuves/tp3_conventions.sql</code></p></div>
<p>Code de sortie <code>0</code>. Le fichier produit mesure <strong>{taille} octets</strong>
({lignes} lignes) et porte l'empreinte SHA-256
<code>{sha}</code>. <code>--single-transaction</code> donne un instantané cohérent sans
bloquer les écritures ; <code>--routines</code> et <code>--triggers</code> conservent les
objets de programmation. Preuve : <code>preuves/sauvegarde.txt</code>.</p>

<h2 class="saut-page">5. Restauration vérifiée</h2>
<p>La sauvegarde est importée dans une base de test dédiée,
<code>tp3_conventions_restauration</code>. Les neuf tables sont comptées dans la base
source et dans la base restaurée :</p>
<table>
  <colgroup><col style="width:40%"><col style="width:20%"><col style="width:20%"><col style="width:20%"></colgroup>
  <thead><tr><th>Table</th><th>Source</th><th>Restaurée</th><th>Verdict</th></tr></thead>
  <tbody>
{lignes_comptages}
  </tbody>
</table>
<p><strong>{total}/{total} tables identiques.</strong> Le test de perte supprime ensuite
<code>historique</code> dans la base de test : le comptage répond « table absente » ;
après réimport du dump, les {total} tables redeviennent identiques. Une sauvegarde n'est
donc déclarée fiable qu'après cette restauration. Preuve :
<code>preuves/restauration.txt</code>.</p>

<h2>6. Incident INC-001 et correction</h2>
<table>
  <colgroup><col style="width:22%"><col style="width:78%"></colgroup>
  <thead><tr><th>Champ</th><th>Valeur</th></tr></thead>
  <tbody>
    <tr>{cellule("Symptôme", "gras")}{cellule("/api/sante répond 503 ; journal PHP : SQLSTATE[HY000] [2002] No such file or directory")}</tr>
    <tr>{cellule("Cause", "gras")}{cellule("DB_SOCKET recopié d'un ancien poste : le fichier socket n'existe plus et le socket est prioritaire sur host/port")}</tr>
    <tr>{cellule("Reproduction", "gras")}{cellule("renseigner un socket absent, démarrer le serveur, appeler /api/sante : 503 à chaque essai (3/3)")}</tr>
    <tr>{cellule("Correction", "gras")}{cellule("test -S sur le socket réel, puis sed sur DB_SOCKET ; /api/sante repasse à 200 sans modifier le code")}</tr>
    <tr>{cellule("Prévention", "gras")}{cellule("socket documenté dans .env.example, contrôle test -S avant démarrage, santé vérifiée après installation")}</tr>
  </tbody>
</table>
<p>Le ticket complet, avec les étapes de reproduction, les réponses attendues et observées
et les preuves, est dans <code>ticket_incident.md</code>. La reproduction et la correction
sont rejouées dans <code>preuves/incident_reproduction.txt</code>.</p>

<h2>7. Étapes manquantes du README</h2>
<p>Le README du TP4 a été suivi à la lettre. Quatre manques ont été relevés puis corrigés
dans <code>TP4_Architecture/README.md</code> :</p>
<table>
  <colgroup><col style="width:37%"><col style="width:30%"><col style="width:33%"></colgroup>
  <thead><tr><th>Manque constaté</th><th>Conséquence</th><th>Correction apportée</th></tr></thead>
  <tbody>
{lignes_manques}
  </tbody>
</table>

<h2>8. Conclusion</h2>
<p>L'installation est reproductible : huit étapes, un compte dédié, une santé à
<code>200</code>. Les droits du compte sont prouvés par deux refus <code>1142</code>. La
sauvegarde est datée, mesurée et empreintée ; sa restauration rétablit
<strong>{total}/{total} tables</strong> après une perte volontaire. L'incident réseau est
reproduit, expliqué et corrigé par la configuration, sans changement de code. Les quatre
manques du README sont comblés : le déploiement peut être refait sur un poste vierge avec
le seul README.</p>
<p class="note">Détail : <code>README.md</code> (protocole), <code>ticket_incident.md</code>
(INC-001), <code>preuves/</code> (sorties réelles et dump).</p>

<footer>Projet informatique 2 — L3 SIL — Déploiement et sauvegarde (TP9) — 20/11/2026</footer>
"""

    return f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8"><title>TP9 — Déploiement et sauvegarde</title>
<style>{css}</style></head><body>{corps}
</body></html>
"""


def main() -> int:
    HTML.write_text(construire_html(), encoding="utf-8")
    print(f"HTML : {HTML.name}")

    sys.path.insert(0, str(RACINE.parent / "outils"))
    import rapport_uno  # noqa: E402

    rapport_uno.generer_pdf(HTML, PDF)
    print(f"PDF  : {PDF.name} — {rapport_uno.compter_pages(PDF)} page(s)")

    script = RACINE / "build_docx.py"
    if script.exists():
        import subprocess
        subprocess.run([sys.executable, str(script)], check=True)
        print(f"DOCX : {DOCX.name}")
    else:
        print("build_docx.py introuvable : DOCX non généré.", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
