"""Hilfen für Tabelle und PDF, wenn gerechnet wird, ohne dass kalkulation.py im Skill liegt.

Im Connector-Paket rechnet der EMR-Server. Der Skill bekommt von dort ein Paket (Ergebnis, Bericht,
Tabellendaten, Texte) und setzt daraus Tabelle und PDF. Für die Zahlenformate braucht er nur diese
Funktionen. Sie entsprechen denen in kalkulation.py (ein Test prüft das).
"""
import json
from decimal import Decimal, ROUND_HALF_UP


class KalkulationsFehler(Exception):
    pass


def lade_firma(pfad):
    with open(pfad, encoding="utf-8") as f:
        if pfad.endswith((".yaml", ".yml")):
            import yaml
            return yaml.safe_load(f) or {}
        return json.load(f)


def lade_paket(pfad):
    """Paket aus der Funktion kalkulation des Connectors (Feld "paket"), als Datei gespeichert."""
    with open(pfad, encoding="utf-8") as f:
        p = json.load(f)
    if not isinstance(p, dict) or "ergebnis" not in p or "daten" not in p:
        raise KalkulationsFehler("Paketdatei unvollständig: Felder ergebnis und daten fehlen. Das Feld \"paket\" "
                                 "aus der Antwort der Funktion kalkulation unverändert speichern.")
    return p


def d(x):
    return Decimal(str(x))


def zahl(x, nachkomma=2):
    q = d(x).quantize(Decimal(1).scaleb(-nachkomma), rounding=ROUND_HALF_UP)
    s = f"{q:,.{nachkomma}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def eur(betrag, nachkomma=2):
    return zahl(betrag, nachkomma) + " €"
