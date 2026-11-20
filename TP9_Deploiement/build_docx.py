#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construit la version DOCX du rapport TP9 avec le constructeur UNO partagé."""

from __future__ import annotations

import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE.parent / "outils"))
sys.path.insert(0, str(RACINE))

import rapport_uno as R  # noqa: E402
from rapport_uno import cellule  # noqa: E402
import build_rapport as D  # noqa: E402

DOCX = RACINE / "deploiement_tp9.docx"


def build() -> None:
    taille, sha, lignes = D.empreinte()
    total = len(D.COMPTAGES)

    doc, b = R.nouveau_document(
        "Projet informatique 2 — L3 SIL — TP9 : déploiement et sauvegarde — 20/11/2026"
    )

    # ---------------- En-tête ----------------
    b.para("Projet informatique 2 — L3 SIL", size=9, align=3, after=1, line=100)
    b.para("Déploiement, compte SQL dédié et sauvegarde", size=16, bold=True, align=3,
           after=1, line=100)
    b.para("Installation reproductible, droits limités, restauration vérifiée, incident",
           size=10.5, align=3, after=1, line=100)
    b.para(f"TP9 — Déploiement et maintenance — {D.DATE}", size=10, align=3, after=0.5,
           line=100)
    b.para(
        "Groupe : OUSSOU Hermax – TCHEGNON Loïk – KANHONOU Ashley\n"
        "Encadreur : MAMA Tairou · PHP 8.5.12 · MySQL 8.0.46 · données fictives",
        size=9, align=3, after=4, line=105,
    )

    # ---------------- 1. Objet ----------------
    b.heading("1. Objet et méthode")
    b.para(
        "Installer l'application sur un second poste, avec un compte SQL à droits limités, "
        "puis prouver qu'une sauvegarde est réutilisable. Le second poste est un clone Git "
        "réel du dépôt (git clone local, commit 4179d8c, 170 fichiers, clone propre), "
        "installé en suivant uniquement son README. Le serveur MySQL est une instance isolée "
        "(socket /tmp/opencode/mysql_tp9/run/mysql.sock, port 3309), afin de ne pas toucher "
        "la base principale. Chaque étape est rejouée et sa sortie est conservée dans "
        "preuves/.",
        size=9.5, align=2, after=1,
    )

    # ---------------- 2. Installation ----------------
    b.heading("2. Installation sur le second poste")
    t = b.table(len(D.INSTALLATION) + 1, 3, [2900, 7700, 6800])
    for i, h in enumerate(["Étape", "Commande ou contrôle", "Résultat obtenu"]):
        cellule(b, t, 0, i, h, bold=True, size=7.5)
    for r, (etape, commande, resultat) in enumerate(D.INSTALLATION, start=1):
        cellule(b, t, r, 0, etape, size=7.5, bold=True)
        cellule(b, t, r, 1, commande, size=7.2, mono=True)
        cellule(b, t, r, 2, resultat, size=7.5)
    b.para(
        "La base importée contient le jeu fictif du TP3. GET /api/sante répond "
        '{"statut":"ok","base":"ok","horodatage":"2026-11-20T08:31:11+00:00"}, puis la '
        "connexion de sena.houngbo@univ.test renvoie 200 et la liste de ses demandes. "
        "Preuve : preuves/installation.txt.",
        size=9.5, align=2, before=1, after=1.5,
    )

    # ---------------- 3. Compte SQL ----------------
    b.heading("3. Compte SQL à droits limités")
    b.para(
        "CREATE USER 'tp9_app'@'localhost' IDENTIFIED BY 'Tp9Demo!2026'; "
        "GRANT SELECT, INSERT, UPDATE, DELETE ON tp3_conventions.* TO 'tp9_app'@'localhost';",
        size=8.5, align=2, before=1, after=2,
    )
    b.para(
        "Aucun privilège DROP, CREATE, ALTER, GRANT ni FILE : le compte lit et modifie les "
        "données, jamais le schéma. Deux refus ont été provoqués volontairement :",
        size=9.5, align=2, after=1.5,
    )
    t = b.table(len(D.REFUS) + 1, 3, [6200, 4200, 7000])
    for i, h in enumerate(["Commande exécutée", "Réponse", "Effet constaté"]):
        cellule(b, t, 0, i, h, bold=True, size=7.5)
    for r, (commande, reponse, effet) in enumerate(D.REFUS, start=1):
        cellule(b, t, r, 0, commande, size=7.2, mono=True)
        cellule(b, t, r, 1, reponse, size=7.2, mono=True)
        cellule(b, t, r, 2, effet, size=7.5)
    b.para(
        "Après ces refus, la table historique est intacte et contient toujours 9 lignes. "
        "Preuve : preuves/compte_sql.txt.",
        size=9.5, align=2, before=1, after=1.5,
    )

    # ---------------- 4. Sauvegarde ----------------
    b.heading("4. Sauvegarde")
    b.para(
        "mysqldump -u root --socket=… --single-transaction --routines --triggers "
        "tp3_conventions > preuves/tp3_conventions.sql",
        size=8.2, align=2, before=1, after=2,
    )
    b.para(
        f"Code de sortie 0. Le fichier produit mesure {taille} octets ({lignes} lignes) et "
        f"porte l'empreinte SHA-256 {sha}. --single-transaction donne un instantané cohérent "
        "sans bloquer les écritures ; --routines et --triggers conservent les objets de "
        "programmation. Preuve : preuves/sauvegarde.txt.",
        size=9.5, align=2, after=1,
    )

    # ---------------- Page 2 ----------------
    b.page_break()

    # ---------------- 5. Restauration ----------------
    b.heading("5. Restauration vérifiée")
    b.para(
        "La sauvegarde est importée dans une base de test dédiée, "
        "tp3_conventions_restauration. Les neuf tables sont comptées dans la base source et "
        "dans la base restaurée :",
        size=9.5, align=2, after=1.5,
    )
    t = b.table(len(D.COMPTAGES) + 1, 4, [7000, 3300, 3300, 3800])
    for i, h in enumerate(["Table", "Source", "Restaurée", "Verdict"]):
        cellule(b, t, 0, i, h, bold=True, size=7.5, align=(3 if i else 0))
    for r, (nom, n) in enumerate(D.COMPTAGES, start=1):
        cellule(b, t, r, 0, nom, size=7.2, mono=True)
        cellule(b, t, r, 1, n, size=7.5, align=3)
        cellule(b, t, r, 2, n, size=7.5, align=3)
        cellule(b, t, r, 3, "OK", size=7.5, align=3)
    b.para(
        f"{total}/{total} tables identiques. Le test de perte supprime ensuite historique dans "
        "la base de test : le comptage répond « table absente » ; après réimport du dump, les "
        f"{total} tables redeviennent identiques. Une sauvegarde n'est donc déclarée fiable "
        "qu'après cette restauration. Preuve : preuves/restauration.txt.",
        size=9.5, align=2, before=1, after=1.5,
    )

    # ---------------- 6. Incident ----------------
    b.heading("6. Incident INC-001 et correction")
    incident = [
        ("Symptôme", "/api/sante répond 503 ; journal PHP : SQLSTATE[HY000] [2002] No such file or directory"),
        ("Cause", "DB_SOCKET recopié d'un ancien poste : le fichier socket n'existe plus et le socket est prioritaire sur host/port"),
        ("Reproduction", "renseigner un socket absent, démarrer le serveur, appeler /api/sante : 503 à chaque essai (3/3)"),
        ("Correction", "test -S sur le socket réel, puis sed sur DB_SOCKET ; /api/sante repasse à 200 sans modifier le code"),
        ("Prévention", "socket documenté dans .env.example, contrôle test -S avant démarrage, santé vérifiée après installation"),
    ]
    t = b.table(len(incident) + 1, 2, [2600, 14800])
    for i, h in enumerate(["Champ", "Valeur"]):
        cellule(b, t, 0, i, h, bold=True, size=7.5)
    for r, (champ, valeur) in enumerate(incident, start=1):
        cellule(b, t, r, 0, champ, size=7.5, bold=True)
        cellule(b, t, r, 1, valeur, size=7.5)
    b.para(
        "Le ticket complet, avec les étapes de reproduction, les réponses attendues et "
        "observées et les preuves, est dans ticket_incident.md. La reproduction et la "
        "correction sont rejouées dans preuves/incident_reproduction.txt.",
        size=9.5, align=2, before=1, after=1.5,
    )

    # ---------------- 7. Manques ----------------
    b.heading("7. Étapes manquantes du README")
    b.para(
        "Le README du TP4 a été suivi à la lettre. Quatre manques ont été relevés puis "
        "corrigés dans TP4_Architecture/README.md :",
        size=9.5, align=2, after=1.5,
    )
    t = b.table(len(D.MANQUES) + 1, 3, [6100, 5000, 6300])
    for i, h in enumerate(["Manque constaté", "Conséquence", "Correction apportée"]):
        cellule(b, t, 0, i, h, bold=True, size=7.5)
    for r, (manque, consequence, correction) in enumerate(D.MANQUES, start=1):
        cellule(b, t, r, 0, manque, size=7.5)
        cellule(b, t, r, 1, consequence, size=7.5)
        cellule(b, t, r, 2, correction, size=7.5)

    # ---------------- 8. Conclusion ----------------
    b.heading("8. Conclusion")
    b.para(
        "L'installation est reproductible : huit étapes, un compte dédié, une santé à 200. "
        "Les droits du compte sont prouvés par deux refus 1142. La sauvegarde est datée, "
        "mesurée et empreintée ; sa restauration rétablit "
        f"{total}/{total} tables après une perte volontaire. L'incident réseau est reproduit, "
        "expliqué et corrigé par la configuration, sans changement de code. Les quatre "
        "manques du README sont comblés : le déploiement peut être refait sur un poste vierge "
        "avec le seul README.",
        size=9.5, align=2, before=1, after=1,
    )
    b.note(
        "Détail : README.md (protocole), ticket_incident.md (INC-001), preuves/ (sorties "
        "réelles et dump)."
    )

    R.enregistrer_docx(
        doc,
        DOCX,
        "TP9 — Déploiement, compte SQL dédié et sauvegarde",
        "Projet informatique 2, L3 SIL",
        "OUSSOU Hermax, TCHEGNON Loïk, KANHONOU Ashley",
        "TP9 — installation, droits SQL, sauvegarde, restauration et incident",
    )


if __name__ == "__main__":
    build()
    print(f"DOCX : {DOCX}")
