# Onboarding: firma.yaml anlegen

Einmal pro Gebäudereinigung. Ziel: in wenigen Minuten eine vollständige `firma.yaml` – mit so wenig
Fragen wie möglich. **Erst selbst recherchieren, dann nur das Fehlende fragen.**

## 1. Selbst recherchieren (vor der ersten Frage)
Firmenname bzw. Webseite aus dem Chat, dem Projektnamen oder den Projektdateien nehmen. Fehlt beides:
genau diese eine Frage stellen („Wie heißt die Firma bzw. wie lautet die Webseite?“).

Dann in dieser Reihenfolge suchen, soweit die Werkzeuge verfügbar sind:
1. **Projektdateien und Uploads**: vorhandene Angebote, Briefbogen, Logo, alte firma.yaml.
2. **Webseite der Firma**: Startseite und **Impressum** abrufen (Websuche/Seitenabruf). Aus dem Impressum:
   Firmenname, Straße, PLZ/Ort, Telefon, E-Mail, Webseite, Geschäftsführung, Registergericht,
   Handelsregisternummer, USt-IdNr. bzw. Steuernummer.
3. **Frühere Chats / Claude-Erinnerung** (falls verfügbar): Stundensätze oder Nummernquelle, die der Nutzer
   schon genannt hat – nur übernehmen, wenn eindeutig, und zur Bestätigung zeigen.
4. **Mendato-Connector** (falls verbunden): nur prüfen, ob er funktioniert → `nummer_quelle: mendato_mcp`
   vorschlagen.

Gefundene Werte als kompakte Tabelle zeigen (Feld · Wert · Quelle mit Link) und mit **einer** Frage
bestätigen lassen. Nichts übernehmen, was nicht eindeutig auf derselben Firma steht.

## 2. Nur das Fehlende fragen – in einer gebündelten Nachricht
Pflicht:
- **Stundensatz je angebotener Leistungsart** (Unterhaltsreinigung, Glas, Grund, Sonder/Einmal, Bau,
  Hausmeister). Nicht angebotene Leistungen bleiben leer. Ist der Nutzer unsicher: den
  Stundensatz-Rechner anbieten (Abschnitt unten). Das Kalkulationsskript ordnet jeden Satz später automatisch
  gegen Tariflohn und EMR-SVS-Faktoren ein.
- **Winterdienst** (nur wenn angeboten): €/m² je Einsatz und Bereitschaftspauschale – kein Stundensatz.
- **Unterzeichner** (Name, Funktion) – falls nicht aus dem Impressum klar.
- **Ansprechpartner für Auftraggeber** (`firma.kontaktperson`): Steht im Angebot unter „Ihr direkter Draht“ jemand
  anderes als der Unterzeichner, z. B. ein Vertriebsmitarbeiter? Dann Name, Funktion, Telefon und E-Mail. Sonst leer.
- **Angebotsnummer**: Mendato mit Connector, Mendato ohne Connector oder anderes Tool (Name)?
- **Logo**: falls nicht im Projekt – in den Chat hochladen lassen.

Optional, in derselben Nachricht kurz anbieten:
- Bankverbindung (Bank, IBAN, BIC) für die Fußzeile – nur vom Nutzer, nicht schätzen.
- **Zertifikate und Auszeichnungen** – konkret nachfragen, Betriebe vergessen das sonst: Qualitätsmanagement (z. B.
  ISO 9001), Umweltmanagement (z. B. ISO 14001), Arbeitsschutz (z. B. ISO 45001, SCC), Meisterbetrieb oder
  Innungsmitgliedschaft, Gütezeichen, Weiterbildungen und Sachkundenachweise der Mitarbeiter (z. B. Desinfektion,
  Hygiene). Je Zertifikat das Logo oder Siegel als Bilddatei hochladen lassen. Nur, was der Betrieb wirklich hat
  und belegen kann – nichts aus der Webseite ableiten, ohne dass der Nutzer es bestätigt.
- Referenzlogos von Kunden (nur echte Kunden mit Zustimmung), Google-Bewertung (aktuelle Zahl).

**Nicht fragen:** Lohnkosten, Deckungsbeitrag, Prüfschwellen, Konditionen, Farben, Zuschlagsfaktor (erst wenn
ein Angebot Nacht-, Sonntags- oder Feiertagsarbeit enthält).
- Konditionen: EMR-Standard aus der Vorlage übernehmen; in einem Satz sagen, dass sie änderbar sind.
- Farben: `auto` – das PDF nimmt die markanteste Farbe aus dem Logo. Nur auf Wunsch einen HEX-Wert setzen.

## 3. Datei erzeugen – immer als Datei, nie nur als Text
1. Gesammelte Werte als JSON nach `/home/claude/firma_daten.json` schreiben (Struktur wie
   `assets/firma.vorlage.yaml`, nur bekannte Felder).
2. ```bash
   python3 <skill-pfad>/scripts/firma_erstellen.py --daten /home/claude/firma_daten.json \
     --out /mnt/user-data/outputs/firma.yaml
   ```
   Bei einer Änderung einer bestehenden Datei zusätzlich `--alt <pfad>/firma.yaml`.
3. Die Datei mit dem Werkzeug zum Bereitstellen von Dateien ausgeben (z. B. `present_files` mit
   `/mnt/user-data/outputs/firma.yaml`), damit eine Datei-Karte erscheint. **Den YAML-Inhalt nie nur
   in den Chat schreiben.** Steht kein solches Werkzeug zur Verfügung, den Pfad nennen und das sagen.
4. Dem Nutzer in zwei Sätzen sagen: Datei über die Datei-Karte in die Projektdateien übernehmen bzw.
   die alte firma.yaml ersetzen; Logo ebenfalls in die Projektdateien legen. Claude kann Projektdateien
   aus einem Chat nicht selbst ändern.
5. Die vom Skript gemeldeten offenen Punkte in einer Zeile nennen (z. B. „IBAN für die Fußzeile fehlt –
   kann jederzeit nachgereicht werden“).
6. Zugang zum EMR-Connector prüfen (`zugang_pruefen`), wie in `references/rueckmeldung.md`, Abschnitt
   „Verbindung prüfen“.

## Stundensatz-Rechner (nur auf Wunsch oder wenn kein Satz vorliegt)
Abfragen (alles vom Nutzer, keine Vorschläge für Prozentwerte):
Grundlohn €/h, Lohnnebenkosten %, Gemeinkosten %, Wagnis und Gewinn %, optional Maschinen/Material %.
```bash
python3 <skill-pfad>/scripts/stundensatz.py --lohn 14.25 --lnk 70 --gk 15 --gewinn 8 [--material 5]
```
Rechenweg zeigen, Satz bestätigen lassen und in `kalkulation.stundensaetze` übernehmen. Die errechneten
Lohnkosten je Stunde zusätzlich als `kalkulation.lohnkosten_pro_stunde` speichern – dann zeigt der
Kalkulationsbericht den Deckungsbeitrag automatisch, ohne dass danach gefragt wird.
Die Bausteine entsprechen der Mendato-Kalkulation (Grundlohn, Lohnnebenkosten, Gemeinkosten,
Wagnis/Gewinn, Maschinen/Material). Rechnet der Betrieb in Mendato anders, gilt seine Logik.

## Eigene Werte
Im Onboarding nicht abfragen. Der Block `eigene_werte` bleibt leer und füllt sich im Alltag, wenn der Betrieb
Werte als seinen Standard bestätigt (`references/eigene_werte.md`). Hat der Betrieb schon eine Liste eigener
Leistungswerte oder Preise, darf er sie hochladen – Werte nur übernehmen, wenn eindeutig, und bestätigen lassen.

## Regeln
- Stundensätze und Prozentwerte nie vorschlagen oder schätzen.
- Referenzlogos nur von echten Kunden (mit Einverständnis) oder echten Zertifikaten; Bewertungen nur
  mit aktueller, echter Zahl – sonst leer lassen.
- Daten aus dem Internet immer mit Quelle zeigen und bestätigen lassen.
