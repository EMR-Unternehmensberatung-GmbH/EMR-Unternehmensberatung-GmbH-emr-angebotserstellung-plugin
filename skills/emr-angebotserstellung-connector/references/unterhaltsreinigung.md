# Unterhaltsreinigung

## Formel (EMR-Standard)
- Monatlich zu reinigende Fläche = Fläche × Monatsfaktor
- Monatsstunden = monatliche Fläche ÷ Leistungswert (m²/h) – oder Zeit je Reinigung × Monatsfaktor (Zeitansatz)
- Monatspauschale = Summe Monatsstunden × Stundensatz (+ Zeitzuschläge, falls vereinbart)
- Rundung: kaufmännisch auf volle Euro (ab ,50 aufrunden) – nur der Endbetrag.

## Monatsfaktor (`katalog` → `turnusse`)
- Wochenbasiert: Häufigkeit pro Woche × 4,33 (z. B. 3× = 12,99; 5× = 21,65; 14-tägig = 2,165)
- Monats-/jahresbasiert: Häufigkeit pro Jahr ÷ 12 (1× monatlich = 1,0; quartalsweise = 0,333)
- **Kalkulationsblatt des Auftraggebers**: Schreibt eine Ausschreibung andere Faktoren vor (z. B. Arbeitstage-
  basiert, 6× = 25,33), je Position `"monatsfaktor": <Wert>` + `begruendung` setzen. Das Skript meldet die
  Abweichung. Nie ohne Vorgabe vom EMR-Standard abweichen.

## Leistungswerte – drei Quellen, eine Reihenfolge
1. **Standardtabelle** (`katalog` → `raumtypen`/`objektarten`, 32 Raumtypen × 9 Objektarten) – immer zuerst.
2. **EMR-Matrix v3** (`katalog` → `lw_matrix`) – wenn Bodenart oder Verschmutzung vom Normalfall abweichen
   (Teppich, Parkett geölt, Naturstein, Praxis-Hygiene, Kita, seltene Reinigung). Position:
   `"lw_matrix": {"bereich": "Büro Teppich Standard", "verschmutzung": "mittel"}`.
   Verschmutzung `"auto"` + `"nutzung": "<Nutzungsprofil>"` leitet die Stufe aus dem Turnus ab (Mapping in der
   Datei). Zwischenstufen wie `hoch_mittel` = Mittelwert. Das Skript nimmt den Wert direkt – Claude überträgt keine
   Zahlen von Hand. Weicht der Matrixwert > 20 % vom Standard ab, kommt ein Prüfhinweis; Begründung eintragen.
3. **Manuell** (`leistungswert` + `begruendung`) – nur mit Wert vom Nutzer.
- Raumtyp nicht in der Tabelle → fachlich nächsten Raumtyp oder Matrix-Bereich vorschlagen und bestätigen lassen.
- Objektart passt nicht exakt (z. B. Kanzlei) → nächstliegende Objektart (Büro) vorschlagen und bestätigen lassen.
- EMR-Regel: Ist die Zeit zu knapp, **Leistungswerte senken, nicht den Stundensatz erhöhen** – Mehraufwand gehört in
  die Stunden.

## Zeitansätze statt Fläche (Container, Aufzug, Treppe je Etage)
Position mit `"zeitansatz": "<id>"` + `"anzahl"` (+ `"minuten"`, wenn der EMR-Wert eine Spanne ist) aus
`katalog` → `zeitansaetze`, oder `"std_je_reinigung"` direkt (Herkunft in `begruendung`). Container werden nie nach
m² gerechnet.

## Hygiene- und Verbrauchsmaterial
Zwei Wege, je nachdem, was der Nutzer hat:
- **Monatsbetrag:** `"zusatz": {"materialkosten_monat": <€>}` (Einkaufspreis plus Aufschlag des Betriebs). Die
  Kalkulation addiert ihn zur Pauschale.
- **Liste:** `"zusatz": {"material": [{"artikel": "Toilettenpapier 3-lagig, 8 Rollen", "menge_monat": 12}, ...]}`.
  Den Preis nimmt das Skript aus `firma.material.preisliste` (gleicher Artikelname) oder aus `"preis"` am Posten,
  rechnet den Aufschlag aus `firma.material.aufschlag_prozent` dazu und addiert die Summe zur Pauschale.
Nie beides in einem Angebot. Lädt der Nutzer eine Preisliste hoch (Excel, CSV, PDF), die Einkaufspreise als
`material.preisliste` in die firma.yaml übernehmen (references/eigene_werte.md, Speichern). Mengen je Monat kommen
vom Nutzer oder aus der Besichtigung – nie schätzen.

## Zeitzuschläge (Nacht, Sonntag, Feiertag)
Nur wenn Reinigung in Zuschlagszeiten vereinbart ist. Position: `"zuschlag": "nacht" | "sonntag" | "feiertag" |
"hoher_feiertag"`, optional `"zuschlag_anteil": 0–1` (Anteil der Stunden in der Zuschlagszeit).
**Sonntag:** Steht „So“ in den Reinigungstagen einer Position und ist kein `"zuschlag"` gesetzt, setzt das Skript
`"zuschlag": "sonntag"` selbst und schreibt es als Annahme in den Kalkulationsbericht. Ohne Zuschlag nur, wenn der
Nutzer es ausdrücklich will: `"ohne_sonntagszuschlag": "<seine Begründung>"` – das steht dann als Annahme im
Kalkulationsbericht. Wird an mehreren Tagen gereinigt (z. B. Mo–So), setzt das Skript den Anteil selbst auf 1 von n
Tagen, wenn `zuschlag_anteil` fehlt.
Rechnung: Monatsstunden × Anteil × Tariflohn (LG aus Tarifdaten auf dem EMR-Server) × RTV-Satz × `kalkulation.zuschlag_faktor`.
Den Zuschlagsfaktor gibt der Betrieb vor (fehlt er, bricht das Skript ab und nennt die EMR-Orientierung).
Die RTV-Sätze für Nacht, Sonn-/Feiertag und hohe Feiertage kennt der Server. Treffen mehrere zusammen, gilt nur der
höchste.
Feiertagseinsätze über das Jahr verteilt (Mischkalkulation 7-Tage-Objekte) als eigene Position mit Turnus `1x_jahr`
und `std_je_reinigung` = Feiertagsstunden im Jahr (vom Nutzer) plus `zuschlag` abbilden – das Skript verteilt auf
den Monat.

## Datenaufnahme
Je Bereich: Bezeichnung, Raumtyp, Fläche in m² (aus Aufmaß oder Grundriss), Turnus.
Unterschiedliche Turnusse je Bereich sind normal (z. B. Büros 3×, Sanitär 5×). Sanitär immer separat erfassen.
Grundriss als Bild/PDF: Flächen ablesen, Ergebnis als Tabelle zur Bestätigung zeigen, erst dann rechnen.
Schließzeiten/Betriebsferien (Schulen, Kitas): im Angebot regeln – entweder voll bezahlt oder Gutschrift; mit dem
Nutzer klären und in `konditionen` festhalten.

## Plausibilität (Skript prüft automatisch)
- Abweichung zu bisherigen Stunden des Kunden (> 20 % → Hinweis). EMR-Regel: Vorgänger-Stunden nie ungeprüft
  übernehmen.
- Vergleich mit Budget; Deckungsbeitrag, wenn Lohnkosten in firma.yaml hinterlegt.
- **EMR-Mindeststunden** (Mindeststunden auf dem EMR-Server): Ø Stunden je Einsatztag gegen Fläche je Einsatztag (nur
  Einordnung). Liegt die Kalkulation deutlich darunter, Leistungsumfang mit dem Nutzer plausibilisieren.
- **Stundensatz**: Einordnung gegen Tariflohn × EMR-SVS-Faktoren (immer) und gegen die EMR-Stundensatz-Matrix, wenn
  `"branche"` gesetzt ist (Liste in `katalog` → `branchen_stundensatz`). Ändert nie den Preis.
- Vorgängerpreis: `besichtigung.vorgaengerpreis_brutto_monat` setzen – das Skript rechnet netto und die implizierten
  Monatsstunden beim Stundensatz des Betriebs aus und stellt sie den kalkulierten gegenüber (nur Einordnung).

## Angebot
Monatliche Pauschale auf der Angebotsseite, Anlage 1 Reinigungsplan (Bereiche, Flächen, Turnus – ohne Einzelpreise
und ohne Stunden), Anlage 2 Leistungsverzeichnis je Bereich (Leistungsverzeichnis vom EMR-Server).
EMR-Regel: Stunden nie im Angebot nennen – die Kalkulation basiert auf Leistungswerten und Leistungsverzeichnis.
