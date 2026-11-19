#!/usr/bin/env python3
"""Génère le rapport TP7 (HTML, PDF, DOCX) depuis les preuves conservées.

Entrées  : preuves/xss_verification.txt, scenario.md, captures PNG
Sorties  : interface_tp7.html, interface_tp7.pdf (Chrome), interface_tp7.docx (UNO)
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
PREUVES = RACINE / "preuves"
XSS = PREUVES / "xss_verification.txt"
HTML = RACINE / "interface_tp7.html"
PDF = RACINE / "interface_tp7.pdf"
DOCX = RACINE / "interface_tp7.docx"

DATE = "19 novembre 2026"

SCENARIO = [
    ("1", "Ouvrir l'application", "Écran de connexion, badge « Service actif »", "Conforme", "01_connexion.png"),
    ("2", "Connexion étudiante A", "« Mes demandes », 2 conventions du jeu d'essai", "« Bienvenue Sènami. », compteurs 1/0/0", "02_etudiante.png"),
    ("3", "Soumettre le formulaire vide", "422, message global et un message par champ", "« Données invalides. », 4 champs", "03_erreurs_422.png"),
    ("4", "Déposer un intitulé contenant une balise", "201, statut En attente, balise affichée en texte", "« Convention n° 7 enregistrée au statut En attente. »", "04_demande_creee.png"),
    ("5", "Recharger la page (F5)", "Session conservée, convention 7 présente", "3 lignes, aucune exécution", "05_persistance.png"),
    ("6", "Cliquer « Consulter » sur la convention 7", "Écran de détail, balise toujours en texte", "« Convention n° 7 », statut En attente", "06_detail.png"),
    ("7", "Connexion responsable", "« Dossiers à traiter », 7 dossiers", "2 en attente, filtres et recherche", "07_responsable.png"),
    ("8", "Cliquer « Décider » sur la convention 2", "Écran de décision, résumé et zone de motif", "Conforme", "08_decision.png"),
    ("9", "Refuser sans motif", "Message sous le champ, aucun appel réseau", "« Le motif doit contenir de 3 à 255 caractères. »", "09_refus_motif.png"),
    ("10", "Saisir un motif puis refuser", "200, statut Refusée, motif conservé", "« Convention n° 2 : refusée. », 1 en attente", "10_refus_enregistre.png"),
    ("11", "Cliquer « Décider » sur la convention 7 puis valider", "200, statut Validée", "« Convention n° 7 : validée. », 0 en attente", "11_validation.png"),
    ("12", "Ouvrir la page de preuve des erreurs", "400, 401 et 500 rendus par le composant commun", "Conforme", "12_erreurs_400_401_500.png"),
    ("13", "Ouvrir la page de preuve XSS", "Deux charges en texte, aucune balise interprétée", "data-xss absent, 0 img, 0 script", "13_xss.png"),
]

ERREURS = [
    ("400", "Corps JSON illisible", "« Le corps de la requête doit être un objet JSON valide. »"),
    ("401", "Session absente ou expirée", "« Authentification requise. » puis retour à la connexion ; « E-mail ou mot de passe incorrect. » à la connexion"),
    ("403", "Rôle ou propriétaire incorrect", "« Vous n'avez pas les droits pour cette action. »"),
    ("404", "Convention inconnue", "« Cette ressource est introuvable. »"),
    ("405", "Méthode non autorisée", "« Cette action n'est pas autorisée sur cette ressource. »"),
    ("409", "Décision déjà prise", "« Cette décision n'est plus possible… »"),
    ("422", "Validation serveur", "Message global + message sous chaque champ concerné"),
    ("500", "Panne interne", "« Une erreur interne est survenue. Réessayez dans un instant. »"),
    ("503", "Base indisponible", "Badge « Service indisponible » et message dans la zone d'état"),
]

ACCESSIBILITE = [
    ("Étiquettes liées", "Chaque champ a un label for=… et un id unique (email, mot-de-passe, entreprise, intitule, date-debut, date-fin, motif)."),
    ("Aide et erreurs", "aria-describedby relie le champ à son texte d'aide et à sa zone d'erreur ; aria-invalid=true sur le champ fautif."),
    ("Zone d'erreur", "Zone globale role=alert + aria-live=assertive ; une zone id=erreur-… par champ."),
    ("Messages de réussite", "role=status : annonce polie, sans interrompre la saisie."),
    ("Décision", "Écran dédié sans dialogue : un refus sans motif est bloqué, le message s'affiche sous la zone de texte et le focus y est placé."),
    ("Clavier", "Lien d'évitement, focus-visible sur tous les contrôles, navigation par boutons entre les six écrans."),
    ("Couleur", "Statut écrit en toutes lettres ; la couleur ne fait que renforcer."),
    ("Structure et langue", "Un seul h1 par écran, sections h2, tableaux avec caption et th scope=col ; lang=fr, dates JJ/MM/AAAA."),
]


def lire_xss() -> dict[str, str]:
    """Relit la vérification XSS pour ne pas recopier les chiffres à la main."""
    valeurs = {"data_xss": "?", "images": "?", "scripts": "?"}
    if not XSS.exists():
        return valeurs
    for ligne in XSS.read_text(encoding="utf-8").splitlines():
        if "data-xss sur <body>" in ligne:
            valeurs["data_xss"] = "absent" if "absent" in ligne.lower() else "présent"
        elif "Éléments <img>" in ligne:
            m = re.search(r":\s*(\d+)", ligne)
            valeurs["images"] = m.group(1) if m else "?"
        elif "Éléments <script>" in ligne:
            m = re.search(r":\s*(\d+)", ligne)
            valeurs["scripts"] = m.group(1) if m else "?"
    return valeurs


def cellule(texte: str, classe: str = "") -> str:
    attribut = f' class="{classe}"' if classe else ""
    return f"<td{attribut}>{html.escape(str(texte))}</td>"


def construire_html() -> str:
    xss = lire_xss()

    lignes_scenario = "\n".join(
        "<tr>"
        + cellule(num, "c")
        + cellule(action)
        + cellule(attendu)
        + cellule(observe)
        + cellule(preuve, "mono")
        + "</tr>"
        for num, action, attendu, observe, preuve in SCENARIO
    )

    lignes_erreurs = "\n".join(
        "<tr>" + cellule(code, "c") + cellule(declencheur) + cellule(affichage) + "</tr>"
        for code, declencheur, affichage in ERREURS
    )

    lignes_accessibilite = "\n".join(
        "<tr>" + cellule(point, "gras") + cellule(mise_en_oeuvre) + "</tr>"
        for point, mise_en_oeuvre in ACCESSIBILITE
    )

    css = """
  @page { size: A4; margin: 15mm 15mm 13mm 15mm; }
  body { font-family: "Liberation Sans", Arial, sans-serif; font-size: 8.7pt; line-height: 1.26; color: #000; margin: 0; }
  .tete { text-align: center; margin-bottom: 6pt; }
  .tete .petit, .tete .date, .tete .groupe { font-size: 7.8pt; }
  .tete h1 { font-size: 15pt; margin: 2pt 0; font-family: Georgia, serif; font-weight: normal; }
  h2 { font-size: 9.8pt; margin: 8pt 0 3pt; page-break-after: avoid; }
  h2.saut-page { page-break-before: always; margin-top: 0; }
  p { margin: 0 0 3.5pt; text-align: justify; }
  .note { font-size: 7.2pt; font-style: italic; color: #333; }
  code { font-family: "Liberation Mono", monospace; font-size: 7.3pt; }
  td.mono { font-family: "Liberation Mono", monospace; font-size: 6.2pt; }
  table { width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 7.3pt; margin: 1pt 0 4pt; }
  th, td { border: 0.4pt solid #555; padding: 2pt 2.5pt; vertical-align: top; text-align: left;
           word-wrap: break-word; overflow-wrap: break-word; }
  th { font-weight: bold; background: #f0f0f0; }
  thead { display: table-header-group; }
  tr { page-break-inside: avoid; }
  td.c { text-align: center; }
  td.gras { font-weight: bold; }
  ul { margin: 1pt 0 4pt 14pt; padding: 0; }
  li { margin-bottom: 1.2pt; }
  footer { margin-top: 6pt; font-size: 7pt; color: #333; text-align: center; }
"""

    corps = f"""
<div class="tete">
  <div class="petit">Projet informatique 2 — L3 SIL</div>
  <h1>Interface de gestion des demandes de stage</h1>
  <div class="date">TP7 — Interface et intégration — {DATE}</div>
  <div class="groupe">Groupe : OUSSOU Hermax – TCHEGNON Loïk – KANHONOU Ashley<br>
  Encadreur : MAMA Tairou · Données fictives du TP3</div>
</div>

<h2>1. Objet</h2>
<p>Relier une interface Web accessible à l'API des demandes. L'interface est servie par la
même application que l'API, dans <code>TP4_Architecture/public/</code> : même origine, donc
même cookie de session, sans duplication ni configuration CORS. Six écrans couvrent deux
rôles : l'étudiante dépose et suit ses conventions, le responsable recherche, filtre et
instruit les dossiers avant de valider ou refuser avec motif. Toutes les écritures passent
par <code>fetch</code> ; aucun rendu n'utilise <code>innerHTML</code>.</p>

<h2>2. Parcours des deux rôles</h2>
<table>
  <colgroup><col style="width:17%"><col style="width:38%"><col style="width:45%"></colgroup>
  <thead><tr><th>Rôle</th><th>Écrans</th><th>Actions et échanges</th></tr></thead>
  <tbody>
    <tr><td class="gras">Étudiante</td>
        <td>Connexion → Mes demandes → Nouvelle convention → Détail</td>
        <td>Saisir entreprise, intitulé et deux dates ; soumettre la convention ; lire le statut,
            la date de décision ou le motif de refus. Une convention SOUMISE part vers le responsable.</td></tr>
    <tr><td class="gras">Responsable</td>
        <td>Connexion → Dossiers à traiter → Décision → Détail</td>
        <td>Rechercher et filtrer par statut ; valider, ou refuser avec un motif obligatoire ;
            la décision revient dans le détail de l'étudiante et reste conservée.</td></tr>
  </tbody>
</table>
<p style="text-align:center;margin:3pt 0 2pt;">
  <img src="parcours.png" alt="Parcours des deux rôles : étudiante et responsable"
       style="width:140mm;height:70mm;"></p>
<p class="note" style="text-align:center;">Figure 1 — Parcours des deux rôles : écrans, actions
et échanges (source : <code>parcours.svg</code>).</p>

<h2>3. Formulaire accessible</h2>
<table>
  <colgroup><col style="width:18%"><col style="width:82%"></colgroup>
  <thead><tr><th>Point</th><th>Mise en œuvre</th></tr></thead>
  <tbody>
{lignes_accessibilite}
  </tbody>
</table>
<p class="note">Les formulaires portent <code>novalidate</code> : la validation est faite par
le serveur et les messages affichés sont ceux de l'API, ce qui permet de montrer les erreurs
422 réelles plutôt que les bulles du navigateur.</p>

<h2 class="saut-page">4. Gestion lisible des erreurs</h2>
<table>
  <colgroup><col style="width:8%"><col style="width:30%"><col style="width:62%"></colgroup>
  <thead><tr><th>Code</th><th>Déclencheur</th><th>Affichage pour l'utilisateur</th></tr></thead>
  <tbody>
{lignes_erreurs}
  </tbody>
</table>
<p class="note"><code>assets/api.js</code> traduit le statut et le corps JSON en titre + liste
de détails ; le message du serveur est préféré quand il existe. Preuve :
<code>preuves/12_erreurs_400_401_500.png</code> et <code>03_erreurs_422.png</code>.</p>

<h2>5. Rendu sécurisé avec textContent</h2>
<p>Chaque valeur reçue de l'API est insérée dans un nœud créé par
<code>document.createElement</code> puis affectée à <code>textContent</code> ; le fichier
<code>assets/rendu.js</code> ne contient aucun <code>innerHTML</code>. Deux charges hostiles
ont été envoyées : <code>&lt;img src=x onerror=…&gt;</code> et
<code>&lt;script&gt;document.body.dataset.xss=…&lt;/script&gt;</code>. Résultat mesuré sur
<code>/preuves/xss.html</code> : attribut <code>data-xss</code> {xss['data_xss']},
{xss['images']} élément(s) <code>img</code> créé(s), {xss['scripts']} élément(s)
<code>script</code> dans le tableau. Les balises apparaissent en texte dans le tableau de
l'étudiante, l'écran de détail et les cartes du responsable. Détail : <code>preuves/xss_verification.txt</code>
et DOM complet <code>preuves/xss_dom.html</code>.</p>

<h2>6. Scénario de bout en bout</h2>
<table>
  <colgroup><col style="width:5%"><col style="width:26%"><col style="width:30%"><col style="width:21%"><col style="width:18%"></colgroup>
  <thead><tr><th>#</th><th>Action</th><th>Attendu</th><th>Observé</th><th>Preuve</th></tr></thead>
  <tbody>
{lignes_scenario}
  </tbody>
</table>
<p class="note">Scénario complet, protocole et commandes de rejeu : <code>scenario.md</code>.
Après l'étape 11, la base contient 7 conventions : la 7 est VALIDEE, la 2 est REFUSEE
avec le motif « Période incompatible avec le calendrier de la filière ».</p>

<h2>7. Preuves et reproductibilité</h2>
<ul>
  <li>13 captures d'écran réelles dans <code>preuves/</code>, de la connexion au test XSS.</li>
  <li><code>preuves/xss_verification.txt</code> : contrôle chiffré du rendu ; <code>xss_dom.html</code> : DOM produit par Chrome.</li>
  <li>Interface : <code>public/index.html</code>, <code>assets/app.css</code>, <code>api.js</code>, <code>rendu.js</code>, <code>app.js</code>.</li>
  <li>Rejouer : <code>cd TP4_Architecture &amp;&amp; php -S 127.0.0.1:8084 -t public public/index.php</code>, puis ouvrir <code>http://127.0.0.1:8084/</code>.</li>
  <li>Comptes : <code>sena.houngbo@univ.test</code> et <code>responsable.pedago@univ.test</code>, mot de passe <code>Demo1234!</code>.</li>
</ul>

<footer>Projet informatique 2 — L3 SIL — Interface des demandes de stage (TP7) — 19/11/2026</footer>
"""

    return f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8"><title>TP7 — Interface des demandes de stage</title>
<style>{css}</style></head><body>{corps}
</body></html>
"""


def main() -> int:
    HTML.write_text(construire_html(), encoding="utf-8")
    print(f"HTML : {HTML.name}")

    sys.path.insert(0, str(RACINE.parent / "outils"))
    import rapport_uno  # noqa: E402

    rapport = rapport_uno
    rapport.generer_pdf(HTML, PDF)
    print(f"PDF  : {PDF.name} — {rapport.compter_pages(PDF)} page(s)")

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
