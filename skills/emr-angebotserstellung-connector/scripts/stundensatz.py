#!/usr/bin/env python3
"""
Schneller Stundensatz-Rechner (Verrechnungssatz netto je Stunde).

Gleiche Bausteine wie die Mendato-Kalkulation: Grundlohn, Lohnnebenkosten %, Maschinen/Material %,
Gemeinkosten %, Wagnis und Gewinn %. Alle Prozentwerte kommen vom Nutzer – der Skill setzt keine
Standardwerte ein.

Rechenweg (transparent, jeder Schritt wird ausgegeben):
  Lohnkosten        = Grundlohn × (1 + Lohnnebenkosten %)
  + Maschinen/Mat.  = Lohnkosten × Maschinen/Material %
  + Gemeinkosten    = (Lohnkosten + Maschinen/Mat.) × Gemeinkosten %
  = Selbstkosten
  + Wagnis/Gewinn   = Selbstkosten × Wagnis/Gewinn %
  = Verrechnungssatz (auf 0,10 € gerundet, kaufmännisch)

Aufruf:
  python3 stundensatz.py --lohn 14.50 --lnk 70 --gk 15 --gewinn 10 [--material 5]
"""
import argparse
from decimal import Decimal, ROUND_HALF_UP


def d(x):
    return Decimal(str(x))


def berechne(lohn, lnk, gk, gewinn, material=0):
    lohn, lnk, gk, gewinn, material = d(lohn), d(lnk), d(gk), d(gewinn), d(material)
    if lohn <= 0:
        raise ValueError("Grundlohn muss größer 0 sein.")
    lohnkosten = lohn * (1 + lnk / 100)
    mat = lohnkosten * material / 100
    gemein = (lohnkosten + mat) * gk / 100
    selbst = lohnkosten + mat + gemein
    gew = selbst * gewinn / 100
    satz = (selbst + gew).quantize(Decimal("0.1"), ROUND_HALF_UP)
    return {
        "grundlohn": float(lohn), "lohnkosten": float(lohnkosten.quantize(Decimal("0.01"), ROUND_HALF_UP)),
        "maschinen_material": float(mat.quantize(Decimal("0.01"), ROUND_HALF_UP)),
        "gemeinkosten": float(gemein.quantize(Decimal("0.01"), ROUND_HALF_UP)),
        "selbstkosten": float(selbst.quantize(Decimal("0.01"), ROUND_HALF_UP)),
        "wagnis_gewinn": float(gew.quantize(Decimal("0.01"), ROUND_HALF_UP)),
        "stundensatz": float(satz),
    }


def eur(v):
    return f"{v:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lohn", required=True, type=float, help="Grundlohn €/h (z. B. Tariflohn der Lohngruppe)")
    ap.add_argument("--lnk", required=True, type=float, help="Lohnnebenkosten in %")
    ap.add_argument("--gk", required=True, type=float, help="Gemeinkosten in %")
    ap.add_argument("--gewinn", required=True, type=float, help="Wagnis und Gewinn in %")
    ap.add_argument("--material", default=0, type=float, help="Maschinen/Material in % (optional)")
    a = ap.parse_args()
    r = berechne(a.lohn, a.lnk, a.gk, a.gewinn, a.material)
    print(f"Grundlohn                    {eur(r['grundlohn']):>12}")
    print(f"+ Lohnnebenkosten {a.lnk:>5.1f} %  = Lohnkosten {eur(r['lohnkosten']):>12}")
    if a.material:
        print(f"+ Maschinen/Material {a.material:>4.1f} %   {eur(r['maschinen_material']):>12}")
    print(f"+ Gemeinkosten {a.gk:>5.1f} %          {eur(r['gemeinkosten']):>12}")
    print(f"= Selbstkosten                {eur(r['selbstkosten']):>12}")
    print(f"+ Wagnis/Gewinn {a.gewinn:>5.1f} %        {eur(r['wagnis_gewinn']):>12}")
    print(f"= VERRECHNUNGSSATZ            {eur(r['stundensatz']):>12} je Stunde netto")
    print("Rechenweg mit dem Nutzer bestätigen. Weicht eure Mendato-Kalkulation ab, gilt die Logik des Betriebs.")


if __name__ == "__main__":
    main()
