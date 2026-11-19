#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construit la version DOCX du rapport TP8 avec le constructeur UNO partagé."""

from __future__ import annotations

import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE.parent / "outils"))
sys.path.insert(0, str(RACINE))

import rapport_uno as R  # noqa: E402
from rapport_uno import cellule  # noqa: E402
import build_rapport as D  # noqa: E402

DOCX = RACINE / "tests_securite.docx"


def build() -> None:
    cas = D.lire_tsv(D.SORTIES)
    hachages = D.lire_tsv(D.HACHAGES)
    total = len(cas)
    conformes = sum(1 for ligne in cas if ligne["conforme"] == "OUI")
    bcrypt = sum(1 for ligne in hachages if ligne["bcrypt"] == "OUI")

    doc, b = R.nouveau_document(
        "Projet informatique 2 — L3 SIL — TP8 : tests et sécurité — 18/11/2026"
    )

    # ---------------- En-tête ----------------
    b.para("Projet informatique 2 — L3 SIL", size=9, align=3, after=1, line=100)
    b.para("Plan de tests et audit de sécurité", size=16, bold=True, align=3,
           after=1, line=100)
    b.para("Matrice, cas limites, autorisations, injection, hachage et revue",
           size=10.5, align=3, after=1, line=100)
    b.para(f"TP8 — Tests et sécurité — {D.DATE}", size=10, align=3, after=0.5, line=100)
    b.para(
        "Groupe : OUSSOU Hermax – TCHEGNON Loïk – KANHONOU Ashley\n"
        "Encadreur : MAMA Tairou · MySQL 8.0.46 · API réelle · données fictives",
        size=9, align=3, after=4, line=105,
    )

    # ---------------- 1. Objet ----------------
    b.heading("1. Objet et méthode")
    b.para(
        f"Vérifier l'application par une matrice de tests et des contrôles de sécurité. Les {total} "
        "cas ont été écrits avant exécution : l'attendu et le code HTTP attendu sont des paramètres "
        "du script tests_securite.sh, qui recharge la base TP3, démarre l'API sur le port 8086 et "
        "compare le code obtenu à l'attendu. Deux cas relisent en plus le statut en base (refus sans "
        "motif, validation répétée) et un cas compare le nombre de lignes avant et après une "
        f"création invalide. Résultat : {conformes} / {total} conformes.",
        size=9.5, align=2, after=1,
    )

    # ---------------- 2. Matrice ----------------
    b.heading(f"2. Matrice de tests ({total} lignes)")
    t = b.table(len(cas) + 1, 7, [750, 850, 3900, 3900, 1500, 1000, 1100])
    for i, h in enumerate(["Test", "Exig.", "Cas", "Données", "Attendu", "Observé", "Conforme"]):
        cellule(b, t, 0, i, h, bold=True, size=7,
                align=(3 if i in (0, 1, 4, 5, 6) else 0))
    for r, ligne in enumerate(cas, start=1):
        valeurs = [
            ligne["test"], ligne["exigence"], ligne["cas"],
            D.DONNEES.get(ligne["test"], ligne["requete"]),
            ligne["attendu"], ligne["obtenu"], ligne["conforme"],
        ]
        for c, val in enumerate(valeurs):
            cellule(b, t, r, c, val, size=6.7,
                    align=(3 if c in (0, 1, 4, 5, 6) else 0))
    b.note(
        "Matrice détaillée, avec la réponse JSON complète : matrice_tests.md et "
        "preuves/sorties.tsv."
    )

    # ---------------- 3. Cas limites ----------------
    b.heading("3. Les quatre cas limites exigés")
    t = b.table(len(D.CAS_LIMITES) + 1, 4, [3000, 900, 2500, 11000])
    for i, h in enumerate(["Cas limite", "Test", "Réponse", "Ce que le test prouve"]):
        cellule(b, t, 0, i, h, bold=True, size=7.5,
                align=(3 if i in (1, 2) else 0))
    for r, (nom, test, reponse, preuve) in enumerate(D.CAS_LIMITES, start=1):
        cellule(b, t, r, 0, nom, size=7.5, bold=True)
        cellule(b, t, r, 1, test, size=7.5, align=3)
        cellule(b, t, r, 2, reponse, size=7.5, align=3)
        cellule(b, t, r, 3, preuve, size=7.5)

    # ---------------- 4. Autorisation et injection ----------------
    b.heading("4. Autorisation et injection")
    b.para(
        "Étudiante B vers le dossier de A (T-05) : la session de B est valide et la demande 1 "
        "existe ; la réponse est pourtant 403 ACCES_REFUSE, sans corps utile. Le contrôle est fait "
        "dans DemandeService sur etudiant_utilisateur_id. Étudiante A qui tente de décider (T-08) : "
        "403 ROLE_NON_AUTORISE ; le rôle est vérifié côté serveur à chaque requête, jamais à partir "
        "d'un paramètre client.",
        size=9.5, align=2, after=1.5,
    )
    b.para(
        "Chaîne « 1 OR 1=1 » (T-06, T-09, T-09b) : comme identifiant de route, elle est rejetée par "
        "ctype_digit() avant tout appel au dépôt (404) ; dans le champ e-mail, par "
        "FILTER_VALIDATE_EMAIL (422) ; dans le mot de passe, par l'échec de password_verify() (401). "
        "Aucun de ces chemins ne construit de SQL par concaténation : requêtes préparées avec "
        "PDO::ATTR_EMULATE_PREPARES = false.",
        size=9.5, align=2, after=1.5,
    )

    # ---------------- Page 2 ----------------
    b.page_break()

    # ---------------- 5. Mots de passe et CSRF ----------------
    b.heading("5. Mots de passe et protection CSRF")
    b.para(
        f"Les {len(hachages)} comptes du jeu d'essai portent une empreinte bcrypt de 60 caractères "
        f"({bcrypt}/{len(hachages)} conformes, 0 mot de passe en clair). La vérification utilise "
        "password_verify() et une empreinte factice égalise le temps de réponse entre compte "
        "inconnu et mot de passe faux.",
        size=9.5, align=2, after=1.5,
    )
    t = b.table(len(hachages) + 1, 4, [6200, 2500, 3600, 1300])
    for i, h in enumerate(["Compte", "Rôle", "Empreinte", "bcrypt"]):
        cellule(b, t, 0, i, h, bold=True, size=7,
                align=(3 if i in (1, 3) else 0))
    for r, ligne in enumerate(hachages, start=1):
        cellule(b, t, r, 0, ligne["email"], size=7, mono=True)
        cellule(b, t, r, 1, ligne["role"], size=7, align=3)
        cellule(b, t, r, 2, ligne["empreinte"] + "…", size=7, mono=True)
        cellule(b, t, r, 3, ligne["bcrypt"], size=7, align=3)
    b.para(
        "CSRF retenu : cookie de session SameSite=Lax, API JSON sans CORS, et contrôle explicite "
        "de l'en-tête Origin sur POST, PATCH, PUT et DELETE (src/Support/Csrf.php). Une écriture "
        "venue d'un autre site reçoit 403 ORIGINE_REFUSEE avant le routeur. Un client sans "
        "navigateur (curl) n'envoie pas Origin : il reste soumis à l'authentification par session. "
        "Le jeton de session par formulaire n'a pas été ajouté pour ne pas modifier le contrat du "
        "TP6 ; il est consigné en dette technique.",
        size=9.5, align=2, after=1.5,
    )

    # ---------------- 6. Revue ----------------
    b.heading("6. Revue de code (4 remarques classées)")
    t = b.table(len(D.REVUE) + 1, 4, [800, 6600, 1300, 8100])
    for i, h in enumerate(["Réf.", "Constat", "Niveau", "État et correctif"]):
        cellule(b, t, 0, i, h, bold=True, size=7.2,
                align=(3 if i in (0, 2) else 0))
    for r, (ref, constat, niveau, etat) in enumerate(D.REVUE, start=1):
        cellule(b, t, r, 0, ref, size=7.2, align=3)
        cellule(b, t, r, 1, constat, size=7.2)
        cellule(b, t, r, 2, niveau, size=7.2, align=3)
        cellule(b, t, r, 3, etat, size=7.2)

    # ---------------- 7. Recette ----------------
    b.heading("7. Recette et conclusion")
    t = b.table(len(D.RECETTE) + 1, 3, [9200, 5700, 1900])
    for i, h in enumerate(["Scénario", "Exigences couvertes", "Verdict"]):
        cellule(b, t, 0, i, h, bold=True, size=7.5,
                align=(3 if i in (1, 2) else 0))
    for r, (nom, exigences, verdict) in enumerate(D.RECETTE, start=1):
        cellule(b, t, r, 0, nom, size=7.5)
        cellule(b, t, r, 1, exigences, size=7.5, align=3)
        cellule(b, t, r, 2, verdict, size=7.5, align=3)
    b.para(
        f"Les 5 scénarios de recette sont conformes et les {conformes} tests automatisés le sont "
        "aussi. Deux remarques de revue ont été corrigées et sont couvertes par la matrice (T-06, "
        "T-10) ; une troisième l'est par le scénario TP7 ; la quatrième (limitation des tentatives) "
        "est acceptée en local et planifiée avant toute mise en ligne. Aucune réserve ne bloque la "
        "réception.",
        size=9.5, align=2, before=2, after=1,
    )
    b.note(
        "Détail : revue_code.md (remarques et dette), recette.md (procès-verbal et signatures), "
        "preuves/resume.txt (synthèse)."
    )

    R.enregistrer_docx(
        doc,
        DOCX,
        "TP8 — Plan de tests et audit de sécurité",
        "Projet informatique 2, L3 SIL",
        "OUSSOU Hermax, TCHEGNON Loïk, KANHONOU Ashley",
        "TP8 — matrice de tests, sécurité et revue de code",
    )


if __name__ == "__main__":
    build()
    print(f"DOCX : {DOCX}")
