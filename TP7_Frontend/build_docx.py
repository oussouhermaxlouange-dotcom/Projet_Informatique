#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construit la version DOCX du rapport TP7 avec le constructeur UNO partagé."""

from __future__ import annotations

import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE.parent / "outils"))

import rapport_uno as R  # noqa: E402
from rapport_uno import cellule  # noqa: E402

DOCX = RACINE / "interface_tp7.docx"
DATE = "19 novembre 2026"

SCENARIO = [
    ("1", "Ouvrir l'application", "Écran de connexion, badge « Service actif »", "Conforme"),
    ("2", "Connexion étudiante A", "« Mes demandes », 2 conventions", "« Bienvenue Sènami. », compteurs 1/0/0"),
    ("3", "Soumettre le formulaire vide", "422, message global et un par champ", "4 champs signalés"),
    ("4", "Déposer un intitulé contenant une balise", "201, statut En attente, balise en texte", "« Convention n° 7 enregistrée au statut En attente. »"),
    ("5", "Recharger la page (F5)", "Session conservée, convention 7 présente", "3 lignes, aucune exécution"),
    ("6", "Consulter la convention 7", "Écran de détail, balise toujours en texte", "« Convention n° 7 », En attente"),
    ("7", "Connexion responsable", "« Dossiers à traiter », 7 dossiers", "2 en attente, filtres et recherche"),
    ("8", "Décider sur la convention 2", "Écran de décision, résumé et motif", "Conforme"),
    ("9", "Refuser sans motif", "Message sous le champ, aucun appel réseau", "Message affiché"),
    ("10", "Saisir un motif puis refuser", "200, statut Refusée, motif conservé", "« Convention n° 2 : refusée. »"),
    ("11", "Décider sur la convention 7 puis valider", "200, statut Validée", "« Convention n° 7 : validée. »"),
    ("12", "Ouvrir la page de preuve des erreurs", "400, 401 et 500 rendus", "Conforme"),
    ("13", "Ouvrir la page de preuve XSS", "Deux charges en texte", "data-xss absent, 0 img"),
]

ERREURS = [
    ("400", "Corps JSON illisible", "« Le corps de la requête doit être un objet JSON valide. »"),
    ("401", "Session absente ou expirée", "« Authentification requise. » puis retour à la connexion ; « E-mail ou mot de passe incorrect. » à la connexion"),
    ("403", "Rôle ou propriétaire incorrect", "« Vous n'avez pas les droits pour cette action. »"),
    ("404", "Convention inconnue", "« Cette ressource est introuvable. »"),
    ("405", "Méthode non autorisée", "« Cette action n'est pas autorisée sur cette ressource. »"),
    ("409", "Décision déjà prise", "« Cette décision n'est plus possible… »"),
    ("422", "Validation serveur", "Message global + message sous chaque champ concerné"),
    ("500", "Panne interne", "« Une erreur interne est survenue… »"),
    ("503", "Base indisponible", "Badge « Service indisponible » et message dans la zone d'état"),
]

ACCESSIBILITE = [
    ("Étiquettes liées", "label for=… et id unique pour chacun des 7 champs ; aria-describedby vers l'aide et l'erreur ; aria-invalid=true si fautif."),
    ("Zone d'erreur", "Zone globale role=alert + aria-live=assertive ; une zone id=erreur-… par champ ; messages de réussite en role=status."),
    ("Décision", "Écran dédié sans dialogue : un refus sans motif est bloqué, le message s'affiche sous la zone de texte et le focus y est placé."),
    ("Clavier et structure", "Lien d'évitement, focus-visible sur tous les contrôles, navigation par boutons ; un seul h1 par écran, tableaux avec caption et th scope=col."),
    ("Couleur, langue et dates", "Statut écrit en toutes lettres ; lang=fr ; dates au format JJ/MM/AAAA ; aucun contenu externe."),
]


def build() -> None:
    doc, b = R.nouveau_document(
        "Projet informatique 2 — L3 SIL — TP7 : interface des demandes — 19/11/2026"
    )

    # ---------------- En-tête ----------------
    b.para("Projet informatique 2 — L3 SIL", size=9, align=3, after=1, line=100)
    b.para("Interface de gestion des demandes de stage", size=16, bold=True,
           align=3, after=1, line=100)
    b.para("Parcours, accessibilité, erreurs lisibles et rendu sécurisé", size=10.5,
           align=3, after=1, line=100)
    b.para(f"TP7 — Interface et intégration — {DATE}", size=10, align=3, after=0.5, line=100)
    b.para(
        "Groupe : OUSSOU Hermax – TCHEGNON Loïk – KANHONOU Ashley\n"
        "Encadreur : MAMA Tairou · Données fictives du TP3",
        size=9, align=3, after=4, line=105,
    )

    # ---------------- 1. Objet ----------------
    b.heading("1. Objet")
    b.para(
        "Relier une interface Web accessible à l'API des demandes. L'interface est servie par "
        "la même application que l'API, dans TP4_Architecture/public/ : même origine, donc même "
        "cookie de session, sans duplication ni configuration CORS. Six écrans couvrent deux "
        "rôles : l'étudiante dépose et suit ses conventions, le responsable pédagogique recherche, "
        "filtre et instruit les dossiers, puis valide ou refuse avec motif. Toutes les écritures "
        "passent par fetch ; aucun rendu n'utilise innerHTML.",
        size=10, align=2, after=1.5,
    )

    # ---------------- 2. Parcours ----------------
    b.heading("2. Parcours des deux rôles")
    parcours = [
        ("Étudiante", "Connexion → Mes demandes → Nouvelle convention → Détail",
         "Saisir entreprise, intitulé et deux dates ; soumettre la convention ; lire statut, "
         "date de décision ou motif de refus. Une convention SOUMISE part vers le responsable."),
        ("Responsable", "Connexion → Dossiers à traiter → Décision → Détail",
         "Rechercher et filtrer par statut ; valider, ou refuser avec motif obligatoire ; la "
         "décision revient dans le détail de l'étudiante et reste conservée."),
    ]
    t = b.table(len(parcours) + 1, 3, [2100, 4500, 10800])
    for i, h in enumerate(["Rôle", "Écrans", "Actions et échanges"]):
        cellule(b, t, 0, i, h, bold=True, size=8)
    for r, ligne in enumerate(parcours, start=1):
        for c, val in enumerate(ligne):
            cellule(b, t, r, c, val, size=8, bold=(c == 0))
    b.image(RACINE / "parcours.png", largeur=14000, hauteur=7000)
    b.note("Figure 1 — Parcours des deux rôles : écrans, actions et échanges "
           "(source : parcours.svg).")

    # ---------------- 3. Accessibilité ----------------
    b.heading("3. Formulaire accessible")
    t = b.table(len(ACCESSIBILITE) + 1, 2, [2700, 14700])
    for i, h in enumerate(["Point", "Mise en œuvre"]):
        cellule(b, t, 0, i, h, bold=True, size=8)
    for r, (point, texte) in enumerate(ACCESSIBILITE, start=1):
        cellule(b, t, r, 0, point, size=8, bold=True)
        cellule(b, t, r, 1, texte, size=8)
    b.note(
        "Les formulaires portent novalidate : la validation est faite par le serveur et les "
        "messages affichés sont ceux de l'API (erreurs 422 réelles)."
    )

    # ---------------- Page 2 ----------------
    b.page_break()

    # ---------------- 4. Erreurs ----------------
    b.heading("4. Gestion lisible des erreurs")
    t = b.table(len(ERREURS) + 1, 3, [900, 4500, 12000])
    for i, h in enumerate(["Code", "Déclencheur", "Affichage pour l'utilisateur"]):
        cellule(b, t, 0, i, h, bold=True, size=8, align=(3 if i == 0 else 0))
    for r, (code, declencheur, affichage) in enumerate(ERREURS, start=1):
        cellule(b, t, r, 0, code, size=8, align=3)
        cellule(b, t, r, 1, declencheur, size=8)
        cellule(b, t, r, 2, affichage, size=8)
    b.note(
        "assets/api.js traduit le statut et le corps JSON en titre + liste de détails. Preuves : "
        "12_erreurs_400_401_500.png et 03_erreurs_422.png."
    )

    # ---------------- 5. Rendu sécurisé ----------------
    b.heading("5. Rendu sécurisé avec textContent")
    b.para(
        "Chaque valeur reçue de l'API est insérée dans un nœud créé par document.createElement "
        "puis affectée à textContent ; assets/rendu.js ne contient aucun innerHTML. Deux charges "
        "hostiles ont été envoyées : <img src=x onerror=…> et "
        "<script>document.body.dataset.xss=…</script>. Résultat mesuré sur /preuves/xss.html : "
        "attribut data-xss absent, 0 élément img créé, 0 élément script dans le tableau. Les "
        "balises apparaissent en texte dans le tableau de l'étudiante, l'écran de détail et les "
        "cartes du responsable. Détail : preuves/xss_verification.txt et DOM complet xss_dom.html.",
        size=10, align=2, after=1.5,
    )

    # ---------------- 6. Scénario ----------------
    b.heading("6. Scénario de bout en bout")
    t = b.table(len(SCENARIO) + 1, 4, [700, 5400, 6800, 4500])
    for i, h in enumerate(["#", "Action", "Attendu", "Observé"]):
        cellule(b, t, 0, i, h, bold=True, size=7.8,
                align=(3 if i == 0 else 0))
    for r, (num, action, attendu, observe) in enumerate(SCENARIO, start=1):
        cellule(b, t, r, 0, num, size=7.6, align=3)
        cellule(b, t, r, 1, action, size=7.6)
        cellule(b, t, r, 2, attendu, size=7.6)
        cellule(b, t, r, 3, observe, size=7.6)
    b.note(
        "Scénario complet, protocole et commandes de rejeu : scenario.md. Après l'étape 11, la "
        "base contient 7 conventions : la 7 est VALIDEE, la 2 est REFUSEE avec motif."
    )

    # ---------------- 7. Preuves ----------------
    b.heading("7. Preuves et reproductibilité")
    for texte in (
        "13 captures d'écran réelles dans preuves/, de la connexion au test XSS.",
        "preuves/xss_verification.txt : contrôle chiffré du rendu ; xss_dom.html : DOM produit "
        "par Chrome.",
        "Interface : public/index.html, assets/app.css, api.js, rendu.js, app.js.",
        "Rejouer : cd TP4_Architecture && php -S 127.0.0.1:8084 -t public public/index.php, "
        "puis ouvrir http://127.0.0.1:8084/.",
        "Comptes : sena.houngbo@univ.test et responsable.pedago@univ.test, mot de passe "
        "Demo1234!.",
    ):
        b.para("• " + texte, size=9.5, align=2, after=0.8, line=108)

    R.enregistrer_docx(
        doc,
        DOCX,
        "TP7 — Interface des demandes de stage",
        "Projet informatique 2, L3 SIL",
        "OUSSOU Hermax, TCHEGNON Loïk, KANHONOU Ashley",
        "TP7 — interface, accessibilité, erreurs et rendu sécurisé",
    )


if __name__ == "__main__":
    build()
    print(f"DOCX : {DOCX}")
