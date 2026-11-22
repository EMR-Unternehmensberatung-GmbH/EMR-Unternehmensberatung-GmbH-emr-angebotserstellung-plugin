#!/usr/bin/env python3
"""
Angebots-PDF im EMR-Premium-Layout.

Seiten: Deckblatt -> Anschreiben -> Angebot im Überblick -> Vorteile & Referenzen
        -> Auftrag erteilen -> (Unterhaltsreinigung) Anlage 1 Reinigungsplan, Anlage 2 Leistungsverzeichnis

Preise kommen aus kalkulation.py. Branding (Logo, Farben, Kontaktdaten) aus firma.yaml.

Aufruf:
  python3 angebot_pdf.py --angebot angebot.json --firma firma.yaml --assets <ordner> --out angebot.pdf [--entwurf]
"""
import argparse
import datetime
import json
import os
import sys
from xml.sax.saxutils import escape

from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import kalkulation as K  # noqa: E402
except ImportError:  # Connector-Paket: gerechnet wird auf dem EMR-Server
    import ausgabe as K  # noqa: E402

_PAKET = None  # Paket vom EMR-Server (--paket), sonst rechnet kalkulation.py hier


def _daten(name):
    if _PAKET is not None:
        if name not in _PAKET["daten"]:
            raise K.KalkulationsFehler(f"{name} fehlt im Paket vom EMR-Server.")
        return json.loads(json.dumps(_PAKET["daten"][name]))
    return K.lade_json(name)

W, H = A4
ML, MR = 20 * mm, 20 * mm
BREITE = W - ML - MR
FUSS_H = 28 * mm
TEXT = HexColor("#262626")
GRAU = HexColor("#4A4F57")
HAAR = HexColor("#D9D9D9")
WOCHE = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
TAG_LANG = {"Mo": "Montag", "Di": "Dienstag", "Mi": "Mittwoch", "Do": "Donnerstag",
            "Fr": "Freitag", "Sa": "Samstag", "So": "Sonntag"}


# ---------------------------------------------------------------- Schrift & Farbe
def schriften():
    for reg, bold in [
        ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")]:
        if os.path.exists(reg) and os.path.exists(bold):
            pdfmetrics.registerFont(TTFont("Txt", reg))
            pdfmetrics.registerFont(TTFont("Txt-B", bold))
            registerFontFamily("Txt", normal="Txt", bold="Txt-B", italic="Txt", boldItalic="Txt-B")
            return "Txt", "Txt-B"
    return "Helvetica", "Helvetica-Bold"


F, FB = schriften()


def mische(farbe, anteil):
    """anteil 0..1 = Anteil der Farbe, Rest Weiß."""
    return Color(1 - (1 - farbe.red) * anteil, 1 - (1 - farbe.green) * anteil, 1 - (1 - farbe.blue) * anteil)


def st(gr=10.5, fett=False, farbe=TEXT, lead=None, align=0):
    return ParagraphStyle("x", fontName=FB if fett else F, fontSize=gr, leading=lead or gr * 1.42,
                          textColor=farbe, alignment=align)


def para(c, txt, x, y, b, stil):
    p = Paragraph(txt, stil)
    _, h = p.wrap(b, H)
    p.drawOn(c, x, y - h)
    return y - h


def para_h(txt, b, stil):
    return Paragraph(txt, stil).wrap(b, H)[1]


def logo_vorbereiten(pfad):
    """Schneidet weiße/transparente Ränder ab, damit das Logo in voller Größe erscheint.
    Gibt den Pfad einer zugeschnittenen PNG-Kopie zurück (oder das Original, wenn PIL fehlt)."""
    try:
        from PIL import Image, ImageChops
    except ImportError:
        return pfad
    try:
        im = Image.open(pfad).convert("RGBA")
    except Exception:
        return pfad
    alpha = im.split()[-1]
    weiss = Image.new("RGBA", im.size, (255, 255, 255, 255))
    flach = Image.alpha_composite(weiss, im).convert("RGB")
    diff = ImageChops.difference(flach, Image.new("RGB", im.size, (255, 255, 255)))
    diff = ImageChops.add(diff, diff, 2.0, -12)
    box = diff.getbbox()
    abox = alpha.point(lambda v: 255 if v > 12 else 0).getbbox()
    if abox and box:
        box = (max(box[0], abox[0]), max(box[1], abox[1]), min(box[2], abox[2]), min(box[3], abox[3]))
    box = box or abox
    if not box or box == (0, 0) + im.size:
        return pfad
    rand = max(2, int(0.01 * max(im.size)))
    box = (max(0, box[0] - rand), max(0, box[1] - rand), min(im.width, box[2] + rand), min(im.height, box[3] + rand))
    import tempfile
    ziel = os.path.join(tempfile.gettempdir(), "emr_logo_" + os.path.splitext(os.path.basename(pfad))[0] + ".png")
    im.crop(box).save(ziel)
    return ziel


def farben_aus_logo(pfad):
    """Ermittelt die markanteste Farbe im Logo (gesättigt, nicht weiß/grau/schwarz) als HEX, sonst None."""
    try:
        from PIL import Image
        import colorsys
        im = Image.open(pfad).convert("RGBA")
        im.thumbnail((160, 160))
        zaehler = {}
        for r, g, b, a in (im.get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata()):
            if a < 128:
                continue
            h, l, sat = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
            if sat < 0.25 or l > 0.92 or l < 0.08:
                continue
            k = (r // 24 * 24, g // 24 * 24, b // 24 * 24)
            zaehler[k] = zaehler.get(k, 0) + 1
        if not zaehler:
            return None
        r, g, b = max(zaehler, key=zaehler.get)
        return "#%02X%02X%02X" % (min(r + 12, 255), min(g + 12, 255), min(b + 12, 255))
    except Exception:
        return None


def lesbar_dunkel(farbe, max_hell=0.42):
    """Dunkelt eine Farbe ab, bis weiße Schrift darauf lesbar ist (relative Helligkeit)."""
    r, g, b = farbe.red, farbe.green, farbe.blue
    for _ in range(12):
        if 0.2126 * r + 0.7152 * g + 0.0722 * b <= max_hell:
            break
        r, g, b = r * 0.88, g * 0.88, b * 0.88
    return Color(r, g, b)


def dunkel_mische(farbe, anteil, basis=(0.18, 0.19, 0.21)):
    """anteil = Anteil der Farbe, Rest ein dunkles Neutral – für farbige statt graue Nebentexte."""
    return Color(basis[0] + (farbe.red - basis[0]) * anteil, basis[1] + (farbe.green - basis[1]) * anteil,
                 basis[2] + (farbe.blue - basis[2]) * anteil)


# ---------------------------------------------------------------- Canvas mit "Seite x von y"
class Leinwand(canvas.Canvas):
    def __init__(self, *a, fuss=None, **k):
        super().__init__(*a, **k)
        self._seiten = []
        self._fuss = fuss

    def showPage(self):
        self._seiten.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        n = len(self._seiten)
        for i, zustand in enumerate(self._seiten, 1):
            self.__dict__.update(zustand)
            if self._fuss and i > 1:
                self._fuss(self, i, n)
            super().showPage()
        super().save()


class Angebot:
    def __init__(self, pfad, firma, assets, angebot, entwurf=False):
        self.firma, self.assets, self.a = firma, assets, angebot
        global GRAU, HAAR
        self.logo_original = self.bild_pfad((firma.get("logos") or {}).get("eigenes"))
        self.logo_pfad = logo_vorbereiten(self.logo_original) if self.logo_original else None
        fb = firma.get("farben") or {}
        logo_farbe = farben_aus_logo(self.logo_pfad) if self.logo_pfad else None
        prim = fb.get("primaer")
        if prim in (None, "", "auto", "XX"):
            prim = logo_farbe or "#1B2A4A"
        akz = fb.get("akzent")
        if akz in (None, "", "auto", "XX"):
            akz = prim
        self.P = lesbar_dunkel(HexColor(prim))
        self.A = lesbar_dunkel(HexColor(akz), 0.55)
        self.P10 = mische(self.P, 0.08)
        self.P25 = mische(self.P, 0.25)
        GRAU = dunkel_mische(self.P, 0.35)
        HAAR = mische(self.P, 0.28)
        self.entwurf = entwurf
        self.fi = firma.get("firma") or {}
        self.c = Leinwand(pfad, pagesize=A4, fuss=self.fuss)
        self.c.setTitle(f"Angebot {self.fi.get('name', '')}")
        self.c.setAuthor(self.fi.get("name", ""))

    # -------- Hilfen
    def bild_pfad(self, name):
        if not name:
            return None
        for k in [name, os.path.join(self.assets, name), os.path.join(self.assets, os.path.basename(name))]:
            if os.path.exists(k):
                return k
        return None

    def bild(self, pfad, x, oben, max_b, max_h, ausrichtung="links"):
        img = ImageReader(pfad)
        iw, ih = img.getSize()
        f = min(max_b / iw, max_h / ih)
        b, h = iw * f, ih * f
        if ausrichtung == "mitte":
            x = x - b / 2
        self.c.drawImage(img, x, oben - h, b, h, mask="auto")
        return b, h

    def wasserzeichen(self):
        c = self.c
        c.saveState()
        if self.logo_pfad:
            c.setFillAlpha(0.045)
            img = ImageReader(self.logo_pfad)
            iw, ih = img.getSize()
            b = 130 * mm
            h = b * ih / iw
            if h > 90 * mm:
                h = 90 * mm
                b = h * iw / ih
            c.translate(W / 2, H / 2 - 10 * mm)
            c.rotate(0)
            c.drawImage(img, -b / 2, -h / 2, b, h, mask="auto")
        else:
            c.setFillColor(self.P)
            c.setFillAlpha(0.05)
            c.setFont(FB, 60)
            c.translate(W / 2, H / 2)
            c.rotate(35)
            c.drawCentredString(0, 0, self.fi.get("name", ""))
        c.restoreState()
        if self.entwurf:
            c.saveState()
            c.setFillColor(HexColor("#C0392B"))
            c.setFillAlpha(0.10)
            c.setFont(FB, 110)
            c.translate(W / 2, H / 2)
            c.rotate(40)
            c.drawCentredString(0, -30, "ENTWURF")
            c.restoreState()

    def kopf(self, titel=None):
        """Kopf auf Inhaltsseiten. Gibt y-Startposition zurück."""
        c = self.c
        self.wasserzeichen()
        top = H - 12 * mm
        if self.logo_pfad:
            self.bild(self.logo_pfad, ML, top, 62 * mm, 17 * mm)
        else:
            c.setFont(FB, 13)
            c.setFillColor(self.P)
            c.drawString(ML, top - 11, self.fi.get("name", ""))
        c.setFont(FB, 8.5)
        c.setFillColor(self.P)
        rechts = self.titel_kurz
        if self.a.get("angebots_nr"):
            rechts += f"   Nr. {self.a['angebots_nr']}"
        c.drawRightString(W - MR, top - 8, rechts)
        c.setStrokeColor(self.P)
        c.setLineWidth(1.1)
        c.line(ML, top - 20 * mm, W - MR, top - 20 * mm)
        y = top - 27 * mm
        if titel:
            c.setFillColor(self.P)
            c.setFont(FB, 20)
            c.drawString(ML, y - 16, titel)
            y -= 16 + 9 * mm
        return y

    def fuss(self, c, nr, gesamt):
        """Fußzeile in vier Spalten (Firma · Kontakt · Bank · Register/Steuer), Linie in Primärfarbe."""
        def ok(x):
            return x and str(x).strip() not in ("XX", "")
        fi, bank = self.fi, (self.firma.get("bank") or {})
        spalten = [
            ("Anschrift", [fi.get("name"), fi.get("strasse"), fi.get("plz_ort")]),
            ("Kontakt", [f"Tel. {fi['telefon']}" if ok(fi.get("telefon")) else None, fi.get("email"), fi.get("web")]),
            ("Bankverbindung", [bank.get("name"), f"IBAN {bank['iban']}" if ok(bank.get("iban")) else None,
                                f"BIC {bank['bic']}" if ok(bank.get("bic")) else None]),
            ("Unternehmen", [f"Geschäftsführung: {fi['geschaeftsfuehrer']}" if ok(fi.get("geschaeftsfuehrer")) else None,
                             fi.get("registergericht"), fi.get("handelsregister"),
                             f"USt-IdNr. {fi['ust_id']}" if ok(fi.get("ust_id")) else
                             (f"St.-Nr. {fi['steuernummer']}" if ok(fi.get("steuernummer")) else None)]),
        ]
        spalten = [(t, [z for z in zeilen if ok(z)]) for t, zeilen in spalten]
        spalten = [(t, z) for t, z in spalten if z]
        c.saveState()
        oben = 24 * mm
        c.setStrokeColor(self.P)
        c.setLineWidth(1.1)
        c.line(ML, oben + 2.5 * mm, W - MR, oben + 2.5 * mm)
        gew = {"Anschrift": 0.95, "Kontakt": 0.95, "Bankverbindung": 1.2, "Unternehmen": 1.1}
        summe = sum(gew[t] for t, _ in spalten) or 1
        x = ML
        for titel, zeilen in spalten:
            sb = BREITE * gew[titel] / summe
            c.setFont(FB, 6.8)
            c.setFillColor(self.P)
            c.drawString(x, oben - 1 * mm, titel.upper())
            c.setFont(F, 7)
            c.setFillColor(TEXT)
            for j, z in enumerate(zeilen[:4]):
                t = str(z)
                while c.stringWidth(t + "…", F, 7) > sb - 2.5 * mm and len(t) > 4:
                    t = t[:-1]
                c.drawString(x, oben - 4.5 * mm - j * 3.2 * mm, t if t == str(z) else t + "…")
            x += sb
        c.setFont(FB, 7.5)
        c.setFillColor(self.P)
        c.drawRightString(W - MR, 5.5 * mm, f"Seite {nr} von {gesamt}")
        c.restoreState()

    def haken(self, x, y, r=2.3 * mm, farbe=None):
        c = self.c
        c.saveState()
        c.setFillColor(farbe or self.A)
        c.circle(x + r, y + r * 0.8, r, stroke=0, fill=1)
        c.setStrokeColor(white)
        c.setLineWidth(1.3)
        c.setLineCap(1)
        c.setLineJoin(1)
        p = c.beginPath()
        p.moveTo(x + r * 0.5, y + r * 0.8)
        p.lineTo(x + r * 0.88, y + r * 0.38)
        p.lineTo(x + r * 1.55, y + r * 1.25)
        c.drawPath(p, stroke=1, fill=0)
        c.restoreState()

    def stern(self, cx, cy, r, farbe):
        import math
        c = self.c
        p = c.beginPath()
        for i in range(10):
            rr = r if i % 2 == 0 else r * 0.45
            w = math.pi / 2 + i * math.pi / 5
            x, y = cx + rr * math.cos(w), cy + rr * math.sin(w)
            p.moveTo(x, y) if i == 0 else p.lineTo(x, y)
        p.close()
        c.setFillColor(farbe)
        c.drawPath(p, stroke=0, fill=1)

    def neue_seite(self):
        self.c.showPage()

    def platz(self, y, bedarf, titel=None):
        if y - bedarf < FUSS_H + 3 * mm:
            self.neue_seite()
            return self.kopf(titel)
        return y


# ---------------------------------------------------------------- Seiten
def deckblatt(d, titel, datum):
    c, a, P = d.c, d.a, d.P
    # Farbfläche links als ruhige Signatur
    c.setFillColor(P)
    c.rect(0, 0, 9 * mm, H, stroke=0, fill=1)
    x0 = 9 * mm + 17 * mm
    top = H - 24 * mm
    if d.logo_pfad:
        d.bild(d.logo_pfad, x0, top, 100 * mm, 40 * mm)
    else:
        c.setFont(FB, 20)
        c.setFillColor(P)
        c.drawString(x0, top - 18, d.fi.get("name", ""))
    y = H * 0.58
    c.setFillColor(d.A)
    c.setFont(FB, 16)
    c.drawString(x0, y, "Angebot")
    y -= 15 * mm
    breite = W - x0 - MR
    y = para(c, f"<b>{escape(titel)}</b>", x0, y + 6 * mm, breite, st(34, True, P, 38))
    y -= 9 * mm
    k = a.get("kunde") or {}
    y = para(c, f"für {escape(k.get('firma', ''))}", x0, y, breite, st(15, False, TEXT, 20))
    # Faktenraster
    o = a.get("objekt") or k
    ap = kontaktperson(d)
    fakten = [
        ("Objekt", "<br/>".join(escape(x) for x in [o.get("strasse"), o.get("plz_ort")] if x) or "–"),
        ("Angebots-Nr.", escape(a.get("angebots_nr") or "–")),
        ("Datum", escape(datum)),
        ("Ihr Ansprechpartner", "<br/>".join(escape(x) for x in [ap["name"], ap["telefon"]] if x)),
    ]
    yb = 62 * mm
    c.setStrokeColor(P)
    c.setLineWidth(1.1)
    c.line(x0, yb + 8 * mm, W - MR, yb + 8 * mm)
    sb = breite / 4
    for i, (lab, wert) in enumerate(fakten):
        x = x0 + i * sb
        para(c, escape(lab), x, yb, sb - 4 * mm, st(8.5, True, P))
        para(c, wert, x, yb - 5.5 * mm, sb - 4 * mm, st(10, True, TEXT, 13.5))
    d.neue_seite()


def kontaktperson(d):
    """Ansprechpartner des Betriebs für den Auftraggeber („Ihr direkter Draht“): kontaktperson aus dem Angebot, sonst
    firma.kontaktperson, sonst der Unterzeichner. Telefon und E-Mail fallen auf die der Firma zurück.
    (Nicht zu verwechseln mit kunde.ansprechpartner – das ist die Person beim Auftraggeber.)"""
    u = d.fi.get("unterzeichner") or {}
    ap = (d.a.get("kontaktperson") or {}) if (d.a.get("kontaktperson") or {}).get("name") else \
        (d.fi.get("kontaktperson") or {})
    gueltig = lambda v: v if v and str(v).strip().upper() != "XX" else None
    if not gueltig(ap.get("name")):
        ap = {}
    return {"name": gueltig(ap.get("name")) or gueltig(u.get("name")) or "",
            "funktion": gueltig(ap.get("funktion")) or ("" if ap else gueltig(u.get("funktion"))) or "",
            "telefon": gueltig(ap.get("telefon")) or gueltig(d.fi.get("telefon")),
            "email": gueltig(ap.get("email")) or gueltig(d.fi.get("email"))}


def anrede_name(k):
    if k.get("anrede_name"):
        return k["anrede_name"]
    teile = (k.get("ansprechpartner") or "").split()
    titel = [t for t in teile if t.lower() in ("dr.", "prof.", "dipl.-ing.", "mag.")]
    return " ".join(titel + teile[-1:]) if teile else ""


def anrede(k):
    n = anrede_name(k)
    if not n:
        return "Sehr geehrte Damen und Herren,"
    a = (k.get("anrede") or "").lower()
    return {"frau": f"Sehr geehrte Frau {n},", "herr": f"Sehr geehrter Herr {n},"}.get(a, f"Guten Tag {n},")


def anschreiben(d, texte, stadt_datum, gegenstand):
    c, a = d.c, d.a
    t = texte["anschreiben"]
    y = d.kopf()
    k = a.get("kunde") or {}
    # Absenderzeile klein
    absender = ", ".join(x for x in [d.fi.get("name"), d.fi.get("strasse"), d.fi.get("plz_ort")] if x)
    para(c, escape(absender), ML, y, 100 * mm, st(7.5, False, GRAU))
    y -= 6 * mm
    yk = y
    for z in [k.get("firma"), k.get("ansprechpartner"), k.get("strasse"), k.get("plz_ort")]:
        if z:
            yk = para(c, escape(z), ML, yk, 100 * mm, st(10.5))
    c.setFont(F, 10)
    c.setFillColor(GRAU)
    c.drawRightString(W - MR, y - 10, stadt_datum)
    y = yk - 14 * mm
    y = para(c, escape(d.titel_kopf), ML, y, BREITE, st(13, True, d.P)) - 7 * mm
    # Kontaktkasten rechts: so breit, dass die längste Kontaktzeile in 9 pt in eine Zeile passt
    ap = kontaktperson(d)
    kontakt = [(lab, v) for lab, v in [("Telefon", ap["telefon"]), ("E-Mail", ap["email"]), ("Web", d.fi.get("web"))]
               if v and v != "XX"]
    bk_noetig = max([stringWidth(str(v), F, 9) for _, v in kontakt] + [38 * mm]) + 10 * mm
    tb = max(min(112 * mm, W - MR - ML - 8 * mm - bk_noetig), 90 * mm)
    for txt in [anrede(k), t["dank"], t["ueberreichung"].format(gegenstand=gegenstand), t["auftrag"], t["fragen"]]:
        y = para(c, escape(txt), ML, y, tb, st(10.5)) - 3.8 * mm
    y = para(c, escape(t["abschluss"]), ML, y, tb, st(10.5)) - 6 * mm
    gruss = (d.firma.get("angebot") or {}).get("grussformel") or t["gruss"]
    y = para(c, escape(gruss), ML, y, tb, st(10.5)) - 10 * mm
    u = d.fi.get("unterzeichner") or {}
    y = para(c, escape(u.get("name", "")), ML, y, tb, st(10.5, True))
    para(c, escape(u.get("funktion", "")), ML, y, tb, st(9, False, GRAU))
    # Kontaktspalte rechts
    xk = ML + tb + 8 * mm
    bk = W - MR - xk
    yk = yk - 14 * mm - 7 * mm - 12
    zeilen = [("Ihr direkter Draht", st(10, True, d.P), 3 * mm), (escape(ap["name"]), st(9.5, True), 0),
              (escape(ap["funktion"]), st(8.5, False, GRAU), 3 * mm)]
    for lab, v in kontakt:
        txt = escape(str(v))
        if stringWidth(str(v), F, 9) > bk - 10 * mm and "@" in txt:
            txt = txt.replace("@", "<br/>@")   # nur bei sehr langen Adressen, nie mitten im Wort
        zeilen += [(escape(lab), st(8, False, GRAU), 0), (txt, st(9, False, TEXT), 1.5 * mm)]
    # Kasten mindestens so hoch wie bisher (62 mm), bei mehr Inhalt höher – nie läuft Text über den Rand.
    hk = max(62 * mm, sum(para_h(z, bk - 10 * mm, s) + g for z, s, g in zeilen) + 10 * mm)
    c.setFillColor(d.P10)
    c.rect(xk, yk - hk, bk, hk, stroke=0, fill=1)
    yy = yk - 5 * mm
    for z, s, g in zeilen:
        yy = para(c, z, xk + 5 * mm, yy, bk - 10 * mm, s) - g
    d.neue_seite()


def kaufmotive_block(d, y):
    km = [m for m in (d.a.get("kaufmotive") or []) if m.get("motiv") and m.get("umsetzung")][:3]
    if not km:
        return y
    c = d.c
    y = para(c, "Was Ihnen wichtig ist – und wie wir es umsetzen", ML, y, BREITE, st(12, True, TEXT)) - 4 * mm
    n = len(km)
    gap = 6 * mm
    sb = (BREITE - gap * (n - 1)) / n
    hoehen = [para_h(f"<b>{escape(m['motiv'])}</b>", sb, st(10.5, True, d.P)) +
              para_h(escape(m["umsetzung"]), sb, st(9.5)) for m in km]
    hmax = max(hoehen) + 6 * mm
    for i, m in enumerate(km):
        x = ML + i * (sb + gap)
        c.setStrokeColor(d.P)
        c.setLineWidth(2)
        c.line(x, y, x + 12 * mm, y)
        yy = para(c, escape(m["motiv"]), x, y - 3.5 * mm, sb, st(10.5, True, d.P)) - 1.5 * mm
        para(c, escape(m["umsetzung"]), x, yy, sb, st(9.5))
    return y - hmax - 4 * mm


def preis_panel(d, y, label, betrag, unterzeile, fakten):
    """Das eine starke Element: Preisfeld in der Primärfarbe."""
    c = d.c
    hl = 44 * mm
    lb = 72 * mm
    rb = BREITE - lb
    hr = sum(para_h(f"{escape(k)}<br/><b>{escape(v)}</b>", rb - 14 * mm, st(9.5, False, TEXT, 13)) + 3 * mm
             for k, v in fakten) + 8 * mm
    h = max(hl, hr)
    c.setFillColor(d.P)
    c.rect(ML, y - h, lb, h, stroke=0, fill=1)
    c.setFillColor(d.P10)
    c.rect(ML + lb, y - h, rb, h, stroke=0, fill=1)
    para(c, escape(label), ML + 7 * mm, y - 7 * mm, lb - 14 * mm, st(10, False, white))
    c.setFillColor(white)
    c.setFont(FB, 27)
    c.drawString(ML + 7 * mm, y - 7 * mm - 14 - 12 * mm, betrag)
    para(c, escape(unterzeile), ML + 7 * mm, y - h + 13 * mm, lb - 14 * mm, st(9, False, white))
    yy = y - 6 * mm
    for k, v in fakten:
        yy = para(c, f"<font color='#{d.P.hexval()[2:]}'>{escape(k)}</font><br/><b>{escape(v)}</b>",
                  ML + lb + 7 * mm, yy, rb - 14 * mm, st(9.5, False, TEXT, 13)) - 3 * mm
    return y - h - 9 * mm


def zwei_spalten_hoehe(links, rechts_kv):
    """Tatsächlicher Platzbedarf des Blocks 'Im Preis enthalten / Konditionen'."""
    sb = (BREITE - 10 * mm) / 2
    hl = sum(para_h(escape(i), sb - 8 * mm, st(10)) + 2.6 * mm for i in links)
    hr = sum(para_h(escape(k), sb, st(8.5, True)) + 0.5 * mm + para_h(escape(str(v)), sb, st(10)) + 3 * mm
             for k, v in rechts_kv)
    return 8 * mm + max(hl, hr) + 1 * mm


def leistungen_konditionen(d, y, tx, kond):
    """Zeichnet 'Im Preis enthalten / Konditionen'. Passt der Block nicht mehr auf die Seite, beginnt er
    oben auf der nächsten – und die Vorteile laufen direkt darunter weiter (keine halbleere Seite)."""
    bedarf = zwei_spalten_hoehe(tx["inklusive"], list(kond.items()))
    if y - bedarf < FUSS_H + 3 * mm:
        d.neue_seite()
        y = d.kopf()
        d.rest_y = zwei_spalten_listen(d, y, "Im Preis enthalten", tx["inklusive"], "Konditionen", list(kond.items()))
        return
    zwei_spalten_listen(d, y, "Im Preis enthalten", tx["inklusive"], "Konditionen", list(kond.items()))
    d.neue_seite()


def zwei_spalten_listen(d, y, links_titel, links, rechts_titel, rechts_kv):
    c = d.c
    sb = (BREITE - 10 * mm) / 2
    para(c, escape(links_titel), ML, y, sb, st(11, True))
    para(c, escape(rechts_titel), ML + sb + 10 * mm, y, sb, st(11, True))
    y -= 8 * mm
    yl = y
    for item in links:
        d.haken(ML, yl - 3.6 * mm)
        yl = para(c, escape(item), ML + 7.5 * mm, yl, sb - 8 * mm, st(10)) - 2.6 * mm
    yr = y
    xr = ML + sb + 10 * mm
    for k, v in rechts_kv:
        c.setStrokeColor(HAAR)
        c.setLineWidth(0.5)
        yr = para(c, escape(k), xr, yr, sb, st(8.5, True, d.P)) - 0.5 * mm
        yr = para(c, escape(str(v)), xr, yr, sb, st(10)) - 3 * mm
    return min(yl, yr) - 6 * mm


def wochenleiste(d, y, zeiten_tage, feiertage):
    """Sieben Tagesfelder; aktive Tage in Primärfarbe mit Uhrzeit."""
    c = d.c
    titel = "Einsatztage und -zeiten" if d.a.get("leistungsart") == "hausmeisterservice" else "Reinigungstage und -zeiten"
    y = para(c, titel, ML, y, BREITE, st(11, True)) - 4 * mm
    gap = 2.5 * mm
    b = (BREITE - 6 * gap) / 7
    h = 17 * mm
    for i, tag in enumerate(WOCHE):
        x = ML + i * (b + gap)
        aktiv = tag in zeiten_tage
        c.setFillColor(d.P if aktiv else HexColor("#F2F2F2"))
        c.roundRect(x, y - h, b, h, 1.5 * mm, stroke=0, fill=1)
        c.setFillColor(white if aktiv else GRAU)
        c.setFont(FB, 10)
        c.drawCentredString(x + b / 2, y - 6.5 * mm, TAG_LANG[tag][:2])
        c.setFont(F, 7.2)
        z = (zeiten_tage.get(tag) or "").replace(" Uhr", "")
        if not aktiv:
            c.drawCentredString(x + b / 2, y - 12.5 * mm, "–")
            continue
        teile = [t.strip() for t in z.replace("–", "-").split("-")] if "-" in z.replace("–", "-") else [z]
        if len(teile) == 2:
            c.drawCentredString(x + b / 2, y - 11.3 * mm, teile[0] + " –")
            c.drawCentredString(x + b / 2, y - 14.6 * mm, teile[1] + " Uhr")
        else:
            c.drawCentredString(x + b / 2, y - 12.5 * mm, z or "")
    y -= h + 2 * mm
    c.setFont(F, 8.5)
    c.setFillColor(GRAU)
    c.drawString(ML, y - 8, "Feiertage: " + (feiertage or "keine Reinigung"))
    return y - 8 * mm


def angebot_monatlich(d, erg, tx, kond):
    c, a = d.c, d.a
    y = d.kopf("Ihr Angebot im Überblick")
    y = para(c, escape(tx["intro"]), ML, y, BREITE * 0.82, st(10.5)) - 6 * mm
    y = kaufmotive_block(d, y)
    tage = reinigungstage(erg)
    fakten = []
    if erg.get("summe_flaeche"):
        fakten.append(("Reinigungsfläche", f"{K.zahl(erg['summe_flaeche'])} m²"))
    if tage:
        fakten.append(("Reinigungstage", ", ".join(TAG_LANG[t] for t in tage)))
    if erg["leistungsart"] == "unterhaltsreinigung":
        fakten.append(("Leistungsumfang", "laut Reinigungsplan und Leistungsverzeichnis"))
    elif erg.get("zeilen"):
        fakten.append(("Leistungsumfang", "laut Aufgabenplan (Anlage 1)"))
    else:
        fakten.append(("Leistungsumfang", "gemäß vereinbartem Aufgabenplan"))
    if a.get("leistungsbeginn"):
        fakten.append(("Leistungsbeginn", a["leistungsbeginn"]))
    y = d.platz(y, 55 * mm, "Ihr Angebot im Überblick")
    y = preis_panel(d, y, "Monatliche Pauschale", K.eur(erg["pauschale"], 2), "netto zzgl. gesetzlicher MwSt.", fakten)
    zt = zeiten_je_tag(a, tage)
    if zt:
        y = d.platz(y, 36 * mm)
        y = wochenleiste(d, y, zt, (a.get("zeiten") or {}).get("Feiertage") or a.get("feiertage"))
    leistungen_konditionen(d, y - 2 * mm, tx, kond)


def tabelle(d, y, kopf, zeilen, spalten, ausr=None, fett_zeilen=(), titel_folgeseite=None, zebra=True):
    c = d.c
    ausr = ausr or ["L"] * len(spalten)

    def pad(b):
        return 2 * mm if b >= 14 * mm else 0.6 * mm

    def zelle(txt, b, fett, farbe, al):
        return Paragraph(str(txt), st(9 if b > 12 * mm else 8.5, fett, farbe, 12, {"L": 0, "C": 1, "R": 2}[al]))

    def zeichne(z, ist_kopf, y, idx):
        ps = [zelle(v, b - 2 * pad(b), ist_kopf or idx in fett_zeilen, white if ist_kopf else TEXT, al)
              for v, b, al in zip(z, spalten, ausr)]
        hs = [p.wrap(b - 2 * pad(b), H)[1] for p, b in zip(ps, spalten)]
        h = max(hs) + 4.2 * mm
        if ist_kopf:
            c.setFillColor(d.P)
            c.rect(ML, y - h, sum(spalten), h, stroke=0, fill=1)
        elif idx in fett_zeilen:
            c.setFillColor(d.P10)
            c.rect(ML, y - h, sum(spalten), h, stroke=0, fill=1)
        elif zebra and idx % 2 == 1:
            c.setFillColor(HexColor("#F7F7F7"))
            c.rect(ML, y - h, sum(spalten), h, stroke=0, fill=1)
        x = ML
        for p, b, hh in zip(ps, spalten, hs):
            p.drawOn(c, x + pad(b), y - h + (h - hh) / 2)
            x += b
        if not ist_kopf:
            c.setStrokeColor(HAAR)
            c.setLineWidth(0.4)
            c.line(ML, y - h, ML + sum(spalten), y - h)
        return y - h, h

    def h_von(z):
        return max(zelle(v, b - 2 * pad(b), False, TEXT, "L").wrap(b - 2 * pad(b), H)[1] for v, b in zip(z, spalten)) + 4.2 * mm

    if kopf:
        y = d.platz(y, h_von(kopf) + h_von(zeilen[0]) if zeilen else 20 * mm, titel_folgeseite)
        y, _ = zeichne(kopf, True, y, -1)
    for i, z in enumerate(zeilen):
        if y - h_von(z) < FUSS_H + 3 * mm:
            d.neue_seite()
            y = d.kopf(titel_folgeseite)
            if kopf:
                y, _ = zeichne(kopf, True, y, -1)
        y, _ = zeichne(z, False, y, i)
    return y


def angebot_einmalig(d, erg, tx, kond):
    c, a = d.c, d.a
    y = d.kopf("Ihr Angebot im Überblick")
    y = para(c, escape(tx["intro"]), ML, y, BREITE * 0.82, st(10.5)) - 8 * mm
    y = kaufmotive_block(d, y)
    sp = [14 * mm, 82 * mm, 26 * mm, 20 * mm, BREITE - 142 * mm]
    zeilen, fett, akt = [], [], None
    for z in erg["zeilen"]:
        if erg.get("gruppen") and z.get("gruppe") and z["gruppe"] != akt:
            akt = z["gruppe"]
            fett.append(len(zeilen))
            zeilen.append([z["nr"].split(".")[0], escape(akt), "", "", ""])
        if z.get("bedarfsposition"):
            zeilen.append([z["nr"], "<i>Bedarfsposition:</i> " + escape(z["bezeichnung"] or ""), escape(z["menge"]),
                           escape(z["einheit_preis"]), "nur EP"])
        else:
            zeilen.append([z["nr"], escape(z["bezeichnung"] or ""), escape(z["menge"]), escape(z["einheit_preis"]),
                           K.eur(z["preis"])])
    for z in erg.get("zusatz", []):
        zeilen.append([z["nr"], escape(z["bezeichnung"]), "1", "Pauschale", K.eur(z["preis"])])
    y = tabelle(d, y, ["Pos.", "Leistung", "Menge", "Einheit", "Betrag"], zeilen, sp,
                ausr=["L", "L", "R", "L", "R"], fett_zeilen=tuple(fett), titel_folgeseite="Ihr Angebot im Überblick")
    y -= 7 * mm
    y = d.platz(y, 50 * mm)
    n = len([z for z in erg["zeilen"] if not z.get("bedarfsposition")]) + len(erg.get("zusatz", []))
    fakten = [("Leistungsumfang", f"{n} Position{'en' if n > 1 else ''} laut Aufstellung")]
    if erg.get("bedarfspositionen_summe"):
        fakten.append(("Bedarfspositionen", "nur nach Beauftragung, Abrechnung zum Einheitspreis"))
    if erg.get("turnus_hinweis"):
        fakten.append(("Hinweis", erg["turnus_hinweis"]))
    fakten.append(("Ausführung", a.get("leistungsbeginn") or "nach Vereinbarung"))
    label = "Preis je Reinigung" if getattr(d, "vertragsart", "") == "vertrag_je_einsatz" else "Gesamtbetrag"
    y = preis_panel(d, y, label, K.eur(erg["gesamt"], 2), steuertext(erg), fakten)
    leistungen_konditionen(d, y, tx, kond)


def angebot_winterdienst(d, erg, tx, kond):
    c, a = d.c, d.a
    y = d.kopf("Ihr Angebot im Überblick")
    y = para(c, escape(tx["intro"]), ML, y, BREITE * 0.82, st(10.5)) - 8 * mm
    y = kaufmotive_block(d, y)
    sp = [14 * mm, 70 * mm, 34 * mm, 24 * mm, BREITE - 142 * mm]
    leistung = {"raeumen_streuen": "Räumen und Streuen", "nur_raeumen": "Räumen",
                "sonderflaeche": "Räumen und Streuen, gesamte Fläche"}
    zeilen = [[z["nr"], escape(z["bezeichnung"]), K.zahl(z["flaeche"]) + " m²",
               escape(leistung.get(z["leistung"], z["leistung"])), K.eur(z["preis_je_einsatz"])] for z in erg["zeilen"]]
    zeilen.append(["", "Preis je Einsatz", "", "", K.eur(erg["preis_je_einsatz"])])
    y = tabelle(d, y, ["Pos.", "Fläche", "Aufmaß", "Leistung", "je Einsatz"], zeilen, sp,
                ausr=["L", "L", "R", "L", "R"], fett_zeilen=(len(zeilen) - 1,), titel_folgeseite="Ihr Angebot im Überblick")
    y -= 7 * mm
    y = d.platz(y, 50 * mm)
    fakten = [("Saison", erg.get("saisonzeitraum") or "nach Vereinbarung")]
    if erg["variante"] == "saison":
        fakten.append(("Enthalten", f"{K.zahl(erg['einsaetze_pauschal'], 0)} Einsätze, Bereitschaftspauschale "
                                    f"{K.eur(erg['bereitschaftspauschale'], 2)}"))
        fakten.append(("Weitere Einsätze", f"je {K.eur(erg['zusatzeinsatz_preis'], 2)}"))
        label, betrag = "Saisonpauschale", erg["gesamt"]
    else:
        fakten.append(("Bereitschaftspauschale", K.eur(erg["bereitschaftspauschale"], 2) + " je Saison"))
        fakten.append(("Abrechnung", "je ausgeführtem Einsatz"))
        label, betrag = "Preis je Einsatz", erg["preis_je_einsatz"]
    y = preis_panel(d, y, label, K.eur(betrag, 2), "netto zzgl. gesetzlicher MwSt.", fakten)
    leistungen_konditionen(d, y, tx, kond)


def vorteile(d, tx):
    c = d.c
    sb = (BREITE - 12 * mm) / 2
    items = tx["vorteile"]
    hoehen = [para_h(escape(v), sb - 8 * mm, st(10)) for v in items]
    rest = getattr(d, "rest_y", None)
    d.rest_y = None
    bedarf = 16 * mm + sum(max(hoehen[i:i + 2]) + 6 * mm for i in range(0, len(items), 2))
    if rest and rest - 4 * mm - bedarf >= FUSS_H + 3 * mm:
        y = rest - 4 * mm
        c.setFillColor(d.P)
        c.setFont(FB, 20)
        c.drawString(ML, y - 16, "Ihre Vorteile mit uns")
        y -= 16 + 9 * mm
    else:
        if rest:
            d.neue_seite()
        y = d.kopf("Ihre Vorteile mit uns")
    for i in range(0, len(items), 2):
        h = max(hoehen[i:i + 2]) + 6 * mm
        for j in range(2):
            if i + j >= len(items):
                continue
            x = ML + j * (sb + 12 * mm)
            d.haken(x, y - 3.6 * mm)
            para(c, escape(items[i + j]), x + 8 * mm, y, sb - 8 * mm, st(10))
        c.setStrokeColor(HAAR)
        c.setLineWidth(0.4)
        c.line(ML, y - h + 2.5 * mm, W - MR, y - h + 2.5 * mm)
        y -= h
    refs = [d.bild_pfad(r) for r in ((d.firma.get("logos") or {}).get("referenzen") or [])]
    refs = [r for r in refs if r]
    bw = d.firma.get("bewertungen") or {}
    zeige_bw = bool(bw.get("google_anzahl") and bw.get("google_sterne"))
    if refs or zeige_bw:
        reihen = (min(len(refs), 8) + 3) // 4 if refs else 0
        y = d.platz(y - 10 * mm, 12 * mm + reihen * 26 * mm + (24 * mm if zeige_bw else 0))
        y = para(c, "Referenzen und Auszeichnungen", ML, y, BREITE, st(12, True)) - 6 * mm
    if refs:
        n = min(len(refs), 4)
        zb = BREITE / n
        reihe_y = y
        for i, r in enumerate(refs[:8]):
            if i and i % n == 0:
                reihe_y -= 26 * mm
            cx = ML + zb * (i % n) + zb / 2
            d.bild(r, cx, reihe_y, zb - 12 * mm, 18 * mm, "mitte")
        y = reihe_y - 26 * mm
    if zeige_bw:
        c.setFillColor(d.P10)
        c.rect(ML, y - 20 * mm, BREITE, 20 * mm, stroke=0, fill=1)
        sterne = float(bw["google_sterne"])
        for i in range(5):
            farbe = HexColor("#F4B400") if i + 0.75 <= sterne else HexColor("#D0D0D0")
            d.stern(ML + 9 * mm + i * 8 * mm, y - 10 * mm, 3.2 * mm, farbe)
        para(c, f"<b>{K.zahl(sterne, 1)} von 5 Sternen</b> aus {int(bw['google_anzahl'])} Google-Bewertungen",
             ML + 52 * mm, y - 7.2 * mm, BREITE - 60 * mm, st(11, False, TEXT))
    d.neue_seite()


def auftrag_seite(d, erg, stadt_datum):
    c, a = d.c, d.a
    y = d.kopf("Auftrag erteilen")
    betrag = K.eur(erg["pauschale"] if erg["abrechnung"] == "monatlich" else erg["gesamt"], 2)
    if erg["abrechnung"] == "saison":
        zusatz = ("Saisonpauschale inkl. Bereitschaftspauschale, netto zzgl. MwSt." if erg.get("variante") == "saison"
                  else f"Bereitschaftspauschale; Einsätze je {K.eur(erg['preis_je_einsatz'], 2)}, netto zzgl. MwSt.")
    elif erg["abrechnung"] == "monatlich":
        zusatz = "monatlich, netto zzgl. MwSt."
    elif d.vertragsart == "vertrag_je_einsatz":
        zusatz = "je Reinigung, netto zzgl. MwSt."
    elif erg.get("steuer") == "13b":
        zusatz = "netto, Steuerschuldnerschaft des Leistungsempfängers"
    else:
        zusatz = "netto zzgl. MwSt."
    y = para(c, f"Hiermit beauftragen wir <b>{escape(d.fi.get('name', ''))}</b> mit der Leistung "
                f"<b>{escape(d.titel_kurz)}</b> zum Preis von <b>{betrag}</b> ({zusatz}) "
                "gemäß diesem Angebot" + (f" Nr. {escape(a['angebots_nr'])}" if a.get("angebots_nr") else "") + ".",
             ML, y, BREITE * 0.85, st(11, False, TEXT, 16)) - 12 * mm
    # Unterschriftsfelder
    k = a.get("kunde") or {}
    felder = [("Ort, Datum", ""), ("Name in Druckbuchstaben", ""), ("Unterschrift", "")]
    sb = (BREITE - 10 * mm) / 2
    yy = y
    para(c, escape(k.get("firma", "Auftraggeber")), ML, yy, sb, st(10, True, d.P))
    yy -= 18 * mm
    for lab, _ in felder:
        c.setStrokeColor(TEXT)
        c.setLineWidth(0.6)
        c.line(ML, yy, ML + BREITE * 0.6, yy)
        c.setFont(F, 8.5)
        c.setFillColor(GRAU)
        c.drawString(ML, yy - 4 * mm, lab)
        yy -= 20 * mm
    y = yy - 2 * mm
    # Nächste Schritte – echte Abfolge, daher nummeriert
    y = d.platz(y, 55 * mm, "Auftrag erteilen")
    y = para(c, "So geht es weiter", ML, y, BREITE, st(12, True)) - 5 * mm
    schritte = d.schritte
    sw = (BREITE - 2 * 8 * mm) / 3
    # Titel und Texte stehen in allen drei Spalten auf derselben Höhe, die Höhe richtet sich nach dem längsten.
    h_titel = max(para_h(escape(t), sw, st(10, True)) for t, _ in schritte)
    h_text = max(para_h(escape(txt), sw, st(9, False, TEXT)) for _, txt in schritte)
    for i, (t, txt) in enumerate(schritte):
        x = ML + i * (sw + 8 * mm)
        c.setFillColor(d.P)
        c.circle(x + 4 * mm, y - 4 * mm, 4 * mm, stroke=0, fill=1)
        c.setFillColor(white)
        c.setFont(FB, 10)
        c.drawCentredString(x + 4 * mm, y - 5.3 * mm, str(i + 1))
        para(c, escape(t), x, y - 11 * mm, sw, st(10, True))
        para(c, escape(txt), x, y - 11 * mm - h_titel - 1 * mm, sw, st(9, False, TEXT))
    y -= 11 * mm + h_titel + 1 * mm + h_text + 8 * mm
    ap = kontaktperson(d)
    kontakt = " oder ".join(x for x in [ap["telefon"], ap["email"]] if x)
    para(c, f"Fragen zum Angebot? {escape(ap['name'])} ist direkt erreichbar: {escape(kontakt)}",
         ML, y, BREITE, st(9.5, False, GRAU))
    d.neue_seite()


STEUER_13B = ("Steuerschuldnerschaft des Leistungsempfängers (§ 13b UStG). "
              "Die Rechnung wird ohne Umsatzsteuer gestellt.")


def steuertext(erg):
    st_ = erg.get("steuer") or "regulaer"
    if st_ not in ("regulaer", "13b"):
        raise K.KalkulationsFehler(f"steuer '{st_}' ungültig (regulaer | 13b).")
    return "netto – " + STEUER_13B if st_ == "13b" else "netto zzgl. gesetzlicher MwSt."


def anlage_aufgabenplan(d, erg):
    y = d.kopf("Anlage 1: Aufgabenplan")
    zeilen = [[escape(z["taetigkeit"]), escape(kurz_turnus(z["turnus"]))] +
              [("●" if t in (z.get("tage") or []) else "") for t in WOCHE] for z in erg["zeilen"]]
    sp = [BREITE - 36 * mm - 7 * 7.5 * mm, 36 * mm] + [7.5 * mm] * 7
    tabelle(d, y, ["Tätigkeit", "Häufigkeit"] + WOCHE, zeilen, sp, ausr=["L", "L"] + ["C"] * 7,
            titel_folgeseite="Anlage 1: Aufgabenplan")
    d.neue_seite()


def anlage_leistungsbeschreibung(d, tx):
    lb = tx.get("leistungsbeschreibung")
    if not lb:
        return
    a = d.a
    titel = "Anlage 1: Leistungsbeschreibung"
    y = d.kopf(titel)
    weg = set(a.get("lb_weglassen") or [])
    extra = set(a.get("lb_zusatz") or [])
    for block in lb:
        punkte = [t["text"] for t in block["punkte"]
                  if t["text"] not in weg and (not t.get("optional") or t["text"] in extra)]
        if not punkte:
            continue
        y = d.platz(y, 30 * mm, titel)
        y = para(d.c, escape(block["titel"]), ML, y, BREITE, st(11.5, True, d.P)) - 3 * mm
        rows = [["●", escape(p)] for p in punkte]
        y = tabelle(d, y, ["", "Leistung"], rows, [10 * mm, BREITE - 10 * mm], ausr=["C", "L"],
                    titel_folgeseite=titel, zebra=False) - 6 * mm
    for zusatz in (a.get("lb_freitext") or []):
        y = d.platz(y, 12 * mm, titel)
        y = para(d.c, escape(zusatz), ML, y, BREITE, st(9.5)) - 2 * mm
    d.neue_seite()


def anlagen(d, erg):
    c, a = d.c, d.a
    y = d.kopf("Anlage 1: Reinigungsplan")
    sp = [62 * mm, 22 * mm, 30 * mm] + [(BREITE - 114 * mm) / 7] * 7
    zeilen = []
    for z in erg["zeilen"]:
        if z.get("flaeche"):
            menge = K.zahl(z["flaeche"]) + " m²"
        elif z.get("zeitansatz") and z.get("anzahl"):
            menge = escape((z.get("basis") or "").split(" x ")[0])
        else:
            menge = "pauschal"
        zeilen.append([escape(z["raum"]), menge, escape(kurz_turnus(z["turnus"]))] +
                      [("●" if t in z["tage"] else "") for t in WOCHE])
    if erg.get("summe_flaeche"):
        zeilen.append(["Gesamtfläche", K.zahl(erg["summe_flaeche"]) + " m²", ""] + [""] * 7)
    y = tabelle(d, y, ["Bereich", "Umfang", "Turnus"] + WOCHE, zeilen, sp,
                ausr=["L", "R", "L"] + ["C"] * 7, fett_zeilen=((len(zeilen) - 1,) if erg.get("summe_flaeche") else ()),
                titel_folgeseite="Anlage 1: Reinigungsplan")
    d.neue_seite()

    lv = _daten("lv_unterhaltsreinigung.json")["bereiche"]
    zu = {}
    for z in erg["zeilen"]:
        if not z.get("raumtyp") and not z.get("lv_bereich"):
            continue
        bid = z.get("lv_bereich") or next((k for k, b in lv.items() if z["raumtyp"] in b["raumtypen"]), "verwaltung_buero")
        zu.setdefault(bid, []).append(z)
    if not zu:
        d.neue_seite()
        return
    extra = set(a.get("lv_zusatz") or [])
    weg = set(a.get("lv_weglassen") or [])
    y = d.kopf("Anlage 2: Leistungsverzeichnis")
    titel2 = "Anlage 2: Leistungsverzeichnis"
    for bid in [k for k in lv if k in zu]:
        b = lv[bid]
        turnusse = sorted({z["turnus"] for z in zu[bid]})
        t_text = turnusse[0] if len(turnusse) == 1 else "gemäß Reinigungsplan"
        tage = sorted({t for z in zu[bid] for t in z["tage"]}, key=WOCHE.index)
        raeume = ", ".join(z["raum"] for z in zu[bid])
        y = d.platz(y, 45 * mm, titel2)
        y = para(c, escape(b["titel"]), ML, y, BREITE, st(11.5, True, d.P)) - 1 * mm
        y = para(c, "Bereiche: " + escape(raeume), ML, y, BREITE, st(8.5, False, GRAU)) - 3 * mm
        rows = []
        for gruppe in ("taetigkeiten", "fussboden"):
            for t in b[gruppe]:
                if t["text"] in weg or (t.get("optional") and t["text"] not in extra):
                    continue
                folgt = "{turnus}" in t["haeufigkeit"]
                h = t["haeufigkeit"].replace("{turnus}", kurz_turnus(t_text))
                rows.append([escape(t["text"]), escape(h)] + [("●" if folgt and tg in tage else "") for tg in WOCHE])
        sp = [BREITE - 36 * mm - 7 * 7.5 * mm, 36 * mm] + [7.5 * mm] * 7
        y = tabelle(d, y, ["Auszuführende Tätigkeit", "Häufigkeit"] + WOCHE, rows, sp,
                    ausr=["L", "L"] + ["C"] * 7, titel_folgeseite=titel2) - 9 * mm
    d.neue_seite()


# ---------------------------------------------------------------- Ableitungen
def kurz_turnus(t):
    return (t.replace(",0 mal täglich", "× täglich").replace(",0 mal wöchentlich", "× wöchentlich")
             .replace(",0 mal jährlich", "× jährlich").replace("1 mal monatlich", "1× monatlich"))


def reinigungstage(erg):
    tage = {t for z in erg.get("zeilen", []) for t in (z.get("tage") or [])}
    return [t for t in WOCHE if t in tage]


def zeiten_je_tag(a, tage):
    z = a.get("zeiten") or {}
    out = {}
    for kurz in WOCHE:
        lang = TAG_LANG[kurz]
        v = z.get(lang, z.get(kurz))
        if v:
            out[kurz] = v
        elif kurz in tage:
            out[kurz] = "nach Vereinbarung"
    return out


MONATLICH = ("unterhaltsreinigung", "hausmeisterservice")


def vertragsart_bestimmen(angebot, erg):
    """vertrag = laufender Vertrag mit Monatspauschale (UR, Hausmeister);
    vertrag_je_einsatz = regelmäßige Ausführung, Preis je Einsatz (z. B. Glas 4x jährlich mit Vertrag);
    einmalig = einmaliger Auftrag."""
    la = angebot["leistungsart"]
    va = angebot.get("vertragsart")
    if la == "winterdienst":
        if va not in (None, "vertrag", "vertrag_saison"):
            raise K.KalkulationsFehler("Winterdienst läuft als Saisonvertrag (vertragsart: vertrag).")
        return "vertrag_saison"
    if la in MONATLICH:
        if va not in (None, "vertrag"):
            raise K.KalkulationsFehler(f"{la} läuft immer als Vertrag (vertragsart: vertrag), nicht '{va}'.")
        return "vertrag"
    va = va or "einmalig"
    if va == "vertrag":
        va = "vertrag_je_einsatz"
    if va not in ("einmalig", "vertrag_je_einsatz"):
        raise K.KalkulationsFehler(f"Unbekannte vertragsart '{va}' (erlaubt: einmalig, vertrag).")
    if va == "vertrag_je_einsatz" and not angebot.get("turnus_hinweis"):
        raise K.KalkulationsFehler("Bei vertragsart 'vertrag' fehlt turnus_hinweis (z. B. 'Vorgesehen: 4 x jährlich').")
    return va


def sperrliste_pruefen(pdf, texte, va):
    """Liest den Text des fertigen PDFs und bricht ab, wenn Begriffe der Sperrliste vorkommen."""
    import subprocess, os, re as _re
    try:
        roh = subprocess.run(["pdftotext", "-enc", "UTF-8", pdf, "-"], capture_output=True, text=True, check=True).stdout
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("HINWEIS: pdftotext nicht verfügbar – Sperrlisten-Prüfung übersprungen. PDF manuell auf "
              "unpassende Vertragsbegriffe prüfen.")
        return
    text = _re.sub(r"-\n(?=[a-zäöüß])", "", roh)
    text = _re.sub(r"\s+", " ", text)
    sl = texte.get("sperrliste") or {}
    treffer = []
    for wort in (sl.get("alle") or []) + (sl.get(va) or []):
        muster = _re.escape(wort)
        if wort == "XX":
            muster = r"\bXX\b"
        if _re.search(muster, text, flags=0 if wort == "XX" else _re.IGNORECASE):
            treffer.append(wort)
    if treffer:
        os.remove(pdf)
        raise K.KalkulationsFehler(
            f"Sperrliste ({va}): {', '.join(treffer)} im PDF gefunden – PDF gelöscht. Text oder Konditionen "
            "anpassen (Leistungs-/Vertragsart prüfen) und neu erzeugen.")


def texte_laden(firma):
    t = _daten("texte.json")
    for la, over in (firma.get("texte") or {}).items():
        if la in t and isinstance(over, dict):
            t[la].update(over)
    return t


def pruefe_firma(firma):
    fi = firma.get("firma") or {}
    fehlend = [f"firma.{k}" for k in ["name", "stadt", "telefon", "email"] if fi.get(k) in (None, "", "XX")]
    if (fi.get("unterzeichner") or {}).get("name") in (None, "", "XX"):
        fehlend.append("firma.unterzeichner.name")
    return fehlend


def pruefe_nachweise(firma, heute):
    """Referenzlogos und Bewertungen müssen regelmäßig bestätigt werden."""
    hinweise = []
    tage_max = int((firma.get("pruefung") or {}).get("nachweise_gueltig_tage", 90))

    def alt(datum):
        if not datum:
            return True
        try:
            dt = datetime.datetime.strptime(str(datum), "%d.%m.%Y").date()
        except ValueError:
            return True
        return (heute - dt).days > tage_max

    logos = firma.get("logos") or {}
    if logos.get("referenzen") and alt(logos.get("referenzen_geprueft_am")):
        hinweise.append(f"Referenzlogos: Prüfdatum fehlt oder älter als {tage_max} Tage – "
                        "beim Nutzer bestätigen lassen, dass Kunden aktuell sind und der Nennung zugestimmt haben.")
    bw = firma.get("bewertungen") or {}
    if bw.get("google_anzahl") and alt(bw.get("stand")):
        hinweise.append(f"Google-Bewertung: Stand fehlt oder älter als {tage_max} Tage – "
                        "aktuelle Anzahl und Sterne beim Nutzer abfragen.")
    return hinweise


def erstelle(angebot, firma, assets, out, entwurf=False, paket=None):
    global _PAKET
    _PAKET = paket
    fehlend = pruefe_firma(firma)
    if fehlend:
        raise K.KalkulationsFehler("firma.yaml unvollständig: " + ", ".join(fehlend))
    erg = paket["ergebnis"] if paket is not None else K.berechne(angebot, firma)
    texte = texte_laden(firma)
    la = angebot["leistungsart"]
    tx = texte.get(la, texte["grundreinigung"])
    titel = angebot.get("titel") or tx["titel"]
    datum = angebot.get("datum") or datetime.date.today().strftime("%d.%m.%Y")
    stadt = (firma.get("firma") or {}).get("stadt", "")
    stadt_datum = f"{stadt}, {datum}" if stadt else datum

    va = vertragsart_bestimmen(angebot, erg)
    fa = firma.get("angebot") or {}
    if va == "vertrag":
        kond = dict(texte["konditionen_standard"])
        if la == "hausmeisterservice":
            kond["Auftragsbedingungen"] = "Ein Vertrag wird vereinbart"
        kond.update(fa.get("konditionen") or {})
    elif va == "vertrag_saison":
        kond = dict(texte["konditionen_winterdienst"])
        if erg.get("variante") == "je_einsatz":
            kond["Abrechnung"] = "je Einsatz nach Ausführung, Bereitschaftspauschale bei Vertragsabschluss"
        kond.update(fa.get("konditionen_winterdienst") or {})
    elif va == "vertrag_je_einsatz":
        kond = dict(texte["konditionen_vertrag_je_einsatz"])
        kond.update(fa.get("konditionen_vertrag_je_einsatz") or {})
    else:
        kond = dict(texte["konditionen_einmalig"])
        kond.update(fa.get("konditionen_einmalig") or {})
    kond.update(angebot.get("konditionen") or {})
    tx = dict(tx)
    if la == "winterdienst" and erg.get("variante") == "je_einsatz":
        tx["intro"] = tx.get("intro_je_einsatz", tx["intro"])
        tx["vorteile"] = tx.get("vorteile_je_einsatz", tx["vorteile"])
    if va == "vertrag_je_einsatz" and tx.get("vorteile_vertrag"):
        tx["vorteile"] = tx["vorteile_vertrag"]
    schl = "vertrag_hausmeister" if la == "hausmeisterservice" else va
    if not entwurf and not str(angebot.get("angebots_nr") or "").strip():
        raise K.KalkulationsFehler(
            "Angebotsnummer fehlt. Ohne Nummer nur mit --entwurf. Nummer aus Mendato bzw. dem Angebotstool "
            "holen (Quelle laut firma.yaml: angebot.nummer_quelle) – niemals selbst vergeben.")

    d = Angebot(out, firma, assets, angebot, entwurf)
    d.vertragsart = va
    d.schritte = texte["schritte"][schl]
    d.titel_kurz = titel
    d.titel_kopf = f"Angebot {titel}" + (f" Nr. {angebot['angebots_nr']}" if angebot.get("angebots_nr") else "")
    deckblatt(d, titel, datum)
    anschreiben(d, texte, stadt_datum, tx["anschreiben_gegenstand"])
    if erg["abrechnung"] == "monatlich":
        angebot_monatlich(d, erg, tx, kond)
    elif erg["abrechnung"] == "saison":
        angebot_winterdienst(d, erg, tx, kond)
    else:
        angebot_einmalig(d, erg, tx, kond)
    vorteile(d, tx)
    auftrag_seite(d, erg, stadt_datum)
    if la == "unterhaltsreinigung" and angebot.get("anlagen", True):
        anlagen(d, erg)
    elif la == "hausmeisterservice" and erg.get("zeilen") and angebot.get("anlagen", True):
        anlage_aufgabenplan(d, erg)
    elif tx.get("leistungsbeschreibung") and angebot.get("anlagen", True):
        anlage_leistungsbeschreibung(d, tx)
    d.c.save()
    sperrliste_pruefen(out, texte, va)

    hinweise = pruefe_nachweise(firma, datetime.date.today())
    if not d.logo_pfad:
        hinweise.append("Firmenlogo nicht gefunden – Firmenname als Text gesetzt. Logo in den Chat hochladen.")
    for bez in ((firma.get("logos") or {}).get("referenzen") or []):
        if not d.bild_pfad(bez):
            hinweise.append(f"Referenzlogo '{bez}' nicht gefunden – nicht im PDF.")
    return erg, hinweise


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--angebot", required=True)
    ap.add_argument("--firma", required=True)
    ap.add_argument("--assets", default=".")
    ap.add_argument("--out", required=True)
    ap.add_argument("--entwurf", action="store_true", help="Wasserzeichen ENTWURF setzen")
    ap.add_argument("--paket", help="Paket vom EMR-Server (Connector). Dann rechnet nicht dieses Skript.")
    a = ap.parse_args()
    with open(a.angebot, encoding="utf-8") as f:
        angebot = json.load(f)
    firma = K.lade_firma(a.firma)
    try:
        paket = None
        if a.paket:
            import ausgabe
            paket = ausgabe.lade_paket(a.paket)
        elif not hasattr(K, "berechne"):
            raise K.KalkulationsFehler("--paket fehlt: In diesem Skill rechnet der EMR-Server. Erst die Funktion "
                                       "kalkulation des Connectors aufrufen und ihr Feld \"paket\" als Datei speichern.")
        erg, hinweise = erstelle(angebot, firma, a.assets, a.out, a.entwurf, paket)
    except K.KalkulationsFehler as e:
        print(f"FEHLER: {e}", file=sys.stderr)
        sys.exit(2)
    except (ArithmeticError, TypeError, ValueError) as e:
        print(f"FEHLER: Ungültige Zahl in angebot.json oder firma.yaml ({type(e).__name__}). Zahlen mit Punkt als "
              "Dezimaltrenner, ohne Anführungszeichen und ohne null angeben.", file=sys.stderr)
        sys.exit(2)
    print(paket["bericht"] if paket is not None else K.bericht(erg))
    for h in hinweise:
        print("HINWEIS:", h)
    print(f"\nPDF erstellt: {a.out}")


if __name__ == "__main__":
    main()
