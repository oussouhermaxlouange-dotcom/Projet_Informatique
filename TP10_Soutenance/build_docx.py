#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construit la version DOCX du rapport TP10 avec le constructeur UNO partagé."""

from __future__ import annotations

import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE.parent / "outils"))
sys.path.insert(0, str(RACINE))

import rapport_uno as R  # noqa: E402
from rapport_uno import cellule  # noqa: E402
import build_rapport as D  # noqa: E402

DOCX = RACINE / "soutenance_tp10.docx"


def build() -> None:
    doc, b = R.nouveau_document(
        "Projet informatique 2 — L3 SIL — TP10 : dossier et soutenance — 20/11/2026"
    )

    # ---------------- En-tête ----------------
    b.para("Projet informatique 2 — L3 SIL", size=9, align=3, after=1, line=100)
    b.para("Dossier de livraison et soutenance", size=16, bold=True, align=3,
           after=1, line=100)
    b.para("Liste de contrôle, démonstration de 8 minutes, oral individuel et bilan",
           size=10.5, align=3, after=1, line=100)
    b.para(f"TP10 — Dossier et démonstration — {D.DATE}", size=10, align=3, after=0.5,
           line=100)
    b.para(
        "Groupe : OUSSOU Hermax – TCHEGNON Loïk – KANHONOU Ashley\n"
        "Encadreur : MAMA Tairou · 8 minutes de démonstration · données fictives",
        size=9, align=3, after=4, line=105,
    )

    # ---------------- 1. Checklist ----------------
    b.heading("1. Dossier de livraison — liste de contrôle (8 éléments)")
    t = b.table(len(D.CHECKLIST) + 1, 3, [3800, 5600, 8000])
    for i, h in enumerate(["Élément", "Emplacement", "Vérification et état"]):
        cellule(b, t, 0, i, h, bold=True, size=7.5)
    for r, (element, emplacement, etat) in enumerate(D.CHECKLIST, start=1):
        cellule(b, t, r, 0, element, size=7.2, bold=True)
        cellule(b, t, r, 1, emplacement, size=6.7, mono=True)
        cellule(b, t, r, 2, etat, size=7.2)
    b.para(
        "Deux réserves sont assumées : pas de migration évolutive (scripts numérotés et "
        "rejouables) et un historique Git groupé par jalon. Elles sont traitées en "
        "rétrospective.",
        size=9.5, align=2, before=1, after=1.5,
    )

    # ---------------- 2. Scénario ----------------
    b.heading("2. Scénario de démonstration (8 minutes)")
    t = b.table(len(D.SCENARIO) + 1, 4, [1500, 4000, 9800, 2100])
    for i, h in enumerate(["Temps", "Séquence", "Preuve montrée", "Qui"]):
        cellule(b, t, 0, i, h, bold=True, size=7.5,
                align=(3 if i in (0, 3) else 0))
    for r, (temps, sequence, preuve, qui) in enumerate(D.SCENARIO, start=1):
        cellule(b, t, r, 0, temps, size=7.2, align=3)
        cellule(b, t, r, 1, sequence, size=7.2, bold=True)
        cellule(b, t, r, 2, preuve, size=7.2)
        cellule(b, t, r, 3, qui, size=7.2, align=3)
    b.para(
        "La programmation de soutenance (EF-05) n'est pas exposée par l'API : elle est "
        "montrée par la vue v_planning_soutenance du TP3, puis annoncée en version 2. "
        "Aucune fonctionnalité inexistante n'est simulée.",
        size=9.5, align=2, before=1, after=1.5,
    )

    # ---------------- 3. Répétition et repli ----------------
    b.heading("3. Répétition et solution de repli")
    t = b.table(len(D.REPETITION) + 1, 4, [1200, 2400, 2000, 11800])
    for i, h in enumerate(["Passage", "Durée", "Écart", "Décision"]):
        cellule(b, t, 0, i, h, bold=True, size=7.5,
                align=(3 if i in (0, 1, 2) else 0))
    for r, (num, duree, ecart, decision) in enumerate(D.REPETITION, start=1):
        cellule(b, t, r, 0, num, size=7.2, align=3)
        cellule(b, t, r, 1, duree, size=7.2, align=3)
        cellule(b, t, r, 2, ecart, size=7.2, align=3)
        cellule(b, t, r, 3, decision, size=7.2)
    b.para(
        "Repli préparé et testé : chaque panne a une réaction immédiate et une preuve de "
        "substitution disponible hors ligne. Le chronomètre est visible et remis à zéro avant "
        "l'entrée du jury.",
        size=9.5, align=2, before=1, after=1.5,
    )
    t = b.table(len(D.REPLI) + 1, 3, [3000, 7600, 6800])
    for i, h in enumerate(["Panne", "Réaction immédiate", "Preuve de substitution"]):
        cellule(b, t, 0, i, h, bold=True, size=7.5)
    for r, (risque, reaction, preuve) in enumerate(D.REPLI, start=1):
        cellule(b, t, r, 0, risque, size=7.2, bold=True)
        cellule(b, t, r, 1, reaction, size=7.2)
        cellule(b, t, r, 2, preuve, size=7.2)

    # ---------------- Page 2 ----------------
    b.page_break()

    # ---------------- 4. Réponses individuelles ----------------
    b.heading("4. Réponses individuelles")
    t = b.table(len(D.REPONSES) + 1, 5, [1250, 4200, 5200, 3300, 3450])
    for i, h in enumerate(["Membre", "Règle métier", "Requête", "Test", "Commit"]):
        cellule(b, t, 0, i, h, bold=True, size=7.2)
    for r, (membre, regle, requete, test, commit) in enumerate(D.REPONSES, start=1):
        cellule(b, t, r, 0, membre, size=7.2, bold=True)
        cellule(b, t, r, 1, regle, size=7)
        cellule(b, t, r, 2, requete, size=6.6, mono=True)
        cellule(b, t, r, 3, test, size=7)
        cellule(b, t, r, 4, commit, size=6.6, mono=True)
    b.note(
        "Réponses complètes, relances et grille d'auto-évaluation : "
        "questions_individuales.md. L'historique Git est centralisé : la question porte sur "
        "le contenu du commit et les fichiers, pas sur la signature."
    )

    # ---------------- 5. Questions transverses ----------------
    b.heading("5. Questions transverses")
    t = b.table(len(D.TRANSVERSES) + 1, 2, [5600, 11800])
    for i, h in enumerate(["Question du jury", "Réponse attendue"]):
        cellule(b, t, 0, i, h, bold=True, size=7.5)
    for r, (question, reponse) in enumerate(D.TRANSVERSES, start=1):
        cellule(b, t, r, 0, question, size=7.2, bold=True)
        cellule(b, t, r, 1, reponse, size=7.2)

    # ---------------- 6. Rétrospective ----------------
    b.heading("6. Rétrospective")
    t = b.table(len(D.RETRO) + 1, 3, [5800, 5800, 5800])
    for i, h in enumerate(["Ce qui a bien fonctionné", "Ce qui a été difficile",
                           "Ce que nous changeons (v2)"]):
        cellule(b, t, 0, i, h, bold=True, size=7.2)
    for r, (positif, difficulte, changement) in enumerate(D.RETRO, start=1):
        cellule(b, t, r, 0, positif, size=7)
        cellule(b, t, r, 1, difficulte, size=7)
        cellule(b, t, r, 2, changement, size=7)
    b.para(
        "La priorité de la version 2 est de finir le métier — programmer une soutenance avec "
        "contrôle de salle et d'encadreur, publier le planning — avant les notifications et "
        "le portail entreprise. La dette technique (R-04, migrations, CI) passe avant les "
        "nouvelles fonctionnalités.",
        size=9.5, align=2, before=1.5, after=1,
    )
    t = b.table(len(D.DECISIONS) + 1, 3, [9000, 4200, 4200])
    for i, h in enumerate(["Décision", "Échéance", "Responsable"]):
        cellule(b, t, 0, i, h, bold=True, size=7.5, align=(3 if i else 0))
    for r, (decision, echeance, qui) in enumerate(D.DECISIONS, start=1):
        cellule(b, t, r, 0, decision, size=7.2)
        cellule(b, t, r, 1, echeance, size=7.2, align=3)
        cellule(b, t, r, 2, qui, size=7.2, align=3)

    # ---------------- 7. Conclusion ----------------
    b.heading("7. Conclusion")
    b.para(
        "Le dossier est complet et reproductible : clone Git, installation sur un second "
        "poste, santé à 200, 14/14 tests, 8/8 mots de passe bcrypt, restauration 9/9. La "
        "démonstration tient en 8 minutes et chaque séquence montre une preuve. Les "
        "faiblesses sont nommées et datées : historique Git groupé, EF-05 hors API, pas de "
        "migration évolutive. Le projet est prêt pour la soutenance.",
        size=9.5, align=2, before=1, after=1,
    )
    b.note(
        "Détail : dossier_livraison.md, scenario_demonstration.md, "
        "questions_individuales.md, retrospective.md."
    )

    R.enregistrer_docx(
        doc,
        DOCX,
        "TP10 — Dossier de livraison et soutenance",
        "Projet informatique 2, L3 SIL",
        "OUSSOU Hermax, TCHEGNON Loïk, KANHONOU Ashley",
        "TP10 — liste de contrôle, démonstration, oral individuel et rétrospective",
    )


if __name__ == "__main__":
    build()
    print(f"DOCX : {DOCX}")
