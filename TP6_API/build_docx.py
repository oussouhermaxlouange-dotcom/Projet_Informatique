#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construit le rapport TP6 en DOCX, noir et blanc, via l'API UNO de LibreOffice.

Le HTML sert au PDF (Chrome) ; ce script produit la version éditable en
réutilisant le même constructeur que le rapport TP3 (Times New Roman, tableaux
à bordures noires, pied de page numéroté). Aucune ligne de tableau n'est
autorisée à se couper entre deux pages.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import uno

FONT = "Times New Roman"
MONO = "Liberation Mono"
PARA_BREAK = uno.getConstantByName("com.sun.star.text.ControlCharacter.PARAGRAPH_BREAK")
PAGE_BREAK = uno.Enum("com.sun.star.style.BreakType", "PAGE_BEFORE")
BLACK = 0x000000

PAGE_W, PAGE_H = 21000, 29700
MARGIN_LR, MARGIN_TB = 1800, 1600
CONTENT_W = PAGE_W - 2 * MARGIN_LR

RACINE = Path(__file__).resolve().parent
SORTIES = RACINE / "preuves" / "sorties.tsv"
ETAT = RACINE / "preuves" / "etat_base.tsv"

DATE = "18 novembre 2026"

SIX_CAS = ["S5", "S6", "S7", "S8", "S9", "S10"]


# --------------------------------------------------------------------------- #
# Accès aux preuves
# --------------------------------------------------------------------------- #
def lire_tsv(chemin: Path) -> list[dict[str, str]]:
    lignes = chemin.read_text(encoding="utf-8").splitlines()
    entetes = lignes[0].split("\t")
    return [dict(zip(entetes, ligne.split("\t"))) for ligne in lignes[1:] if ligne.strip()]


def extrait(reponse: str) -> str:
    """Réponse compacte pour le tableau : JSON valide et lisible."""
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


# --------------------------------------------------------------------------- #
# Connexion UNO (soffice écoute sur le port 2002)
# --------------------------------------------------------------------------- #
def connecter():
    local = uno.getComponentContext()
    resolver = local.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", local
    )
    ctx = resolver.resolve(
        "uno:socket,host=127.0.0.1,port=2002;urp;StarOffice.ComponentContext"
    )
    return ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.frame.Desktop", ctx
    )


def demarrer_soffice() -> subprocess.Popen:
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice is None:
        raise SystemExit("LibreOffice introuvable : DOCX non généré.")
    profil = "file:///tmp/opencode/lo_profile_tp6_uno"
    proc = subprocess.Popen(
        [
            soffice,
            "--headless",
            "--norestore",
            "--invisible",
            f"-env:UserInstallation={profil}",
            "--accept=socket,host=127.0.0.1,port=2002;urp;",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(60):
        try:
            return proc, connecter()
        except Exception:
            time.sleep(0.25)
    proc.terminate()
    raise SystemExit("LibreOffice n'a pas ouvert le port UNO 2002.")


# --------------------------------------------------------------------------- #
# Mise en page
# --------------------------------------------------------------------------- #
def line_spacing(height=115):
    ls = uno.createUnoStruct("com.sun.star.style.LineSpacing")
    ls.Mode = 0
    ls.Height = height
    return ls


def set_page(doc):
    page = doc.StyleFamilies.getByName("PageStyles").getByName("Standard")
    page.Width = PAGE_W
    page.Height = PAGE_H
    page.LeftMargin = MARGIN_LR
    page.RightMargin = MARGIN_LR
    page.TopMargin = MARGIN_TB
    page.BottomMargin = MARGIN_TB
    page.HeaderIsOn = False
    page.FooterIsOn = True
    page.FooterHeight = 800
    page.FooterBodyDistance = 450
    return page


def add_footer(doc, page):
    footer = page.FooterText
    fc = footer.createTextCursor()
    fc.CharFontName = FONT
    fc.CharHeight = 8
    fc.CharColor = BLACK
    fc.ParaAdjust = 3
    footer.insertString(
        fc,
        "Projet informatique 2 — L3 SIL — TP6 : API des demandes — 18/11/2026 — page ",
        False,
    )
    pn = doc.createInstance("com.sun.star.text.TextField.PageNumber")
    pn.NumberingType = 4
    footer.insertTextContent(fc, pn, False)
    footer.insertString(fc, " sur ", False)
    pc = doc.createInstance("com.sun.star.text.TextField.PageCount")
    pc.NumberingType = 4
    footer.insertTextContent(fc, pc, False)


class Builder:
    def __init__(self, doc):
        self.doc = doc
        self.text = doc.getText()
        self.cur = self.text.createTextCursor()

    def para(self, txt="", size=10, bold=False, italic=False, align=0,
             before=0, after=2, line=115, keep=False):
        c = self.cur
        c.ParaAdjust = align
        c.ParaTopMargin = int(before * 100)
        c.ParaBottomMargin = int(after * 100)
        c.ParaLineSpacing = line_spacing(line)
        c.CharFontName = FONT
        c.CharHeight = size
        c.CharWeight = 150 if bold else 100
        c.CharPosture = 2 if italic else 0
        c.CharColor = BLACK
        try:
            c.ParaKeepTogether = keep
            c.ParaKeepWithNext = keep
        except Exception:
            pass
        parts = str(txt).split("\n")
        for i, part in enumerate(parts):
            self.text.insertString(c, part, False)
            if i < len(parts) - 1:
                self.text.insertControlCharacter(c, PARA_BREAK, False)
        self.text.insertControlCharacter(c, PARA_BREAK, False)

    def heading(self, txt):
        self.para(txt, size=11, bold=True, before=6, after=2, line=100, keep=True)

    def note(self, txt):
        self.para(txt, size=8, italic=True, align=2, before=1, after=3, line=105)

    def page_break(self):
        self.cur.BreakType = PAGE_BREAK
        self.text.insertControlCharacter(self.cur, PARA_BREAK, False)
        self.cur.BreakType = uno.Enum("com.sun.star.style.BreakType", "NONE")

    def table(self, rows, cols, widths, header=True, font=8.4,
              header_font=8.4, align_center_cols=()):
        t = self.doc.createInstance("com.sun.star.text.TextTable")
        t.initialize(rows, cols)
        self.text.insertTextContent(self.cur, t, False)

        total = sum(widths)
        seps = []
        acc = 0
        for w in widths[:-1]:
            acc += w
            s = uno.createUnoStruct("com.sun.star.text.TableColumnSeparator")
            s.Position = int(round(acc / total * 10000))
            s.IsVisible = True
            seps.append(s)
        t.TableColumnSeparators = tuple(seps)

        b = uno.createUnoStruct("com.sun.star.table.BorderLine")
        b.Color = BLACK
        b.InnerLineWidth = 0
        b.OuterLineWidth = 15
        b.LineDistance = 0
        tb = uno.createUnoStruct("com.sun.star.table.TableBorder")
        for name in ("TopLine", "BottomLine", "LeftLine", "RightLine",
                     "HorizontalLine", "VerticalLine"):
            setattr(tb, name, b)
        for name in ("IsTopLineValid", "IsBottomLineValid", "IsLeftLineValid",
                     "IsRightLineValid", "IsHorizontalLineValid", "IsVerticalLineValid"):
            setattr(tb, name, True)
        t.TableBorder = tb
        t.CollapsingBorders = True
        t.LeftMargin = 60
        t.RightMargin = 60
        t.TopMargin = 40
        t.BottomMargin = 55
        t.Split = True
        if header:
            try:
                t.RepeatHeadline = True
                t.HeaderRowCount = 1
            except Exception:
                pass

        for r in range(rows):
            try:
                row = t.getRows().getByIndex(r)
                row.IsAutoHeight = True
                row.Height = 0
                row.IsSplitAllowed = False   # aucune ligne coupée entre deux pages
            except Exception:
                pass
            for c in range(cols):
                self.fill_cell(
                    t.getCellByPosition(c, r), "",
                    size=(header_font if header and r == 0 else font),
                    bold=(header and r == 0),
                    align=(3 if c in align_center_cols else 0),
                )
        return t

    def fill_cell(self, cell, txt, size=8.4, bold=False, italic=False, align=0,
                  mono=False):
        cell.BackTransparent = True
        try:
            cell.VertOrient = 1
            cell.TopBorderDistance = 25
            cell.BottomBorderDistance = 40
            cell.LeftBorderDistance = 70
            cell.RightBorderDistance = 70
        except Exception:
            pass
        cell.String = ""
        c = cell.getText().createTextCursor()
        c.CharFontName = MONO if mono else FONT
        c.CharHeight = size
        c.CharWeight = 150 if bold else 100
        c.CharPosture = 2 if italic else 0
        c.CharColor = BLACK
        c.ParaAdjust = align
        c.ParaTopMargin = 0
        c.ParaBottomMargin = 0
        c.ParaLineSpacing = line_spacing(100)
        parts = str(txt).split("\n")
        for i, part in enumerate(parts):
            cell.getText().insertString(c, part, False)
            if i < len(parts) - 1:
                cell.getText().insertControlCharacter(c, PARA_BREAK, False)


def cellule(b, table, r, col, txt, bold=False, align=0, size=8.4, mono=False):
    b.fill_cell(
        table.getCellByPosition(col, r), txt,
        size=size, bold=bold, align=align, mono=mono,
    )
    try:
        row = table.getRows().getByIndex(r)
        row.IsAutoHeight = True
        row.Height = 0
    except Exception:
        pass


# --------------------------------------------------------------------------- #
# Construction
# --------------------------------------------------------------------------- #
def build(path_docx: Path) -> None:
    try:
        desktop = connecter()
        lance = None
    except Exception:
        lance, desktop = demarrer_soffice()

    try:
        cas = {ligne["numero"]: ligne for ligne in lire_tsv(SORTIES)}
        etat = lire_tsv(ETAT)
        demandes = [ligne for ligne in etat if re.fullmatch(r"\d+", ligne.get("id", ""))]
        historique = next(
            (ligne.get("etudiant_id", "?") for ligne in etat
             if ligne.get("id") == "lignes_historique"),
            "?",
        )
        total = len(cas)
        conformes = sum(1 for ligne in cas.values() if ligne["conforme"] == "OUI")

        doc = desktop.loadComponentFromURL("private:factory/swriter", "_blank", 0, ())
        page = set_page(doc)
        add_footer(doc, page)
        b = Builder(doc)

        # ---------------- En-tête ----------------
        b.para("Projet informatique 2 — L3 SIL", size=9, align=3, after=1, line=100)
        b.para("API des demandes de stage", size=16, bold=True, align=3, after=1, line=100)
        b.para("Implémentation, contrôles et preuves d'exécution", size=10.5, align=3, after=1, line=100)
        b.para(f"TP6 — {DATE}", size=10, align=3, after=0.5, line=100)
        b.para(
            "Groupe : OUSSOU Hermax – TCHEGNON Loïk – KANHONOU Ashley\n"
            "Encadreur : MAMA Tairou · Dépôt Git : local (commits TP1 à TP3)",
            size=9, align=3, after=4, line=105,
        )

        # ---------------- 1. Objet ----------------
        b.heading("1. Objet")
        b.para(
            "Implémentation de la création, de la lecture et de la validation d'une demande, avec "
            "contrôles côté serveur. Sur "
            f"{total} cas exécutés contre MySQL 8.0.46 et l'API réelle, {conformes} sont conformes à "
            "l'attendu écrit avant le test. La base tp3_conventions est rechargée depuis le jeu "
            "d'essai TP3 avant chaque exécution, ce qui rend la manipulation reproductible.",
            size=10, align=2, after=1.5,
        )

        # ---------------- 2. Routes ----------------
        b.heading("2. Routes implémentées")
        routes = [
            ("GET", "/api/sante", "Public", "200", "503"),
            ("POST", "/api/connexion", "Public", "200", "400, 401, 403, 422"),
            ("POST", "/api/deconnexion", "Session", "200", "401"),
            ("GET", "/api/moi", "Session", "200", "401"),
            ("GET", "/api/demandes", "Session (selon rôle)", "200", "401, 403"),
            ("GET", "/api/demandes/{id}", "Session (selon rôle)", "200", "401, 403, 404"),
            ("POST", "/api/demandes", "Étudiant", "201", "400, 401, 403, 422"),
            ("PATCH", "/api/demandes/{id}/statut", "Responsable", "200",
             "400, 401, 403, 404, 409, 422"),
        ]
        t = b.table(len(routes) + 1, 5, [1300, 4600, 3300, 1200, 7000])
        for i, h in enumerate(["Méthode", "Chemin", "Rôle", "Succès", "Erreurs"]):
            cellule(b, t, 0, i, h, bold=True, size=8)
        for r, ligne in enumerate(routes, start=1):
            for c, val in enumerate(ligne):
                cellule(b, t, r, c, val, align=(3 if c in (0, 3) else 0), size=8)
        b.note(
            "Contrat complet (corps, champs, codes d'erreur) : TP4_Architecture/docs/contrat_api.md. "
            "Les routes /api/moi et /api/demandes/{id} complètent le contrat du TP4."
        )

        # ---------------- 3. Transitions ----------------
        b.heading("3. Transitions autorisées")
        transitions = [
            ("BROUILLON → SOUMISE", "Étudiant", "Soumission de la demande"),
            ("SOUMISE → VALIDEE", "Responsable", "Décision favorable"),
            ("SOUMISE → REFUSEE", "Responsable", "Motif obligatoire (422 sinon)"),
        ]
        t = b.table(len(transitions) + 1, 3, [5600, 2800, 9000])
        for i, h in enumerate(["Transition", "Qui", "Règle"]):
            cellule(b, t, 0, i, h, bold=True, size=8)
        for r, ligne in enumerate(transitions, start=1):
            for c, val in enumerate(ligne):
                cellule(b, t, r, c, val, size=8)
        b.note(
            "Table des transitions : src/Services/DemandeService.php. VALIDEE et REFUSEE sont "
            "terminales : toute autre transition est refusée avec 409."
        )

        # ---------------- 4. Six cas ----------------
        b.heading("4. Cas testés (les six cas exigés, sorties réelles)")
        b.para(
            "Chaque ligne reprend l'attendu écrit avant exécution, le code réellement renvoyé et un "
            "extrait du corps JSON. Les réponses complètes sont dans preuves/sorties.tsv.",
            size=9.5, align=2, after=1.5,
        )
        lignes = [cas[n] for n in SIX_CAS if n in cas]
        t = b.table(len(lignes) + 1, 5, [700, 3700, 1400, 1400, 10200])
        for i, h in enumerate(["N°", "Cas", "Attendu", "Obtenu", "Réponse de l'API (extrait)"]):
            cellule(b, t, 0, i, h, bold=True, size=7.8,
                    align=(3 if i in (0, 2, 3) else 0))
        for r, ligne in enumerate(lignes, start=1):
            cellule(b, t, r, 0, ligne["numero"], size=7.6, align=3)
            cellule(b, t, r, 1, ligne["cas"], size=7.6)
            cellule(b, t, r, 2, ligne["attendu"], size=7.6, align=3)
            cellule(b, t, r, 3, ligne["obtenu"], size=7.6, align=3)
            cellule(b, t, r, 4, extrait(ligne["reponse"]), size=6.8, mono=True)
        b.note(
            f"Les {total} cas du script sont listés au §8 et dans preuves/sorties.tsv "
            f"({total} cas, {conformes} conformes), avec les corps JSON complets. "
            "Le script tests_api.sh recharge la base avant chaque exécution."
        )

        # ---------------- Page 2 ----------------
        b.page_break()

        # ---------------- 5. État de la base ----------------
        b.heading("5. État de la base après les cas")
        t = b.table(len(demandes) + 1, 5, [2000, 2000, 2700, 7100, 3600])
        for i, h in enumerate(["Demande", "Étudiant", "Statut", "Motif de refus", "Décision"]):
            cellule(b, t, 0, i, h, bold=True, size=8,
                    align=(3 if i in (0, 1, 2) else 0))
        for r, ligne in enumerate(demandes, start=1):
            cellule(b, t, r, 0, ligne["id"], size=8, align=3)
            cellule(b, t, r, 1, ligne["etudiant_id"], size=8, align=3)
            cellule(b, t, r, 2, ligne["statut"], size=8, align=3)
            cellule(b, t, r, 3, "—" if ligne["motif_refus"] in ("NULL", "") else ligne["motif_refus"], size=8)
            cellule(b, t, r, 4, "—" if ligne["date_decision"] in ("NULL", "") else ligne["date_decision"], size=8)
        b.note(
            f"Lignes dans historique après les cas : {historique}. La demande 7 a été créée puis "
            "validée pendant le test ; la demande 2 a été refusée avec motif."
        )

        # ---------------- 6. Sécurité ----------------
        b.heading("6. Sécurité et cohérence")
        securite = [
            ("Mots de passe",
             "password_verify contre un hash password_hash (bcrypt) ; message identique pour "
             "compte inconnu et mot de passe faux."),
            ("Session",
             "session_regenerate_id(true) à chaque connexion réussie ; cookie HttpOnly, "
             "SameSite=Lax ; identifiant inconnu refusé (use_strict_mode)."),
            ("Autorisation",
             "Rôle contrôlé côté serveur à chaque requête ; un étudiant ne voit et ne traite que "
             "ses demandes (403 sinon)."),
            ("SQL",
             "Requêtes préparées avec paramètres liés, émulation désactivée ; aucun SQL dans les "
             "contrôleurs."),
            ("Transaction",
             "Statut et historique dans une seule transaction ; rollback complet si une étape "
             "échoue (vérifié par un test dédié)."),
            ("Erreurs",
             "Le détail technique va dans le journal serveur ; le client reçoit un message neutre "
             "et un code cohérent (400, 401, 403, 404, 409, 422, 503)."),
        ]
        t = b.table(len(securite) + 1, 2, [2700, 14700])
        for i, h in enumerate(["Point", "Mise en œuvre"]):
            cellule(b, t, 0, i, h, bold=True, size=8)
        for r, ligne in enumerate(securite, start=1):
            for c, val in enumerate(ligne):
                cellule(b, t, r, c, val, size=8, bold=(c == 0))

        # ---------------- 7. Justification ----------------
        b.heading("7. Justification (preuve de travail)")
        b.para(
            "Les six cas exigés ont été écrits avant exécution, puis joués sur une base rechargée. "
            "Toutes les réponses sont conformes. Le rollback est vérifié séparément par "
            "tests/test_domain.php : une exception provoquée après l'UPDATE laisse le statut et le "
            "motif inchangés. Le code de l'API reste dans TP4_Architecture/ (couches contrôleur, "
            "service, dépôt) ; les preuves et le script de rejeu sont regroupés dans TP6_API/.",
            size=10, align=2, after=1.5,
        )
        b.para(
            "Reproduire : mysql … < TP3_Modele_donnees/001_schema.sql puis 002_seed.sql, puis "
            "cd TP6_API && ./tests_api.sh.",
            size=8.5, italic=True, align=2, after=2,
        )

        # ---------------- 8. Preuves ----------------
        b.heading("8. Preuves et reproductibilité")
        b.para(
            "tests_api.sh recharge la base, démarre l'API et rejoue les "
            f"{total} cas ; les sorties sont écrites dans preuves/sorties.tsv (un cas par ligne, "
            "corps JSON complets). Le tableau ci-dessous en donne la synthèse.",
            size=9.5, align=2, after=1.5,
        )
        t = b.table(total + 1, 6, [700, 5600, 4700, 2100, 2100, 2200])
        for i, h in enumerate(["N°", "Cas", "Requête", "Attendu", "Obtenu", "Conforme"]):
            cellule(b, t, 0, i, h, bold=True, size=7.8,
                    align=(3 if i in (0, 3, 4, 5) else 0))
        for r, (numero, ligne) in enumerate(cas.items(), start=1):
            cellule(b, t, r, 0, numero, size=7.4, align=3)
            cellule(b, t, r, 1, ligne["cas"], size=7.4)
            cellule(b, t, r, 2, ligne["requete"], size=7.4, mono=True)
            cellule(b, t, r, 3, ligne["attendu"], size=7.4, align=3)
            cellule(b, t, r, 4, ligne["obtenu"], size=7.4, align=3)
            cellule(b, t, r, 5, ligne["conforme"], size=7.4, align=3)
        b.note(
            "Capture réelle de /api/sante dans un navigateur : preuves/capture_api.png. "
            "Base après les cas : preuves/etat_base.tsv."
        )

        # ---------------- Propriétés et sauvegarde ----------------
        try:
            dp = doc.getDocumentProperties()
            dp.Title = "TP6 — API des demandes de stage"
            dp.Subject = "Projet informatique 2, L3 SIL"
            dp.Author = "OUSSOU Hermax, TCHEGNON Loïk, KANHONOU Ashley"
            dp.Description = "TP6 — API des demandes : rapport et preuves"
        except Exception:
            pass

        p = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
        p.Name = "FilterName"
        p.Value = "MS Word 2007 XML"
        doc.storeToURL("file://" + os.path.abspath(path_docx), (p,))
        doc.close(True)
        print("DOCX :", Path(path_docx).name)
    finally:
        if lance is not None:
            try:
                desktop.terminate()
            except Exception:
                pass
            lance.wait(timeout=15)


if __name__ == "__main__":
    build(Path(sys.argv[1]) if len(sys.argv) > 1 else RACINE / "api_demandes.docx")
