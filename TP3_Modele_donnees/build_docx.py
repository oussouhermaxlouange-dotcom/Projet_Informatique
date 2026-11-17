#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construit le rapport TP3 (UML + modèle de données) en DOCX, noir et blanc."""

import os
import sys
import uno

from PIL import Image

FONT = "Times New Roman"
MONO = "Liberation Mono"
PARA_BREAK = uno.getConstantByName("com.sun.star.text.ControlCharacter.PARAGRAPH_BREAK")
PAGE_BREAK = uno.Enum("com.sun.star.style.BreakType", "PAGE_BEFORE")
ANCHOR_CHAR = uno.Enum("com.sun.star.text.TextContentAnchorType", "AS_CHARACTER")

PAGE_W, PAGE_H = 21000, 29700
MARGIN_LR, MARGIN_TB = 1800, 1600
CONTENT_W = PAGE_W - 2 * MARGIN_LR
BLACK = 0x000000


def connect():
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
        "Projet informatique 2 — L3 SIL — TP3 : UML et modélisation des données — 17/11/2026 — page ",
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
        self.para(txt, size=11, bold=True, before=5, after=2, line=100, keep=True)

    def caption(self, txt):
        self.para(txt, size=8, italic=True, align=3, before=1, after=3, line=100)

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

    def fill_cell(self, cell, txt, size=8.4, bold=False, italic=False, align=0):
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
        c.CharFontName = FONT
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

    def figure(self, path, width_mm, caption):
        w, h = Image.open(path).size
        g = self.doc.createInstance("com.sun.star.text.GraphicObject")
        g.GraphicURL = uno.systemPathToFileUrl(os.path.abspath(path))
        g.AnchorType = ANCHOR_CHAR
        g.Width = int(width_mm * 100)
        g.Height = int(width_mm * 100 * h / w)
        self.cur.ParaAdjust = 3
        self.text.insertTextContent(self.cur, g, False)
        self.text.insertControlCharacter(self.cur, PARA_BREAK, False)
        self.caption(caption)

    def code_block(self, text, size=7.0):
        t = self.doc.createInstance("com.sun.star.text.TextTable")
        t.initialize(1, 1)
        self.text.insertTextContent(self.cur, t, False)
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
        t.LeftMargin = 80
        t.RightMargin = 80
        t.TopMargin = 50
        t.BottomMargin = 60
        t.Split = False
        try:
            t.getRows().getByIndex(0).IsSplitAllowed = False
        except Exception:
            pass

        cell = t.getCellByPosition(0, 0)
        cell.BackTransparent = True
        cell.String = ""
        c = cell.getText().createTextCursor()
        c.CharFontName = MONO
        c.CharHeight = size
        c.CharColor = BLACK
        c.ParaAdjust = 0
        c.ParaTopMargin = 0
        c.ParaBottomMargin = 0
        c.ParaLineSpacing = line_spacing(92)
        lines = text.splitlines()
        for i, line in enumerate(lines):
            cell.getText().insertString(c, line.replace("\t", "    "), False)
            if i < len(lines) - 1:
                cell.getText().insertControlCharacter(c, PARA_BREAK, False)


def cell(b, table, r, col, txt, bold=False, align=0, size=8.4):
    b.fill_cell(table.getCellByPosition(col, r), txt, size=size, bold=bold, align=align)
    try:
        row = table.getRows().getByIndex(r)
        row.IsAutoHeight = True
        row.Height = 0
    except Exception:
        pass


def verification_output(path):
    raw = open(path, encoding="utf-8").read().splitlines()
    out = []
    for i, line in enumerate(raw):
        if i > 0 and line.startswith("+") and raw[i - 1].startswith("+"):
            out.append("")
        out.append(line)
    blocks = []
    current = []
    for line in out:
        if line == "":
            if current:
                blocks.append("\n".join(current))
                current = []
        else:
            current.append(line)
    if current:
        blocks.append("\n".join(current))
    return blocks


def build(path_odt, path_docx):
    desktop = connect()
    doc = desktop.loadComponentFromURL("private:factory/swriter", "_blank", 0, ())
    page = set_page(doc)
    add_footer(doc, page)
    b = Builder(doc)

    # ---------------- En-tête ----------------
    b.para("Projet informatique 2 — L3 SIL", size=9, align=3, after=1, line=100)
    b.para("UML et modélisation des données", size=17, bold=True, align=3, after=1, line=100)
    b.para(
        "Plateforme de suivi des conventions de stage et des soutenances",
        size=11, align=3, after=1, line=100,
    )
    b.para("TP3 — version 1.0 — 17 novembre 2026", size=10, align=3, after=0.5, line=100)
    b.para(
        "Groupe : [NOM 1], [NOM 2], [NOM 3], [NOM 4] — Dépôt Git : [url du dépôt partagé]",
        size=9, align=3, after=3, line=100,
    )

    # ---------------- 1. Cas d'utilisation ----------------
    b.heading("1. Diagramme de cas d'utilisation")
    b.para(
        "Le diagramme reprend les quatre acteurs du tableau blanc : l'étudiant, le responsable "
        "pédagogique, l'administrateur et le développeur. Chaque acteur est relié directement aux "
        "cas d'utilisation qu'il déclenche. Les décisions métier (confirmer, refuser) sont modélisées "
        "comme des extensions de « Gérer une demande » : elles ne se produisent que dans ce contexte. "
        "« Se connecter » est inclus par les cas principaux ; une légende rappelle que toute action "
        "suppose une session authentifiée (EF-01).",
        size=10, align=2, after=1.5,
    )
    b.figure("cas_utilisation.png", 140, "Figure 1 — Diagramme de cas d'utilisation (source : cas_utilisation.svg).")

    t = b.table(10, 4, [5200, 4200, 3400, 4200])
    for i, h in enumerate(["Cas d'utilisation", "Acteur principal", "Type", "Exigence"]):
        cell(b, t, 0, i, h, bold=True, align=(3 if i > 0 else 0))
    rows = [
        ("Gérer son compte", "Étudiant", "Direct", "EF-01"),
        ("Soumettre une demande", "Étudiant", "Direct", "EF-02"),
        ("Consulter une demande", "Étudiant", "Direct", "EF-06"),
        ("Gérer une demande", "Responsable", "Direct", "EF-03"),
        ("Confirmer une demande", "Responsable", "Extend", "EF-03"),
        ("Refuser une demande", "Responsable", "Extend", "EF-04"),
        ("Programmer une soutenance", "Responsable, Admin", "Direct", "EF-07"),
        ("Gérer les comptes", "Admin, Développeur", "Direct", "EF-08"),
        ("Se connecter", "Tous les acteurs", "Include", "EF-01"),
    ]
    for r, row in enumerate(rows, start=1):
        for c, val in enumerate(row):
            cell(b, t, r, c, val, align=(3 if c in (2, 3) else 0))
    b.note(
        "Lecture UML : un acteur n'est pas un cas d'utilisation. Les liens pleins sont des associations "
        "acteur–cas ; les flèches pointillées portent les stéréotypes « include » (comportement obligatoire) "
        "et « extend » (comportement conditionnel)."
    )

    # ---------------- 2. Classes ----------------
    b.heading("2. Diagramme de classes et multiplicités")
    b.para(
        "Neuf classes couvrent le périmètre : le compte (Utilisateur) et ses fiches spécialisées "
        "(Étudiant, Encadreur), l'entreprise d'accueil, la salle, la convention, les disponibilités de "
        "l'encadreur, la soutenance et le journal des décisions. Les multiplicités traduisent les règles "
        "du TP1 : un étudiant dépose plusieurs conventions, une convention est portée par un seul "
        "étudiant et une seule entreprise, et elle peut rester sans encadreur jusqu'à l'affectation.",
        size=10, align=2, after=1.5,
    )
    b.figure("classes.png", 148, "Figure 2 — Diagramme de classes (source : classes.puml).")

    t = b.table(12, 2, [6200, 10800])
    for i, h in enumerate(["Association et multiplicités", "Traduction dans le schéma relationnel"]):
        cell(b, t, 0, i, h, bold=True)
    rows = [
        ("Utilisateur 1 — 0..1 Étudiant", "etudiant.utilisateur_id NOT NULL UNIQUE (FK)"),
        ("Utilisateur 1 — 0..1 Encadreur", "encadreur.utilisateur_id NOT NULL UNIQUE (FK)"),
        ("Étudiant 1 — 0..* Convention", "convention.etudiant_id NOT NULL (FK)"),
        ("Entreprise 1 — 0..* Convention", "convention.entreprise_id NOT NULL (FK)"),
        ("Encadreur 0..1 — 0..* Convention", "convention.encadreur_id NULL (FK, affectation optionnelle)"),
        ("Encadreur 1 — 0..* Disponibilité", "disponibilite.encadreur_id NOT NULL (FK, ON DELETE CASCADE)"),
        ("Convention 1 — 0..1 Soutenance", "soutenance.convention_id NOT NULL UNIQUE (FK)"),
        ("Salle 1 — 0..* Soutenance", "soutenance.salle_id NOT NULL (FK)"),
        ("Encadreur 1 — 0..* Soutenance", "soutenance.encadreur_id NOT NULL ; FK composite avec convention"),
        ("Convention 1 — 0..* Historique", "historique.convention_id NOT NULL (FK, ON DELETE CASCADE)"),
        ("Utilisateur 1 — 0..* Historique", "historique.auteur_id NOT NULL (FK)"),
    ]
    for r, row in enumerate(rows, start=1):
        for c, val in enumerate(row):
            cell(b, t, r, c, val)
    b.note(
        "Règle appliquée : une association 1—0..* devient une clé étrangère du côté « plusieurs » ; une "
        "association 1—0..1 devient une clé étrangère déclarée UNIQUE. La clé étrangère composite "
        "(convention_id, encadreur_id) garantit que la soutenance est confiée à l'encadreur de la convention."
    )

    # ---------------- 3. Scénario ----------------
    b.heading("3. Scénario de validation — « Confirmer une convention »")
    b.para(
        "Le scénario part d'une convention au statut SOUMISE. Chaque échec renvoie un code HTTP distinct, "
        "ce qui rend le cas testable sans lire le code. Le refus suit le même chemin ; seule l'étape 5 "
        "change, le motif devenant obligatoire.",
        size=10, align=2, after=1.5,
    )
    t = b.table(8, 4, [700, 6200, 7200, 2900])
    for i, h in enumerate(["#", "Acteur ou composant", "Échec possible", "Code"]):
        cell(b, t, 0, i, h, bold=True, align=(3 if i in (0, 3) else 0))
    rows = [
        ("1", "Contrôleur — vérifier la session", "Session absente ou expirée", "401"),
        ("2", "ConventionRepository::findById", "Convention inexistante", "404"),
        ("3", "ConventionService — autorisation", "Rôle insuffisant (étudiant, développeur)", "403"),
        ("4", "ConventionService — état", "Transition interdite (déjà validée ou refusée)", "409"),
        ("5", "ConventionService — décision", "Date de décision absente ; refus sans motif", "400"),
        ("6", "Repository — UPDATE + INSERT historique", "Erreur SQL ou contrainte violée", "500 + rollback"),
        ("7", "Contrôleur — réponse", "—", "200"),
    ]
    for r, row in enumerate(rows, start=1):
        for c, val in enumerate(row):
            cell(b, t, r, c, val, align=(3 if c in (0, 3) else 0))
    b.note(
        "Les étapes 6 et 7 sont indissociables : le changement de statut et l'écriture dans l'historique "
        "forment une seule transaction (commit complet ou rollback complet). Un refus sans motif est "
        "rejeté deux fois : par le service (400) et par la contrainte ck_convention_motif."
    )

    # ---------------- 4. Schéma ----------------
    b.heading("4. Schéma relationnel et scripts")
    b.para(
        "Quatre scripts versionnés reconstruisent la base à l'identique. Ils créent la base dédiée "
        "tp3_conventions, puis les tables dans l'ordre des dépendances ; les vues sont supprimées avant "
        "les tables, ce qui rend l'ensemble rejouable sur une base vide.",
        size=10, align=2, after=1.5,
    )
    t = b.table(5, 2, [3700, 13300])
    for i, h in enumerate(["Fichier", "Contenu"]):
        cell(b, t, 0, i, h, bold=True)
    rows = [
        ("001_schema.sql",
         "Création de la base et des neuf tables : clés primaires, clés étrangères, contraintes UNIQUE "
         "et CHECK ; quatre vues d'indicateurs et de planning."),
        ("002_seed.sql",
         "Jeu fictif : 8 comptes, 3 étudiants, 2 encadreurs, 2 entreprises, 3 salles, 6 conventions, "
         "4 disponibilités, 2 soutenances et 9 lignes d'historique."),
        ("003_verification.sql",
         "Comptages par table, répartition par statut, conventions sans encadreur, planning, délais de "
         "publication, conflits et journal des décisions."),
        ("004_tests_contraintes.sql",
         "Insertions volontairement invalides : refus sans motif, email incorrect, entreprise inconnue, "
         "période inversée, doublon de créneau et chevauchement."),
    ]
    for r, row in enumerate(rows, start=1):
        for c, val in enumerate(row):
            cell(b, t, r, c, val)
    b.para(
        "Règles portées par la base : ck_convention_motif (refus motivé), ck_convention_depot (date de "
        "dépôt dès la soumission), ck_convention_decision (date de décision si validée ou refusée), "
        "ck_convention_periode (date de fin postérieure au début), ck_disponibilite_ordre, "
        "ck_soutenance_duree, ck_utilisateur_email et ck_historique_motif. Les clés UNIQUE "
        "uk_soutenance_salle_creneau et uk_soutenance_encadreur_creneau interdisent deux soutenances au "
        "même instant dans une salle ou avec un encadreur ; la vue v_soutenances_conflits détecte les "
        "chevauchements de durée.",
        size=9.2, align=2, before=1, after=1.5,
    )

    # ---------------- 5. Jeu d'essai ----------------
    b.heading("5. Jeu d'essai et vérification")
    b.para(
        "Résultat obtenu en exécutant 001_schema.sql, 002_seed.sql puis 003_verification.sql sur une base "
        "vide, sous MySQL 8.0.46. Sortie brute de 003_verification.sql (les blocs sont séparés pour la lecture) :",
        size=10, align=2, after=1.5,
    )
    for block in verification_output("sortie_verification.txt"):
        b.code_block(block, size=6.5)
        b.para("", size=1, after=0.6)

    b.para(
        "Contraintes éprouvées par des insertions invalides (script 004_tests_contraintes.sql, exécuté "
        "avec mysql --force) :",
        size=10, align=2, before=1, after=1.5,
    )
    t = b.table(7, 4, [3300, 5600, 5900, 2200])
    for i, h in enumerate(["Cas testé", "Requête", "Erreur renvoyée par la base", "Effet"]):
        cell(b, t, 0, i, h, bold=True)
    rows = [
        ("Refus sans motif", "INSERT … statut = 'REFUSEE', motif NULL",
         "ERROR 3819 : Check constraint 'ck_convention_motif' is violated.", "Aucune ligne"),
        ("Email sans arobase", "INSERT utilisateur … 'sans-arobase.test'",
         "ERROR 3819 : Check constraint 'ck_utilisateur_email' is violated.", "Aucune ligne"),
        ("Entreprise inexistante", "INSERT … entreprise_id = 999",
         "ERROR 1452 : fk_convention_entreprise fails.", "Aucune ligne"),
        ("Période inversée", "INSERT … date_debut > date_fin",
         "ERROR 3819 : Check constraint 'ck_convention_periode' is violated.", "Aucune ligne"),
        ("Doublon salle/créneau", "INSERT … salle 1, 15/06/2027 09:00",
         "ERROR 1062 : Duplicate entry for key 'uk_soutenance_salle_creneau'.", "Aucune ligne"),
        ("Chevauchement de 30 min", "INSERT … salle 1, 15/06/2027 09:30",
         "Accepté par les UNIQUE ; 1 ligne dans v_soutenances_conflits, puis rollback.", "0 conflit"),
    ]
    for r, row in enumerate(rows, start=1):
        for c, val in enumerate(row):
            cell(b, t, r, c, val)
    b.note(
        "Après les tests, les comptages sont restés identiques (6 conventions, 8 utilisateurs) et la vue "
        "des conflits est revenue à 0 : aucune écriture partielle n'a été conservée."
    )

    # ---------------- 6. Suite ----------------
    b.heading("6. Ce qui reste à faire")
    b.para(
        "Le modèle est figé pour la v1. Restent à écrire la couche d'accès aux données (TP6) et les tests "
        "T-02 à T-11 annoncés dans la matrice du TP2. Les diagrammes sont versionnés en sources modifiables "
        "(cas_utilisation.svg, sa variante cas_utilisation.puml et classes.puml) : une correction du modèle se fait dans "
        "le texte, pas dans une image. "
        "Les scripts SQL et leurs sorties sont conservés dans le dossier TP3_Modele_donnees, ce qui permet "
        "de rejouer la vérification à tout moment.",
        size=10, align=2, after=1.5,
    )

    # ---------------- Propriétés et sauvegarde ----------------
    try:
        dp = doc.getDocumentProperties()
        dp.Title = "TP3 — UML et modélisation des données"
        dp.Subject = "Plateforme de suivi des conventions de stage et des soutenances"
        dp.Author = "Groupe [0X]"
        dp.Description = "TP3 — Projet informatique 2, L3 SIL"
    except Exception:
        pass

    doc.storeToURL("file://" + os.path.abspath(path_odt), ())
    p = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
    p.Name = "FilterName"
    p.Value = "MS Word 2007 XML"
    doc.storeToURL("file://" + os.path.abspath(path_docx), (p,))
    doc.close(True)
    print("OK:", path_docx)


if __name__ == "__main__":
    build(
        sys.argv[1] if len(sys.argv) > 1 else "TP3_Modele_donnees.odt",
        sys.argv[2] if len(sys.argv) > 2 else "TP3_Modele_donnees.docx",
    )
