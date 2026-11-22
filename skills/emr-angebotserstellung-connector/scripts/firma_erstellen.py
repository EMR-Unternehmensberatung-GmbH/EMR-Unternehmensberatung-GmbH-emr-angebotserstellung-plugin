#!/usr/bin/env python3
"""
Erzeugt die firma.yaml als echte Datei (nicht nur als Text im Chat).

Eingabe: JSON mit den gesammelten Firmendaten (gleiche Struktur wie assets/firma.vorlage.yaml, nur die
bekannten Felder). Fehlende Felder werden aus der Vorlage übernommen. Das Skript prüft Pflichtfelder,
gibt offene Punkte aus und schreibt die Datei standardmäßig nach /mnt/user-data/outputs/firma.yaml.

Aufruf:
  python3 firma_erstellen.py --daten firma_daten.json [--alt firma.yaml] [--out /mnt/user-data/outputs/firma.yaml]
  --alt: bestehende firma.yaml, die aktualisiert wird (z. B. neuer Stundensatz).
"""
import argparse
import copy
import datetime
import json
import os
import sys

import yaml

HIER = os.path.dirname(os.path.abspath(__file__))
VORLAGE = os.path.join(HIER, "..", "assets", "firma.vorlage.yaml")


SCHEMA_VERSION = 2


def mischen(basis, neu):
    for k, v in (neu or {}).items():
        if k == "regeln_entfernen":
            continue
        if k == "regeln" and isinstance(v, list) and isinstance(basis.get(k), list):
            # Regeln des Betriebs werden ergänzt, nie überschrieben (Duplikate entfallen)
            basis[k] = basis[k] + [r for r in v if r not in basis[k]]
        elif isinstance(v, dict) and isinstance(basis.get(k), dict):
            mischen(basis[k], v)
        else:
            basis[k] = v
    weg = (neu or {}).get("regeln_entfernen")
    if weg and isinstance(basis.get("regeln"), list):
        basis["regeln"] = [r for r in basis["regeln"] if r not in weg]
    return basis


def ergaenze_neue_felder(alt, vorlage):
    """Bei einem Update nur fehlende Hauptbereiche aus der Vorlage ergänzen – vorhandene Werte des Betriebs
    (auch bewusst gelöschte Konditionen, eigene_werte, Texte) bleiben unverändert."""
    for k, v in vorlage.items():
        if k not in alt:
            alt[k] = copy.deepcopy(v)
    # Neue Unterfelder, die es früher nicht gab (V1.9): leer ergänzen, damit der Betrieb sie sieht.
    if isinstance(alt.get("firma"), dict) and "kontaktperson" not in alt["firma"]:
        alt["firma"]["kontaktperson"] = copy.deepcopy((vorlage.get("firma") or {}).get("kontaktperson"))
    alt["schema_version"] = SCHEMA_VERSION
    return alt


def leer(v):
    return v in (None, "", "XX") or (isinstance(v, str) and v.strip() in ("", "XX"))


def pruefen(f):
    fehlt, offen = [], []
    fi = f.get("firma") or {}
    for k in ["name", "strasse", "plz_ort", "stadt", "telefon", "email"]:
        if leer(fi.get(k)):
            fehlt.append(f"firma.{k}")
    if leer((fi.get("unterzeichner") or {}).get("name")):
        fehlt.append("firma.unterzeichner.name")
    saetze = (f.get("kalkulation") or {}).get("stundensaetze") or {}
    if not any(not leer(v) for v in saetze.values()):
        fehlt.append("kalkulation.stundensaetze (mindestens eine Leistungsart)")
    q = (f.get("angebot") or {}).get("nummer_quelle")
    if q not in ("mendato_mcp", "mendato_manuell", "anderes_tool"):
        fehlt.append("angebot.nummer_quelle (mendato_mcp | mendato_manuell | anderes_tool)")
    for k in ["geschaeftsfuehrer", "registergericht", "handelsregister"]:
        if leer(fi.get(k)):
            offen.append(f"firma.{k} (Fußzeile)")
    if leer(fi.get("ust_id")) and leer(fi.get("steuernummer")):
        offen.append("firma.ust_id oder firma.steuernummer (Fußzeile)")
    bank = f.get("bank") or {}
    if leer(bank.get("iban")):
        offen.append("bank.iban/bic/name (Fußzeile)")
    if leer((f.get("logos") or {}).get("eigenes")):
        offen.append("logos.eigenes (Logo-Dateiname)")
    nicht_angeboten = [k for k, v in saetze.items() if leer(v)]
    return fehlt, offen, nicht_angeboten


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--daten", required=True, help="JSON mit den bekannten Firmendaten")
    ap.add_argument("--alt", help="bestehende firma.yaml, die aktualisiert wird")
    ap.add_argument("--out", default="/mnt/user-data/outputs/firma.yaml")
    a = ap.parse_args()
    with open(VORLAGE, encoding="utf-8") as fh:
        vorlage = yaml.safe_load(fh)
    if a.alt:
        with open(a.alt, encoding="utf-8") as fh:
            basis = ergaenze_neue_felder(yaml.safe_load(fh) or {}, vorlage)
    else:
        basis = vorlage
    with open(a.daten, encoding="utf-8") as fh:
        neu = json.load(fh)
    f = mischen(copy.deepcopy(basis), neu)
    for k, v in list(((f.get("kalkulation") or {}).get("stundensaetze") or {}).items()):
        if v == "XX":
            f["kalkulation"]["stundensaetze"][k] = None
    alt_anzahl = None
    if a.alt:
        ew = basis.get("eigene_werte") or {}
        alt_anzahl = sum(len(ew.get(k) or []) for k in ("leistungswerte", "zeitansaetze", "positionen", "regeln"))
    fehlt, offen, nicht = pruefen(f)
    kopf = (f"# firma.yaml – Stammdaten {f['firma'].get('name', '')}\n"
            f"# Erstellt/aktualisiert am {datetime.date.today():%d.%m.%Y} mit dem EMR-Angebots-Skill.\n"
            "# Diese Datei in die Projektdateien legen (vorhandene firma.yaml ersetzen).\n"
            "# Stundensatz null = Leistung wird nicht angeboten.\n"
            "# eigene_werte = Werte und Regeln dieses Betriebs. Sie bleiben bei Skill-Updates erhalten.\n\n")
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as fh:
        fh.write(kopf)
        yaml.safe_dump(f, fh, allow_unicode=True, sort_keys=False, width=110)
    with open(a.out, encoding="utf-8") as fh:
        yaml.safe_load(fh)  # Lesetest
    print(f"DATEI GESCHRIEBEN: {os.path.abspath(a.out)}")
    if fehlt:
        print("PFLICHT FEHLT (vor dem ersten Angebot klären): " + "; ".join(fehlt))
    if offen:
        print("OPTIONAL OFFEN (Fußzeile/Logo, kann nachgereicht werden): " + "; ".join(offen))
    if nicht:
        print("Ohne Stundensatz (gilt als nicht angeboten): " + ", ".join(nicht))
    ew = f.get("eigene_werte") or {}
    n = {k: len(ew.get(k) or []) for k in ("leistungswerte", "zeitansaetze", "positionen", "regeln")}
    if any(n.values()):
        print("BETRIEBSWERTE: " + ", ".join(f"{k} {v}" for k, v in n.items() if v))
    if alt_anzahl is not None and sum(n.values()) < alt_anzahl and not neu.get("eigene_werte", {}).get("regeln_entfernen"):
        print("WARNUNG: Die neue Datei enthält weniger Betriebswerte als die alte – nicht übernehmen, erst prüfen.")
    sys.exit(0)


if __name__ == "__main__":
    main()
