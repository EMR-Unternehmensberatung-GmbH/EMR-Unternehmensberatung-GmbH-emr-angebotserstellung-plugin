# Hausmeisterservice

Monatspauschale = Monatsstunden × Stundensatz (firma.yaml `hausmeisterservice`), kaufmännisch auf volle Euro.

## Zwei Wege
1. **Tätigkeiten** (bevorzugt): `positionen` mit `taetigkeit`, `turnus` und `std_je_einsatz` (aus Besichtigung) oder
   `zeitansatz` aus `katalog` → `zeitansaetze` (z. B. `aufzug`, `treppenhaus_etage_buero`). Ist der EMR-Wert eine
   Spanne, die Minuten beim Nutzer erfragen. Monatsstunden = Zeit je Einsatz × Monatsfaktor.
2. **Monatsstunden direkt**: `stunden_pro_monat` – wenn der Nutzer die Summe nennt.

## EMR-Orientierung (nur zur Plausibilisierung, Zeiten kommen vom Nutzer)
- Treppenhaus MFH: Die EMR-Quellen zur Zeit je Einsatz widersprechen sich. Zeit immer beim Nutzer erfragen, ebenso
  Zu- oder Abschläge für Verschmutzung und Hausart.
- Aufzug nie mit einer knappen Pauschale von wenigen Minuten ansetzen, Zeit beim Nutzer erfragen.
- Bereitstellungspauschale nur bei Sonderaufträgen, nie bei laufenden Monatsverträgen.
- Grünpflege laut EMR pauschal je Einsatz (nicht nach Stunden) – als Einmal-/Sonderauftrag mit Einheitspreis je
  Ausführung kalkulieren, Preis vom Nutzer.
- Winterdienst: eigene Leistungsart (`references/winterdienst.md`).
- Schließzeiten, Schlüssel und Alarmcodes vor dem ersten Einsatz klären und im Angebot festhalten.

Grundlage für den Aufgabenplan: „EMR-G – Leistungsverzeichnis – Hausmeisterservice“ (Google Drive) – noch nicht im
Skill hinterlegt; das PDF enthält deshalb keine LV-Anlage.
