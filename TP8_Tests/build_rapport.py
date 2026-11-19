#!/usr/bin/env python3
"""Génère le rapport TP8 (HTML, PDF, DOCX) depuis les preuves d'exécution.

Entrées  : preuves/sorties.tsv, preuves/hachages.tsv, preuves/resume.txt
Sorties  : tests_securite.html, tests_securite.pdf (Chrome), tests_securite.docx (UNO)
"""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
PREUVES = RACINE / "preuves"
SORTIES = PREUVES / "sorties.tsv"
HACHAGES = PREUVES / "hachages.tsv"
RESUME = PREUVES / "resume.txt"
HTML = RACINE / "tests_securite.html"
PDF = RACINE / "tests_securite.pdf"
DOCX = RACINE / "tests_securite.docx"

DATE = "18 novembre 2026"

DONNEES = {
    "T-01": "PATCH /demandes/999/statut, session responsable",
    "T-02": "PATCH /demandes/2/statut, statut REFUSEE, sans motif",
    "T-03": "PATCH /demandes/3/statut sur une demande VALIDEE",
    "T-04": "POST /demandes, date_debut = 2027-02-30",
    "T-05": "Session B, GET /demandes/1 (dossier de A)",
    "T-06": "GET /demandes/1%20OR%201=1, session responsable",
    "T-07": "GET /demandes sans cookie de session",
    "T-08": "Session A, PATCH /demandes/2/statut, VALIDEE",
    "T-09": "POST /connexion, email = ' OR '1'='1",
    "T-09b": "POST /connexion, mot de passe = ' OR '1'='1",
    "T-10": "POST /connexion avec Origin: http://evil.test",
    "T-11": "POST /demandes, intitule = <script>alert(1)</script>",
    "T-12": "POST /demandes, intitule = espaces",
    "T-13": "SELECT mot_de_passe_hash FROM utilisateur",
}

CAS_LIMITES = [
    ("Demande inexistante", "T-01", "404",
     "Aucun accès à une ressource absente, aucune création implicite."),
    ("Refus sans motif", "T-02", "422 + statut inchangé",
     "La règle « motif obligatoire » est portée par le serveur ; l'absence d'écriture est relue en base."),
    ("Validation répétée", "T-03", "409 + statut inchangé",
     "VALIDEE et REFUSEE sont terminales ; la table des transitions fait foi."),
    ("Date invalide", "T-04", "422",
     "Le 30 février est refusé par le serveur, pas seulement par le champ type=date."),
]

REVUE = [
    ("R-01", "Identifiant de route converti par (int) : « 12abc » devenait 12, « 1 OR 1=1 » devenait 1.",
     "Bloquante", "Corrigée : ctype_digit + > 0, sinon 404 avant le dépôt. Testée T-06."),
    ("R-02", "CSRF implicite : SameSite=Lax seul, sans contrôle explicite de l'origine.",
     "Majeure", "Corrigée : Csrf.php refuse toute écriture d'une autre origine (403 ORIGINE_REFUSEE). Testée T-10."),
    ("R-03", "Formulaire de refus sans novalidate : la validation native masquait le message maison.",
     "Mineure", "Corrigée : novalidate ; message affiché sous le champ. Testée au scénario TP7."),
    ("R-04", "Aucune limitation des tentatives de connexion (bruteforce possible).",
     "Majeure", "Acceptée et planifiée : compteur 5 essais / 15 min, réponse 429 avant mise en ligne."),
]

RECETTE = [
    ("S1 — Connexion et dépôt", "EF-01, EF-02, EF-06", "Conforme"),
    ("S2 — Erreurs lisibles", "EF-02, ENF-02", "Conforme"),
    ("S3 — Validation", "EF-03, ENF-01", "Conforme"),
    ("S4 — Refus motivé", "EF-03", "Conforme"),
    ("S5 — Autorisations et injection", "ENF-01, ENF-02", "Conforme"),
]


def lire_tsv(chemin: Path) -> list[dict[str, str]]:
    lignes = chemin.read_text(encoding="utf-8").splitlines()
    entetes = lignes[0].split("\t")
    return [dict(zip(entetes, ligne.split("\t"))) for ligne in lignes[1:] if ligne.strip()]


def extrait(reponse: str) -> str:
    try:
        donnees = json.loads(reponse)
    except json.JSONDecodeError:
        return reponse
    if "erreur" in donnees:
        erreur = donnees["erreur"]
        return json.dumps(
            {"erreur": {"code": erreur.get("code", ""), "message": erreur.get("message", "")}},
            ensure_ascii=False, separators=(", ", ": "),
        )
    return reponse


def cellule(texte: str, classe: str = "") -> str:
    attribut = f' class="{classe}"' if classe else ""
    return f"<td{attribut}>{html.escape(str(texte))}</td>"


def construire_html() -> str:
    cas = lire_tsv(SORTIES)
    hachages = lire_tsv(HACHAGES)
    resume = RESUME.read_text(encoding="utf-8").strip().splitlines() if RESUME.exists() else []

    total = len(cas)
    conformes = sum(1 for ligne in cas if ligne["conforme"] == "OUI")
    bcrypt = sum(1 for ligne in hachages if ligne["bcrypt"] == "OUI")

    lignes_matrice = "\n".join(
        "<tr>"
        + cellule(ligne["test"], "c")
        + cellule(ligne["exigence"], "c")
        + cellule(ligne["cas"])
        + cellule(DONNEES.get(ligne["test"], ligne["requete"]))
        + cellule(ligne["attendu"], "c")
        + cellule(ligne["obtenu"], "c")
        + cellule(ligne["conforme"], "c")
        + "</tr>"
        for ligne in cas
    )

    lignes_limites = "\n".join(
        "<tr>" + cellule(nom, "gras") + cellule(test, "c")
        + cellule(reponse, "c") + cellule(preuve) + "</tr>"
        for nom, test, reponse, preuve in CAS_LIMITES
    )

    lignes_revue = "\n".join(
        "<tr>" + cellule(ref, "c") + cellule(constat) + cellule(niveau, "c")
        + cellule(etat) + "</tr>"
        for ref, constat, niveau, etat in REVUE
    )

    lignes_recette = "\n".join(
        "<tr>" + cellule(nom) + cellule(exigences, "c") + cellule(verdict, "c") + "</tr>"
        for nom, exigences, verdict in RECETTE
    )

    lignes_hachages = "\n".join(
        "<tr>" + cellule(ligne["email"], "mono") + cellule(ligne["role"], "c")
        + cellule(ligne["empreinte"] + "…", "mono") + cellule(ligne["longueur"], "c")
        + cellule(ligne["bcrypt"], "c") + "</tr>"
        for ligne in hachages
    )

    css = """
  @page { size: A4; margin: 14mm 14mm 12mm 14mm; }
  body { font-family: "Liberation Sans", Arial, sans-serif; font-size: 8.3pt; line-height: 1.24; color: #000; margin: 0; }
  .tete { text-align: center; margin-bottom: 5pt; }
  .tete .petit, .tete .date, .tete .groupe { font-size: 7.6pt; }
  .tete h1 { font-size: 14.5pt; margin: 2pt 0; font-family: Georgia, serif; font-weight: normal; }
  h2 { font-size: 9.4pt; margin: 7pt 0 2.5pt; page-break-after: avoid; }
  h2.saut-page { page-break-before: always; margin-top: 0; }
  p { margin: 0 0 3pt; text-align: justify; }
  .note { font-size: 6.9pt; font-style: italic; color: #333; }
  code, .mono { font-family: "Liberation Mono", monospace; font-size: 6.9pt; }
  table { width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 6.9pt; margin: 1pt 0 3pt; }
  th, td { border: 0.4pt solid #555; padding: 1.6pt 2.2pt; vertical-align: top; text-align: left;
           word-wrap: break-word; overflow-wrap: break-word; }
  th { font-weight: bold; background: #f0f0f0; }
  thead { display: table-header-group; }
  tr { page-break-inside: avoid; }
  td.c { text-align: center; }
  td.gras { font-weight: bold; }
  footer { margin-top: 5pt; font-size: 6.8pt; color: #333; text-align: center; }
"""

    corps = f"""
<div class="tete">
  <div class="petit">Projet informatique 2 — L3 SIL</div>
  <h1>Plan de tests et audit de sécurité</h1>
  <div class="date">TP8 — Tests et sécurité — {DATE}</div>
  <div class="groupe">Groupe : OUSSOU Hermax – TCHEGNON Loïk – KANHONOU Ashley<br>
  Encadreur : MAMA Tairou · MySQL 8.0.46 · API réelle · données fictives</div>
</div>

<h2>1. Objet et méthode</h2>
<p>Vérifier l'application par une matrice de tests et des contrôles de sécurité. Les {total}
cas ont été écrits <strong>avant</strong> exécution : l'attendu et le code HTTP attendu sont des
paramètres du script <code>tests_securite.sh</code>, qui recharge la base TP3, démarre l'API
sur le port 8086 et compare le code obtenu à l'attendu. Deux cas relisent en plus le statut en
base (refus sans motif, validation répétée) et un cas compare le nombre de lignes avant et
après une création invalide. Résultat : <strong>{conformes} / {total} conformes</strong>.</p>

<h2>2. Matrice de tests ({total} lignes)</h2>
<table>
  <colgroup><col style="width:6%"><col style="width:7%"><col style="width:29%"><col style="width:29%"><col style="width:12%"><col style="width:8%"><col style="width:9%"></colgroup>
  <thead><tr><th>Test</th><th>Exig.</th><th>Cas</th><th>Données</th><th>Attendu</th><th>Observé</th><th>Conforme</th></tr></thead>
  <tbody>
{lignes_matrice}
  </tbody>
</table>
<p class="note">Matrice détaillée, avec la réponse JSON complète de chaque cas :
<code>matrice_tests.md</code> et <code>preuves/sorties.tsv</code>.</p>

<h2>3. Les quatre cas limites exigés</h2>
<table>
  <colgroup><col style="width:18%"><col style="width:6%"><col style="width:17%"><col style="width:59%"></colgroup>
  <thead><tr><th>Cas limite</th><th>Test</th><th>Réponse</th><th>Ce que le test prouve</th></tr></thead>
  <tbody>
{lignes_limites}
  </tbody>
</table>

<h2>4. Autorisation et injection</h2>
<p><strong>Étudiante B vers le dossier de A (T-05)</strong> : la session de B est valide et la
demande 1 existe ; la réponse est pourtant <code>403 ACCES_REFUSE</code>, sans corps utile. Le
contrôle est fait dans <code>DemandeService</code> sur <code>etudiant_utilisateur_id</code>.
<strong>Étudiante A qui tente de décider (T-08)</strong> : <code>403 ROLE_NON_AUTORISE</code> ;
le rôle est vérifié côté serveur à chaque requête, jamais à partir d'un paramètre client.</p>
<p><strong>Chaîne « 1 OR 1=1 » (T-06, T-09, T-09b)</strong> : comme identifiant de route, elle
est rejetée par <code>ctype_digit()</code> avant tout appel au dépôt (<code>404</code>) ; dans le
champ e-mail, par <code>FILTER_VALIDATE_EMAIL</code> (<code>422</code>) ; dans le mot de passe,
par l'échec de <code>password_verify()</code> (<code>401</code>). Aucun de ces chemins ne
construit de SQL par concaténation : requêtes préparées avec
<code>PDO::ATTR_EMULATE_PREPARES = false</code>.</p>

<h2 class="saut-page">5. Mots de passe et protection CSRF</h2>
<p>Les {len(hachages)} comptes du jeu d'essai portent une empreinte bcrypt de 60 caractères
({bcrypt}/{len(hachages)} conformes, 0 mot de passe en clair). La vérification utilise
<code>password_verify()</code> et une empreinte factice égalise le temps de réponse entre
compte inconnu et mot de passe faux.</p>
<table>
  <colgroup><col style="width:34%"><col style="width:16%"><col style="width:28%"><col style="width:9%"><col style="width:13%"></colgroup>
  <thead><tr><th>Compte</th><th>Rôle</th><th>Empreinte</th><th>Long.</th><th>bcrypt</th></tr></thead>
  <tbody>
{lignes_hachages}
  </tbody>
</table>
<p><strong>CSRF retenu</strong> : cookie de session <code>SameSite=Lax</code>, API JSON sans
CORS, et contrôle explicite de l'en-tête <code>Origin</code> sur POST, PATCH, PUT et DELETE
(<code>src/Support/Csrf.php</code>). Une écriture venue d'un autre site reçoit
<code>403 ORIGINE_REFUSEE</code> avant le routeur. Un client sans navigateur (curl) n'envoie pas
<code>Origin</code> : il reste soumis à l'authentification par session. Le jeton de session par
formulaire n'a pas été ajouté pour ne pas modifier le contrat du TP6 ; il est consigné en dette
technique.</p>

<h2>6. Revue de code (4 remarques classées)</h2>
<table>
  <colgroup><col style="width:6%"><col style="width:39%"><col style="width:9%"><col style="width:46%"></colgroup>
  <thead><tr><th>Réf.</th><th>Constat</th><th>Niveau</th><th>État et correctif</th></tr></thead>
  <tbody>
{lignes_revue}
  </tbody>
</table>

<h2>7. Recette et conclusion</h2>
<table>
  <colgroup><col style="width:52%"><col style="width:32%"><col style="width:16%"></colgroup>
  <thead><tr><th>Scénario</th><th>Exigences couvertes</th><th>Verdict</th></tr></thead>
  <tbody>
{lignes_recette}
  </tbody>
</table>
<p>Les 5 scénarios de recette sont conformes et les {conformes} tests automatisés le sont aussi.
Deux remarques de revue ont été corrigées et sont couvertes par la matrice (T-06, T-10) ; une
troisième l'est par le scénario TP7 ; la quatrième (limitation des tentatives) est acceptée en
local et planifiée avant toute mise en ligne. Aucune réserve ne bloque la réception.</p>
<p class="note">Détail : <code>revue_code.md</code> (remarques et dette), <code>recette.md</code>
(procès-verbal et signatures), <code>preuves/resume.txt</code> (synthèse).</p>

<footer>Projet informatique 2 — L3 SIL — Plan de tests et audit de sécurité (TP8) — 18/11/2026</footer>
"""

    return f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8"><title>TP8 — Plan de tests et audit de sécurité</title>
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
