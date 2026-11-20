#!/usr/bin/env python3
"""Génère le rapport TP10 (HTML, PDF, DOCX) : dossier, démonstration, oral, bilan.

Sorties : soutenance_tp10.html, soutenance_tp10.pdf (Chrome), soutenance_tp10.docx (UNO)
"""

from __future__ import annotations

import html
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
HTML = RACINE / "soutenance_tp10.html"
PDF = RACINE / "soutenance_tp10.pdf"
DOCX = RACINE / "soutenance_tp10.docx"

DATE = "20 novembre 2026"

CHECKLIST = [
    ("Dépôt Git et historique", "racine, origin GitHub, .gitignore",
     "clone propre, 170 fichiers, dernier commit 4179d8c"),
    ("Fiche de cadrage", "TP1_Fiche_cadrage.md / .docx",
     "problème, acteurs, périmètre, objectifs SMART"),
    ("Exigences et traçabilité", "TP2_Exigences.md / .docx",
     "8 EF, 3 ENF, matrice exigence → composant → test"),
    ("Diagrammes UML", "TP3_Modele_donnees/",
     "4 acteurs, 9 cas, 9 classes, SVG/PNG/PUML"),
    ("Schéma SQL", "001_schema.sql",
     "9 tables, clés étrangères, contraintes, 4 vues"),
    ("Scripts SQL et jeu d'essai", "002 à 004_*.sql",
     "seed, vérifications, tests de contraintes"),
    ("Plan de tests et recette", "TP8_Tests/",
     "14/14 tests, 5/5 scénarios, revue de code"),
    ("README et ADR", "TP4_Architecture/ + TP9_Deploiement/",
     "installation, ADR-001, sauvegarde 9/9"),
]

SCENARIO = [
    ("0:00–1:00", "Contexte et problème", "Indicateurs TP1 : 12 jours, 35 %, 4 conflits", "Hermax"),
    ("1:00–3:00", "Dépôt d'une demande", "Ligne SOUMISE en base, écran de confirmation", "Loïk"),
    ("3:00–4:00", "Validation", "Statut VALIDEE + ligne d'historique", "Hermax"),
    ("4:00–5:00", "Programmation de la soutenance", "v_planning_soutenance (2), conflits = 0 ; EF-05 en v2", "Ashley"),
    ("5:00–6:00", "Contrôle d'accès", "403 ACCES_REFUSE, session de B vers dossier de A", "Loïk"),
    ("6:00–8:00", "Tests et bilan", "14/14 tests, 8/8 bcrypt, 9/9 tables restaurées", "Ashley, Hermax"),
]

REPONSES = [
    ("Hermax",
     "Refus sans motif → 422, aucun statut écrit ; décision en transaction.",
     "UPDATE convention SET statut = :statut … WHERE id = :id (préparée, rowCount = 1).",
     "T-02 : 422 + statut inchangé.",
     "ab5239c : API TP4/TP6, DemandeService et DemandeRepository."),
    ("Loïk",
     "Une convention → au plus une soutenance ; encadreur identique par clé composite.",
     "SELECT * FROM v_planning_soutenance ; contraintes de soutenance.",
     "004 : doublon, encadreur incohérent et chevauchement refusés.",
     "bd0ed02 : correction UML TP3, cas d'utilisation et rapport."),
    ("Ashley",
     "Mot de passe bcrypt ; écriture inter-site refusée par contrôle de Origin.",
     "SELECT … FROM utilisateur WHERE email = :email ; password_verify().",
     "T-13 : 8/8 bcrypt ; T-10 : 403 ORIGINE_REFUSEE.",
     "4179d8c : dossier TP8, matrice, revue, recette et preuves."),
]

REPETITION = [
    ("1", "9 min 10 s", "+70 s", "contexte réduit à 45 s, tests à 90 s"),
    ("2", "8 min 05 s", "+5 s", "une phrase sur les vues supprimée"),
    ("3", "7 min 52 s", "−8 s", "scénario retenu, marge conservée"),
]

REPLI = [
    ("Serveur PHP arrêté", "relancer php -S ; sinon passer à la vidéo", "vidéo locale de 8 minutes"),
    ("Base indisponible", "restaurer le dump TP9 en moins de 2 minutes", "preuves/restauration.txt"),
    ("Réseau ou vidéoprojecteur", "poste local et rapports PDF", "tests_securite.pdf"),
    ("Session ou compte erroné", "changer de profil de navigateur", "captures TP7 01…13"),
]

TRANSVERSES = [
    ("Pourquoi PHP sans framework ?", "Déploiement immédiat, aucune dépendance, code lisible ; ADR-001."),
    ("Où sont les règles métier ?", "Dans les Services, jamais dans les contrôleurs ni dans le HTML."),
    ("Comment la restauration est-elle prouvée ?", "Dump restauré, table supprimée, 9/9 tables identiques."),
    ("Quelle est la limite principale ?", "EF-05 (programmation de soutenance) hors API ; traitée en version 2."),
]

DECISIONS = [
    ("Un commit par fonctionnalité et par membre", "immédiat", "tous"),
    ("Migration avant toute évolution du schéma", "version 2", "Hermax"),
    ("EF-05 avec contrôle de conflit", "version 2", "Loïk"),
    ("Limitation des tentatives (R-04)", "avant mise en ligne", "Ashley"),
]

RETRO = [
    ("Chaîne de preuve exigence → composant → test → sortie ; 14/14 tests, 8/8 bcrypt, 9/9 tables restaurées ; une seule application du TP4 au TP9.",
     "Commits groupés en fin de jalon ; EF-05 hors API ; socket MySQL obsolète et 503 difficile à diagnostiquer ; 25 heures pour trois.",
     "Un commit par fonctionnalité et par membre ; CI minimale ; EF-05 avec contrôle de conflit ; migrations versionnées ; limitation des tentatives."),
]


def cellule(texte: str, classe: str = "") -> str:
    attribut = f' class="{classe}"' if classe else ""
    return f"<td{attribut}>{html.escape(str(texte))}</td>"


def construire_html() -> str:
    lignes_checklist = "\n".join(
        "<tr>" + cellule(element, "gras") + cellule(emplacement, "mono")
        + cellule(etat) + "</tr>"
        for element, emplacement, etat in CHECKLIST
    )
    lignes_scenario = "\n".join(
        "<tr>" + cellule(temps, "c") + cellule(sequence, "gras")
        + cellule(preuve) + cellule(qui, "c") + "</tr>"
        for temps, sequence, preuve, qui in SCENARIO
    )
    lignes_reponses = "\n".join(
        "<tr>" + cellule(membre, "gras") + cellule(regle) + cellule(requete, "mono")
        + cellule(test) + cellule(commit, "mono") + "</tr>"
        for membre, regle, requete, test, commit in REPONSES
    )
    lignes_repetition = "\n".join(
        "<tr>" + cellule(num, "c") + cellule(duree, "c") + cellule(ecart, "c")
        + cellule(decision) + "</tr>"
        for num, duree, ecart, decision in REPETITION
    )
    lignes_repli = "\n".join(
        "<tr>" + cellule(risque, "gras") + cellule(reaction) + cellule(preuve) + "</tr>"
        for risque, reaction, preuve in REPLI
    )
    lignes_transverses = "\n".join(
        "<tr>" + cellule(question, "gras") + cellule(reponse) + "</tr>"
        for question, reponse in TRANSVERSES
    )
    lignes_decisions = "\n".join(
        "<tr>" + cellule(decision) + cellule(echeance, "c") + cellule(qui, "c") + "</tr>"
        for decision, echeance, qui in DECISIONS
    )
    lignes_retro = "\n".join(
        "<tr>" + cellule(positif) + cellule(difficulte) + cellule(changement) + "</tr>"
        for positif, difficulte, changement in RETRO
    )

    css = """
  @page { size: A4; margin: 14mm 14mm 12mm 14mm; }
  body { font-family: "Liberation Sans", Arial, sans-serif; font-size: 9pt; line-height: 1.27; color: #000; margin: 0; }
  .tete { text-align: center; margin-bottom: 5pt; }
  .tete .petit, .tete .date, .tete .groupe { font-size: 7.6pt; }
  .tete h1 { font-size: 14.8pt; margin: 2pt 0; font-family: Georgia, serif; font-weight: normal; }
  h2 { font-size: 10.1pt; margin: 7pt 0 2.5pt; page-break-after: avoid; }
  h2.saut-page { page-break-before: always; margin-top: 0; }
  p { margin: 0 0 3pt; text-align: justify; }
  .note { font-size: 6.9pt; font-style: italic; color: #333; }
  code, .mono { font-family: "Liberation Mono", monospace; font-size: 6.9pt; }
  table { width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 7.2pt; margin: 1pt 0 3pt; }
  th, td { border: 0.4pt solid #555; padding: 1.85pt 2.3pt; vertical-align: top; text-align: left;
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
  <h1>Dossier de livraison et soutenance</h1>
  <div class="date">TP10 — Dossier et démonstration — {DATE}</div>
  <div class="groupe">Groupe : OUSSOU Hermax – TCHEGNON Loïk – KANHONOU Ashley<br>
  Encadreur : MAMA Tairou · 8 minutes de démonstration · données fictives</div>
</div>

<h2>1. Dossier de livraison — liste de contrôle (8 éléments)</h2>
<table>
  <colgroup><col style="width:22%"><col style="width:33%"><col style="width:45%"></colgroup>
  <thead><tr><th>Élément</th><th>Emplacement</th><th>Vérification et état</th></tr></thead>
  <tbody>
{lignes_checklist}
  </tbody>
</table>
<p>Deux réserves sont assumées : pas de migration évolutive (scripts numérotés et
rejouables) et un historique Git groupé par jalon. Elles sont traitées en rétrospective.</p>

<h2>2. Scénario de démonstration (8 minutes)</h2>
<table>
  <colgroup><col style="width:10%"><col style="width:24%"><col style="width:54%"><col style="width:12%"></colgroup>
  <thead><tr><th>Temps</th><th>Séquence</th><th>Preuve montrée</th><th>Qui</th></tr></thead>
  <tbody>
{lignes_scenario}
  </tbody>
</table>
<p>La programmation de soutenance (EF-05) n'est pas exposée par l'API : elle est montrée
par la vue <code>v_planning_soutenance</code> du TP3, puis annoncée en version 2. Aucune
fonctionnalité inexistante n'est simulée.</p>

<h2>3. Répétition et solution de repli</h2>
<table>
  <colgroup><col style="width:8%"><col style="width:14%"><col style="width:12%"><col style="width:66%"></colgroup>
  <thead><tr><th>Passage</th><th>Durée</th><th>Écart</th><th>Décision</th></tr></thead>
  <tbody>
{lignes_repetition}
  </tbody>
</table>
<p><strong>Repli préparé et testé</strong> : chaque panne a une réaction immédiate et une
preuve de substitution disponible hors ligne. Le chronomètre est visible et remis à zéro
avant l'entrée du jury.</p>
<table>
  <colgroup><col style="width:24%"><col style="width:42%"><col style="width:34%"></colgroup>
  <thead><tr><th>Panne</th><th>Réaction immédiate</th><th>Preuve de substitution</th></tr></thead>
  <tbody>
{lignes_repli}
  </tbody>
</table>

<h2 class="saut-page">4. Réponses individuelles</h2>
<table>
  <colgroup><col style="width:8%"><col style="width:25%"><col style="width:29%"><col style="width:19%"><col style="width:19%"></colgroup>
  <thead><tr><th>Membre</th><th>Règle métier</th><th>Requête</th><th>Test</th><th>Commit</th></tr></thead>
  <tbody>
{lignes_reponses}
  </tbody>
</table>
<p class="note">Réponses complètes, relances et grille d'auto-évaluation :
<code>questions_individuales.md</code>. L'historique Git est centralisé : la question
porte sur le contenu du commit et les fichiers, pas sur la signature.</p>

<h2>5. Questions transverses</h2>
<table>
  <colgroup><col style="width:34%"><col style="width:66%"></colgroup>
  <thead><tr><th>Question du jury</th><th>Réponse attendue</th></tr></thead>
  <tbody>
{lignes_transverses}
  </tbody>
</table>

<h2>6. Rétrospective</h2>
<table>
  <colgroup><col style="width:33%"><col style="width:34%"><col style="width:33%"></colgroup>
  <thead><tr><th>Ce qui a bien fonctionné</th><th>Ce qui a été difficile</th><th>Ce que nous changeons (v2)</th></tr></thead>
  <tbody>
{lignes_retro}
  </tbody>
</table>
<p>La priorité de la version 2 est de finir le métier — programmer une soutenance avec
contrôle de salle et d'encadreur, publier le planning — avant les notifications et le
portail entreprise. La dette technique (R-04, migrations, CI) passe avant les nouvelles
fonctionnalités.</p>
<table>
  <colgroup><col style="width:52%"><col style="width:24%"><col style="width:24%"></colgroup>
  <thead><tr><th>Décision</th><th>Échéance</th><th>Responsable</th></tr></thead>
  <tbody>
{lignes_decisions}
  </tbody>
</table>

<h2>7. Conclusion</h2>
<p>Le dossier est complet et reproductible : clone Git, installation sur un second poste,
santé à <code>200</code>, 14/14 tests, 8/8 mots de passe bcrypt, restauration 9/9. La
démonstration tient en 8 minutes et chaque séquence montre une preuve. Les faiblesses sont
nommées et datées : historique Git groupé, EF-05 hors API, pas de migration évolutive.
Le projet est prêt pour la soutenance.</p>
<p class="note">Détail : <code>dossier_livraison.md</code>,
<code>scenario_demonstration.md</code>, <code>questions_individuales.md</code>,
<code>retrospective.md</code>.</p>

<footer>Projet informatique 2 — L3 SIL — Dossier de livraison et soutenance (TP10) — 20/11/2026</footer>
"""

    return f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8"><title>TP10 — Dossier de livraison et soutenance</title>
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
