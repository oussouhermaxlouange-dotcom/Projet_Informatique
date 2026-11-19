#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Constructeur de rapports partagé (TP6, TP7, TP8).

Mise en page commune, en noir et blanc : A4, marges de 18 mm, Times New Roman
10 pt, tableaux à bordures noires dont aucune ligne n'est coupée entre deux
pages, pied de page numéroté. Le PDF est produit par Chrome depuis le HTML ;
le DOCX par l'API UNO de LibreOffice.

Ce module ne contient aucun contenu de rapport : chaque livrable fournit ses
propres données (TSV, textes) et appelle `Builder`.
"""

from __future__ import annotations

import os
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

PAGE_W, PAGE_H = 21000, 29700          # A4 en 1/100 mm
MARGIN_LR, MARGIN_TB = 1800, 1600      # 18 mm / 16 mm
CONTENT_W = PAGE_W - 2 * MARGIN_LR

PROFIL_UNO = "file:///tmp/opencode/lo_profile_rapports"
PORT_UNO = 2002

_CTX = None  # contexte UNO distant, renseigné par connecter()


# --------------------------------------------------------------------------- #
# Connexion UNO
# --------------------------------------------------------------------------- #
def connecter(port: int = PORT_UNO):
    local = uno.getComponentContext()
    resolver = local.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", local
    )
    ctx = resolver.resolve(
        f"uno:socket,host=127.0.0.1,port={port};urp;StarOffice.ComponentContext"
    )
    global _CTX
    _CTX = ctx
    return ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.frame.Desktop", ctx
    )


def demarrer_soffice(port: int = PORT_UNO) -> subprocess.Popen:
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice is None:
        raise SystemExit("LibreOffice introuvable : DOCX non généré.")
    proc = subprocess.Popen(
        [
            soffice,
            "--headless",
            "--norestore",
            "--invisible",
            f"-env:UserInstallation={PROFIL_UNO}",
            f"--accept=socket,host=127.0.0.1,port={port};urp;",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(80):
        try:
            return proc, connecter(port)
        except Exception:
            time.sleep(0.25)
    proc.terminate()
    raise SystemExit(f"LibreOffice n'a pas ouvert le port UNO {port}.")


def obtenir_bureau(port: int = PORT_UNO):
    """Réutilise un soffice déjà à l'écoute, sinon en démarre un."""
    try:
        return None, connecter(port)
    except Exception:
        return demarrer_soffice(port)


# --------------------------------------------------------------------------- #
# Mise en page
# --------------------------------------------------------------------------- #
def line_spacing(height: int = 115):
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


def add_footer(doc, page, texte: str):
    footer = page.FooterText
    fc = footer.createTextCursor()
    fc.CharFontName = FONT
    fc.CharHeight = 8
    fc.CharColor = BLACK
    fc.ParaAdjust = 3
    footer.insertString(fc, texte + " — page ", False)
    pn = doc.createInstance("com.sun.star.text.TextField.PageNumber")
    pn.NumberingType = 4
    footer.insertTextContent(fc, pn, False)
    footer.insertString(fc, " sur ", False)
    pc = doc.createInstance("com.sun.star.text.TextField.PageCount")
    pc.NumberingType = 4
    footer.insertTextContent(fc, pc, False)


# --------------------------------------------------------------------------- #
# Construction du contenu
# --------------------------------------------------------------------------- #
class Builder:
    """Primitives d'écriture : paragraphe, titre, note, tableau, saut de page."""

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
        return c

    def heading(self, txt):
        self.para(txt, size=11, bold=True, before=6, after=2, line=100, keep=True)

    def note(self, txt):
        self.para(txt, size=8, italic=True, align=2, before=1, after=3, line=105)

    def page_break(self):
        self.cur.BreakType = PAGE_BREAK
        self.text.insertControlCharacter(self.cur, PARA_BREAK, False)
        self.cur.BreakType = uno.Enum("com.sun.star.style.BreakType", "NONE")

    def image(self, chemin: Path, largeur: int = 12000, hauteur: int = 6000):
        """Insère une image (1/100 mm) centrée, suivie d'un saut de paragraphe."""
        if _CTX is None:
            raise RuntimeError("Connexion UNO absente : appeler connecter() d'abord.")
        provider = _CTX.ServiceManager.createInstanceWithContext(
            "com.sun.star.graphic.GraphicProvider", _CTX
        )
        args = (uno.createUnoStruct("com.sun.star.beans.PropertyValue"),)
        args[0].Name = "URL"
        args[0].Value = Path(chemin).resolve().as_uri()
        graphique = provider.queryGraphic(args)

        image = self.doc.createInstance("com.sun.star.drawing.GraphicObjectShape")
        image.Graphic = graphique
        taille = uno.createUnoStruct("com.sun.star.awt.Size")
        taille.Width = largeur
        taille.Height = hauteur
        image.Size = taille
        image.AnchorType = uno.Enum(
            "com.sun.star.text.TextContentAnchorType", "AS_CHARACTER"
        )
        try:
            image.Surround = uno.Enum("com.sun.star.text.WrapTextMode", "NONE")
        except Exception:
            pass
        self.cur.ParaAdjust = 3
        self.text.insertTextContent(self.cur, image, False)
        self.text.insertControlCharacter(self.cur, PARA_BREAK, False)
        # Le curseur d'insertion reste avant l'objet : on le replace en fin de texte.
        self.cur.gotoEnd(False)

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
# Documents
# --------------------------------------------------------------------------- #
def nouveau_document(pied: str):
    """Crée un document Writer paginé et renvoie (doc, builder)."""
    lance, desktop = obtenir_bureau()
    doc = desktop.loadComponentFromURL("private:factory/swriter", "_blank", 0, ())
    page = set_page(doc)
    add_footer(doc, page, pied)
    return doc, Builder(doc)


def enregistrer_docx(doc, chemin: Path, titre: str, sujet: str, auteur: str,
                     description: str) -> None:
    try:
        dp = doc.getDocumentProperties()
        dp.Title = titre
        dp.Subject = sujet
        dp.Author = auteur
        dp.Description = description
    except Exception:
        pass
    p = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
    p.Name = "FilterName"
    p.Value = "MS Word 2007 XML"
    doc.storeToURL("file://" + os.path.abspath(chemin), (p,))
    doc.close(False)


def fermer_soffice_si_lance(proc) -> None:
    if proc is not None:
        proc.terminate()


def generer_pdf(html: Path, pdf: Path) -> bool:
    """Imprime le HTML en PDF A4 via Chrome headless."""
    chrome = shutil.which("google-chrome") or shutil.which("chromium")
    if chrome is None:
        print("Chrome introuvable : PDF non généré.", file=sys.stderr)
        return False
    subprocess.run(
        [
            chrome,
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--hide-scrollbars",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf}",
            html.as_uri(),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return pdf.exists()


def compter_pages(pdf: Path) -> int:
    out = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True)
    for ligne in out.stdout.splitlines():
        if ligne.startswith("Pages:"):
            return int(ligne.split()[1])
    return 0
