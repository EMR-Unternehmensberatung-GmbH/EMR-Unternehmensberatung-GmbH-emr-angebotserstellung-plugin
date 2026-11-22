# Schema angebot.json

Eine Datei je Angebot. Claude schreibt sie, das Skript rechnet daraus.

## Gemeinsame Felder
```json
{
  "leistungsart": "unterhaltsreinigung | glasreinigung | grundreinigung | einmalauftrag | baureinigung | hausmeisterservice | winterdienst",
  "angebots_nr": "AN-2026-014",
  "datum": "14.10.2026",
  "titel": "nur bei einmalauftrag: z. B. 'Baureinigung' (sonst Standardtitel)",
  "kunde": {"firma": "...", "anrede": "Frau | Herr | null", "ansprechpartner": "Dr. Anna Beispiel",
            "strasse": "...", "plz_ort": "..."},
  "objekt": {"strasse": "...", "plz_ort": "..."},
  "stundensatz": null,
  "konditionen": {"Gültigkeit des Angebots": "6 Wochen"},
  "besichtigung": {
    "objektart": "...", "bisher": "...", "zufriedenheit": "...", "wechselgruende": "...",
    "bisherige_stunden_monat": 55, "mitarbeiter_bisher": 2,
    "budget_monat": 1600, "budget": null,
    "prioritaeten": ["...", "...", "..."], "region": "..."
  }
}
```
- `stundensatz`: nur setzen, wenn der Nutzer für dieses Angebot ausdrücklich abweicht. Sonst gilt firma.yaml.
- `kunde.ansprechpartner` mit vollem Namen ohne „Herr/Frau“ (für Adressblock); die Anrede steht in `anrede`.
- `kontaktperson` (optional, `{"name", "funktion", "telefon", "email"}`): wer beim Betrieb für dieses Angebot
  Ansprechpartner ist („Ihr direkter Draht“, Deckblatt, Auftragsseite), wenn es nicht `firma.kontaktperson` bzw. der
  Unterzeichner sein soll. Leere Telefon/E-Mail → die der Firma.
  Briefanrede automatisch: akademischer Titel + Nachname („Sehr geehrte Frau Dr. Beispiel“).
  Abweichend: `anrede_name` setzen (z. B. bei Doppelnamen).
- `besichtigung.bisherige_stunden_monat`, `budget_monat` und `vorgaengerpreis_brutto_monat` lösen automatische Vergleiche aus.
- UR: Hygienematerial entweder als `zusatz.materialkosten_monat` (Betrag) oder als `zusatz.material` (Liste mit
  `artikel`, `menge_monat`, optional `preis`) – references/unterhaltsreinigung.md.

## Unterhaltsreinigung
```json
{
  "objektart": "Büro",
  "positionen": [
    {"raum": "Büros EG", "raumtyp": "Büro", "flaeche": 380, "turnus": "3x_woche", "tage": ["Mo", "Mi", "Fr"]},
    {"raum": "Sanitär", "raumtyp": "Toilette", "flaeche": 32, "turnus": "5x_woche",
     "tage": ["Mo", "Di", "Mi", "Do", "Fr"],
     "leistungswert": 70, "begruendung": "stark frequentiert, 40 MA auf 4 WC"}
  ],
  "kaufmotive": [
    {"motiv": "Verlässlichkeit", "umsetzung": "Feste Reinigungskraft und geplante Vertretung bei Urlaub und Krankheit."}
  ],
  "leistungsbeginn": "01.11.2026",
  "zeiten": {"Montag": "18:00 – 21:00 Uhr", "Dienstag": "", "Mittwoch": "18:00 – 21:00 Uhr",
             "Donnerstag": "", "Freitag": "18:00 – 21:00 Uhr", "Samstag": "", "Sonntag": "", "Feiertage": ""},
  "lv_zusatz": ["Kaffeemaschine gemäß Kundenvorgabe reinigen"],
  "lv_weglassen": [],
  "anlagen": true
}
```
- `objektart`: Büro, Fitnessstudio & Spa, Gastronomie, Hotel, Industrie, Schule, Kindergarten, Einzelhandel, Praxis.
- `raumtyp`: exakt wie in `katalog` → `raumtypen`/`objektarten`.
- `turnus`: ID aus `katalog` → `turnusse` (z. B. `5x_woche`, `14taegig`, `1x_monat`).
- `tage`: Reinigungstage je Bereich (Mo–So). Optional im Schnellangebot: fehlen sie, setzt das Skript
  Standardtage je Turnus und meldet sie unter ANNAHMEN. Anzahl muss zum Turnus passen (3x_woche = 3 Tage).
  Bei 14-tägig/monatlich den Tag angeben, an dem gereinigt wird. Erscheinen im Reinigungsplan und LV.
- `zeiten`: Uhrzeit je Tag („18:00 – 21:00 Uhr“), Schlüssel als Tagesname (Montag …) und `Feiertage`.
  Fehlt die Uhrzeit für einen Reinigungstag, steht „nach Vereinbarung“.
- `kaufmotive`: max. 3; nur bestätigte Umsetzungen. Leer lassen, wenn aus der Besichtigung nichts vorliegt.
- `lv_bereich` (optional je Position): `verwaltung_buero | sanitaer | sozialraum_kueche | treppe`.
- `lv_zusatz`: optionale LV-Tätigkeiten (in der JSON mit `optional: true`) exakt im Wortlaut aufnehmen.
- `branche` (optional): Einordnung des Stundensatzes in die EMR-Stundensatz-Matrix (Namen in
  `katalog` → `branchen_stundensatz`, z. B. „Büro Standard“, „Kita / Kindergarten“).

Weitere Positionsarten (statt `flaeche` + Standard-Leistungswert):
```json
{"raum": "Bürocontainer", "zeitansatz": "buerocontainer", "anzahl": 3, "turnus": "1x_woche"},
{"raum": "Sanitärcontainer", "zeitansatz": "sanitaercontainer_klein", "anzahl": 1, "minuten": 18, "turnus": "2x_woche"},
{"raum": "Treppenhaus", "std_je_reinigung": 1.25, "turnus": "1x_woche", "begruendung": "Besichtigung"},
{"raum": "Büros Teppich", "raumtyp": "Büro", "flaeche": 210, "turnus": "3x_woche",
 "lw_matrix": {"bereich": "Büro Teppich Standard", "verschmutzung": "mittel"}, "begruendung": "Teppichboden"},
{"raum": "Verkaufsfläche", "raumtyp": "Verkaufsraum (maschinell)", "flaeche": 1000, "turnus": "6x_woche",
 "monatsfaktor": 25.3333, "begruendung": "Vorgabe Kalkulationsblatt AG", "zuschlag": "nacht", "zuschlag_anteil": 0.5}
```

## Glas-, Grund-, Einmalauftrag
```json
{
  "positionen": [
    {"bezeichnung": "Glasreinigung 2-seitig mit Rahmen, Bockleiter und Teleskopstange, hoher Verschmutzungsgrad",
     "flaeche": 193.73, "leistungswert": 18, "material": 0, "erschwernisse": ["Bockleiter"]},
    {"bezeichnung": "Reinigung Jalousien", "stunden": 6}
  ],
  "zusatz": {"materialkosten": 0, "fahrtkosten": 35},
  "turnus_hinweis": "Die Preise gelten je Reinigung. Vorgesehen: 4 x jährlich."
}
```
- Je Position entweder `flaeche`/`menge` + `leistungswert` (m²/h), `lw_matrix`, `stunden` oder
  `einheitspreis` + `menge` + `einheit` + `ep_quelle` (Einheitspreis vom Nutzer/LV, z. B. Stück, lfm, h, m³).
  Oder `betriebswert` (Schlüssel aus firma.yaml › eigene_werte.positionen) + `menge`: Bezeichnung, Einheit und
  Einheitspreis bzw. Leistungswert kommen aus der firma.yaml; Werte in der Position haben Vorrang.
- `bedarfsposition: true` → berechnet, PDF zeigt „nur EP“, nicht in der Summe.
- `vergleich`: Einordnung in EMR-Preisrahmen, z. B. `{"spanne": "gr_elastisch"}` oder
  `{"tabelle": "glas", "zeile": "Fenster Standard 2-Seiten", "frequenz": "quartal"}` (siehe `katalog` → `preisrahmen`).
- Grundreinigung: `ohne_moebel: true`, wenn kein Mobiliar zu räumen ist (sonst Prüfhinweis).
- `menge_anzeige` / `einheit_preis_anzeige` optional, wenn die Spalten anders lauten sollen.

## Hausmeisterservice
```json
{"stunden_pro_monat": 24, "zeiten": {"Montag": "08:00 – 12:00 Uhr"}}
```
oder mit Tätigkeiten:
```json
{"positionen": [
  {"taetigkeit": "Treppenhausreinigung", "std_je_einsatz": 2.25, "turnus": "1x_woche", "tage": ["Mi"]},
  {"taetigkeit": "Aufzugskabinen", "zeitansatz": "aufzug", "anzahl": 2, "minuten": 12, "turnus": "1x_woche"}]}
```

## Winterdienst
```json
{"leistungsart": "winterdienst", "vertragsart": "vertrag",
 "positionen": [
   {"bezeichnung": "Gehweg Vorderseite", "laufmeter": 270, "preis_je_m2": 1.05, "leistung": "raeumen_streuen"},
   {"bezeichnung": "Bushaltestelle", "flaeche": 60, "preis_je_m2": 2.40, "leistung": "sonderflaeche"}],
 "abrechnung_wd": "saison", "einsaetze_pauschal": 12, "zusatzeinsatz_prozent": 15,
 "bereitschaftspauschale": 120, "saisonzeitraum": "15.11.2026 – 15.03.2027"}
```
- `raeumbreite` je Position optional (sonst EMR-Standard). `preis_je_m2` alternativ auf Angebotsebene oder in firma.yaml.
