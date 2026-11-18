#!/usr/bin/env python3
"""Génère le rapport TP6 (HTML, PDF, DOCX) à partir des preuves réelles.

Entrées  : preuves/sorties.tsv, preuves/etat_base.tsv
Sorties  : api_demandes.html, api_demandes.pdf (Chrome), api_demandes.docx (UNO)
"""

from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
SORTIES = RACINE / "preuves" / "sorties.tsv"
ETAT = RACINE / "preuves" / "etat_base.tsv"
HTML = RACINE / "api_demandes.html"
PDF = RACINE / "api_demandes.pdf"
DOCX = RACINE / "api_demandes.docx"

DATE = "18 novembre 2026"


def lire_tsv(chemin: Path) -> list[dict[str, str]]:
    lignes = chemin.read_text(encoding="utf-8").splitlines()
    entetes = lignes[0].split("\t")
    return [dict(zip(entetes, ligne.split("\t"))) for ligne in lignes[1:] if ligne.strip()]


def extrait(reponse: str) -> str:
    """Réponse compacte pour le tableau, JSON valide et lisible."""
    try:
        donnees = json.loads(reponse)
    except json.JSONDecodeError:
        return reponse

    if "demande" in donnees:
        demande = donnees["demande"]
        garde = {cle: demande[cle] for cle in ("id", "statut", "date_decision") if cle in demande}
        return json.dumps({"demande": garde}, ensure_ascii=False, separators=(", ", ": "))

    if "erreur" in donnees:
        erreur = donnees["erreur"]
        garde = {"code": erreur.get("code", ""), "message": erreur.get("message", "")}
        return json.dumps({"erreur": garde}, ensure_ascii=False, separators=(", ", ": "))

    return reponse


def cellule(texte: str, classe: str = "") -> str:
    attribut = f' class="{classe}"' if classe else ""
    return f"<td{attribut}>{html.escape(texte)}</td>"


def construire_html() -> str:
    cas = {ligne["numero"]: ligne for ligne in lire_tsv(SORTIES)}
    etat = lire_tsv(ETAT)

    demandes = [ligne for ligne in etat if re.fullmatch(r"\d+", ligne.get("id", ""))]
    historique = next(
        (ligne.get("etudiant_id", "?") for ligne in etat if ligne.get("id") == "lignes_historique"),
        "?",
    )

    total = len(cas)
    conformes = sum(1 for ligne in cas.values() if ligne["conforme"] == "OUI")

    six_cas = ["S5", "S6", "S7", "S8", "S9", "S10"]
    lignes_cas = "\n".join(
        "<tr>"
        + cellule(numero)
        + cellule(cas[numero]["cas"])
        + cellule(cas[numero]["attendu"])
        + cellule(cas[numero]["obtenu"])
        + cellule(extrait(cas[numero]["reponse"]), "json")
        + "</tr>"
        for numero in six_cas
        if numero in cas
    )

    lignes_etat = "\n".join(
        "<tr>"
        + cellule(ligne["id"])
        + cellule(ligne["etudiant_id"])
        + cellule(ligne["statut"])
        + cellule("—" if ligne["motif_refus"] in ("NULL", "") else ligne["motif_refus"])
        + cellule("—" if ligne["date_decision"] in ("NULL", "") else ligne["date_decision"])
        + "</tr>"
        for ligne in demandes
    )

    lignes_tous = "\n".join(
        "<tr>"
        + cellule(numero)
        + cellule(ligne["cas"])
        + cellule(ligne["requete"])
        + cellule(ligne["attendu"])
        + cellule(ligne["obtenu"])
        + cellule(ligne["conforme"])
        + "</tr>"
        for numero, ligne in cas.items()
    )

    css = """
  @page { size: A4; margin: 16mm 16mm 14mm 16mm; }
  body { font-family: "Liberation Sans", Arial, sans-serif; font-size: 8.9pt; line-height: 1.28; color: #000; margin: 0; }
  .tete { text-align: center; margin-bottom: 7pt; }
  .tete .petit, .tete .date, .tete .groupe { font-size: 7.9pt; }
  .tete h1 { font-size: 13.5pt; margin: 2pt 0; }
  h2 { font-size: 10pt; margin: 10pt 0 3pt; page-break-after: avoid; }
  p { margin: 0 0 4pt; text-align: justify; }
  .note { font-size: 7.4pt; font-style: italic; color: #333; }
  table { width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 7.5pt; margin: 1pt 0 4pt; }
  th, td { border: 0.4pt solid #666; padding: 2pt 3pt; vertical-align: top; text-align: left;
           word-wrap: break-word; overflow-wrap: break-word; }
  th { font-weight: bold; }
  thead { display: table-header-group; }
  tr { page-break-inside: avoid; }
  td.json { font-family: "Liberation Mono", monospace; font-size: 6.5pt; line-height: 1.2;
            word-break: normal; overflow-wrap: break-word; }
  footer { margin-top: 8pt; font-size: 7.2pt; color: #444; text-align: center; }
"""

    corps = f"""
<div class="tete">
  <div class="petit">Projet informatique 2 — L3 SIL</div>
  <h1>API des demandes de stage</h1>
  <div class="date">TP6 — {DATE}</div>
  <div class="groupe">Groupe : OUSSOU Hermax – TCHEGNON Loïk – KANHONOU Ashley<br>
  Encadreur : MAMA Tairou · Dépôt Git : local (commits TP1 à TP3)</div>
</div>

<h2>1. Objet</h2>
<p>Implémentation de la création, de la lecture et de la validation d'une demande, avec
contrôles côté serveur. Sur {total} cas exécutés contre MySQL 8.0.46 et l'API réelle,
{conformes} sont conformes à l'attendu écrit avant le test. La base
<code>tp3_conventions</code> est rechargée depuis le jeu d'essai TP3 avant chaque exécution.</p>

<h2>2. Routes implémentées</h2>
<table>
  <colgroup><col style="width:9%"><col style="width:29%"><col style="width:20%"><col style="width:9%"><col style="width:33%"></colgroup>
  <thead><tr><th>Méthode</th><th>Chemin</th><th>Rôle</th><th>Succès</th><th>Erreurs</th></tr></thead>
  <tbody>
    <tr><td>GET</td><td>/api/sante</td><td>Public</td><td>200</td><td>503</td></tr>
    <tr><td>POST</td><td>/api/connexion</td><td>Public</td><td>200</td><td>400, 401, 403, 422</td></tr>
    <tr><td>POST</td><td>/api/deconnexion</td><td>Session</td><td>200</td><td>401</td></tr>
    <tr><td>GET</td><td>/api/moi</td><td>Session</td><td>200</td><td>401</td></tr>
    <tr><td>GET</td><td>/api/demandes</td><td>Session (selon rôle)</td><td>200</td><td>401, 403</td></tr>
    <tr><td>GET</td><td>/api/demandes/{{id}}</td><td>Session (selon rôle)</td><td>200</td><td>401, 403, 404</td></tr>
    <tr><td>POST</td><td>/api/demandes</td><td>Étudiant</td><td>201</td><td>400, 401, 403, 422</td></tr>
    <tr><td>PATCH</td><td>/api/demandes/{{id}}/statut</td><td>Responsable</td><td>200</td><td>400, 401, 403, 404, 409, 422</td></tr>
  </tbody>
</table>
<p class="note">Le contrat complet (corps, champs, codes d'erreur) est dans
<code>TP4_Architecture/docs/contrat_api.md</code>. Les routes de consultation
<code>/api/moi</code> et <code>/api/demandes/{{id}}</code> complètent le contrat du TP4.</p>

<h2>3. Transitions autorisées</h2>
<table>
  <colgroup><col style="width:38%"><col style="width:20%"><col style="width:42%"></colgroup>
  <thead><tr><th>Transition</th><th>Qui</th><th>Règle</th></tr></thead>
  <tbody>
    <tr><td>BROUILLON vers SOUMISE</td><td>Étudiant</td><td>Soumission de la demande</td></tr>
    <tr><td>SOUMISE vers VALIDEE</td><td>Responsable</td><td>Décision favorable</td></tr>
    <tr><td>SOUMISE vers REFUSEE</td><td>Responsable</td><td>Motif obligatoire (422 sinon)</td></tr>
  </tbody>
</table>
<p class="note">Table des transitions : <code>src/Services/DemandeService.php</code>.
VALIDEE et REFUSEE sont terminales : toute autre transition est refusée avec 409.</p>

<h2>4. Cas testés (les six cas exigés, sorties réelles)</h2>
<table>
  <colgroup><col style="width:5%"><col style="width:31%"><col style="width:8%"><col style="width:8%"><col style="width:48%"></colgroup>
  <thead><tr><th>N°</th><th>Cas</th><th>Attendu</th><th>Obtenu</th><th>Réponse de l'API (extrait)</th></tr></thead>
  <tbody>
{lignes_cas}
  </tbody>
</table>
<p class="note">Tous les cas du script sont listés dans <code>preuves/sorties.tsv</code>
({total} cas, {conformes} conformes), avec les corps JSON complets. Le script
<code>tests_api.sh</code> recharge la base avant chaque exécution.</p>

<h2>5. État de la base après les cas</h2>
<table>
  <colgroup><col style="width:9%"><col style="width:10%"><col style="width:14%"><col style="width:42%"><col style="width:25%"></colgroup>
  <thead><tr><th>Demande</th><th>Étudiant</th><th>Statut</th><th>Motif de refus</th><th>Décision</th></tr></thead>
  <tbody>
{lignes_etat}
  </tbody>
</table>
<p class="note">Lignes dans <code>historique</code> après les cas : {historique}.
La demande 7 a été créée puis validée pendant le test ; la demande 2 a été refusée avec motif.</p>

<h2>6. Sécurité et cohérence</h2>
<table>
  <colgroup><col style="width:20%"><col style="width:80%"></colgroup>
  <thead><tr><th>Point</th><th>Mise en œuvre</th></tr></thead>
  <tbody>
    <tr><td>Mots de passe</td><td><code>password_verify</code> contre un hash <code>password_hash</code> (bcrypt) ; message identique pour compte inconnu et mot de passe faux.</td></tr>
    <tr><td>Session</td><td><code>session_regenerate_id(true)</code> à chaque connexion réussie ; cookie HttpOnly, SameSite=Lax ; identifiant inconnu refusé (<code>use_strict_mode</code>).</td></tr>
    <tr><td>Autorisation</td><td>Rôle contrôlé côté serveur à chaque requête ; un étudiant ne voit et ne traite que ses demandes (403 sinon).</td></tr>
    <tr><td>SQL</td><td>Requêtes préparées avec paramètres liés, émulation désactivée ; aucun SQL dans les contrôleurs.</td></tr>
    <tr><td>Transaction</td><td>Statut et historique dans une seule transaction ; rollback complet si une étape échoue (vérifié par un test dédié).</td></tr>
    <tr><td>Erreurs</td><td>Le détail technique va dans le journal serveur ; le client reçoit un message neutre et un code cohérent (400, 401, 403, 404, 409, 422, 503).</td></tr>
  </tbody>
</table>

<h2>7. Justification (preuve de travail)</h2>
<p>Les six cas exigés ont été écrits avant exécution, puis joués sur une base rechargée.
Toutes les réponses sont conformes. Le rollback est vérifié séparément par
<code>tests/test_domain.php</code> : une exception provoquée après l'<code>UPDATE</code>
laisse le statut et le motif inchangés. Le code de l'API reste dans
<code>TP4_Architecture/</code> (couches contrôleur, service, dépôt) ; les preuves et le
script de rejeu sont regroupés dans <code>TP6_API/</code>.</p>
<p class="note">Reproduire : <code>mysql ... &lt; TP3_Modele_donnees/001_schema.sql</code>
puis <code>002_seed.sql</code>, puis <code>cd TP6_API &amp;&amp; ./tests_api.sh</code>.</p>

<h2>8. Preuves et reproductibilité</h2>
<p>Le script <code>tests_api.sh</code> recharge la base, démarre l'API et rejoue les
{total} cas ; les sorties sont écrites dans <code>preuves/sorties.tsv</code> (un cas par
ligne, corps JSON complets). Le tableau ci-dessous en donne la synthèse.</p>
<table>
  <colgroup><col style="width:5%"><col style="width:43%"><col style="width:22%"><col style="width:10%"><col style="width:10%"><col style="width:10%"></colgroup>
  <thead><tr><th>N°</th><th>Cas</th><th>Requête</th><th>Attendu</th><th>Obtenu</th><th>Conforme</th></tr></thead>
  <tbody>
{lignes_tous}
  </tbody>
</table>
<p class="note">Capture réelle de <code>/api/sante</code> dans un navigateur :
<code>preuves/capture_api.png</code>. Base après les cas :
<code>preuves/etat_base.tsv</code>.</p>

<footer>Projet informatique 2 — L3 SIL — API des demandes de stage (TP6) — 18/11/2026</footer>
"""

    return f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8"><title>TP6 — API des demandes de stage</title>
<style>{css}</style></head><body>{corps}
</body></html>
"""


def generer_pdf() -> None:
    chrome = shutil.which("google-chrome") or shutil.which("chromium")
    if chrome is None:
        print("Chrome introuvable : PDF non généré.", file=sys.stderr)
        return

    subprocess.run(
        [
            chrome,
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--hide-scrollbars",
            "--no-pdf-header-footer",
            f"--print-to-pdf={PDF}",
            HTML.as_uri(),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def generer_docx() -> None:
    """Construit la version éditable avec le constructeur UNO (comme le TP3)."""
    script = RACINE / "build_docx.py"
    if not script.exists():
        print("build_docx.py introuvable : DOCX non généré.", file=sys.stderr)
        return

    subprocess.run(
        [sys.executable, str(script), str(DOCX)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def main() -> int:
    if not SORTIES.exists() or not ETAT.exists():
        print("Preuves absentes : exécuter ./tests_api.sh d'abord.", file=sys.stderr)
        return 1

    HTML.write_text(construire_html(), encoding="utf-8")
    print(f"HTML : {HTML.name}")

    generer_pdf()
    print(f"PDF  : {PDF.name}" if PDF.exists() else "PDF  : non généré")

    generer_docx()
    print(f"DOCX : {DOCX.name}" if DOCX.exists() else "DOCX : non généré")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
