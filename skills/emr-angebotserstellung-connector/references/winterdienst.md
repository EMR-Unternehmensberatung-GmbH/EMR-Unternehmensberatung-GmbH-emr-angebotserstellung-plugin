# Winterdienst

Leistungsart `winterdienst`, Vertragsart Saisonvertrag (`"vertragsart": "vertrag"`). Methode nach EMR-Winterdienst-
Bibel: **nie nach Stunden**, immer €/m² je Einsatz. Der Stundensatz wird nicht verwendet.

## Rechnung (Skript)
- Fläche = Laufmeter × Räumbreite (EMR-Standard, wenn nicht angegeben) oder `flaeche` direkt (Sonderflächen komplett).
- Preis je Einsatz = Σ Fläche × €/m² (je Fläche kaufmännisch auf volle Euro).
- `"abrechnung_wd": "saison"` (Standard): Saisonpauschale = Preis je Einsatz × Einsätze (EMR-Standard für
  Deutschland, änderbar) + Bereitschaftspauschale. Weitere Einsätze als Anteil der Saisonpauschale (EMR-Standard,
  änderbar).
- `"abrechnung_wd": "je_einsatz"`: Preis je Einsatz + Bereitschaftspauschale; Einsätze nach Aufwand.

## Pflichtangaben (sonst bricht das Skript ab)
- Aufmaß je Fläche: `laufmeter` (+ `raeumbreite`) oder `flaeche` – gemessen, nicht geschätzt (Hausmeister vor Ort
  fragen ist EMR-Best-Practice).
- €/m² je Einsatz: Position `preis_je_m2`, `angebot.preis_je_m2` oder firma.yaml `kalkulation.winterdienst.preis_je_m2`.
- Bereitschaftspauschale: angebot oder firma.yaml (0 = ohne).
Räumbreite, Einsatzzahl, Zusatzeinsatz und Saisonzeitraum: Fehlen sie, setzt der Server die EMR-Standards und nennt
sie im Bericht unter ANNAHMEN. Dem Nutzer zur Bestätigung zeigen.

## Leistung je Fläche (`leistung`)
- `raeumen_streuen` (Standard), `nur_raeumen` (erzeugt Hinweis: geräumte Flächen müssen gestreut werden –
  Kompromiss-Variante anbieten oder schriftlich klären), `sonderflaeche` (Bushaltestelle, Hofdurchgang: gesamte
  Fläche räumen).

## Einordnung (automatisch, ändert nie den Preis)
Der Server ordnet €/m² je Einsatz und Bereitschaftspauschale in die EMR-Preisrahmen ein (Abschnitt EINORDNUNG im
Bericht). Diese Einordnung in einem Satz weitergeben. Rahmenwerte nie selbst nennen.

## Regionale Unterschiede
In Bayern und den Alpen sowie in Österreich und der Schweiz liegen Saison und Einsatzzahl deutlich über dem
deutschen Standard. Dort Saisonzeitraum und Einsätze immer mit dem Nutzer festlegen.

## Rechtliches – nur als Hinweis an den Nutzer, nicht als Zusage im Angebot
- Die geforderte Räumbreite und Räumzeiten regelt die kommunale Satzung (üblich: werktags ab 7 Uhr, sonn- und
  feiertags ab 8/9 Uhr, bis 20 Uhr). Beim Kunden bzw. der Gemeinde prüfen.
- Verkehrssicherung und Haftung im Winterdienstvertrag klar abgrenzen; Betriebshaftpflicht muss Winterdienst abdecken.
- Einsätze mit Zeit und Streumittel dokumentieren.

## Vertragsinhalte (Checkliste für den Nutzer)
Saisonzeitraum, €/m² je Einsatz, Räumbreite, Bereitschaftspauschale separat, Regel für Zusatzeinsätze,
Räumzeiten, Sonn-/Feiertagsregelung, Kündigungsfrist. Optional zwei Varianten anbieten (Saisonpauschale vs. je
Einsatz). Kombination mit Unterhalts- oder Glasreinigung ansprechen.

## Texte
Texte vom EMR-Server → `winterdienst` (Entwurf V1.5, Freigabe durch EMR offen). Konditionen `konditionen_winterdienst`,
Schritte `vertrag_saison`.
