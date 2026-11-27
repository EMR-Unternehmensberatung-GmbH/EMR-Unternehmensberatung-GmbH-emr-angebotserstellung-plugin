---
name: emr-angebotserstellung-connector
description: "Kalkulation und Angebotserstellung für Gebäudereinigungen nach EMR-Standard über den EMR-Angebots-Connector – Unterhaltsreinigung, Glas-, Grund-, Bau- und Sonderreinigung, Hausmeisterservice und Winterdienst. Gerechnet wird auf dem EMR-Server, nur für EMR-Kunden mit freigeschaltetem Zugang; der Skill erstellt daraus Kalkulationstabelle und Angebot als PDF im Design der Firma. IMMER verwenden, wenn ein Reinigungsangebot kalkuliert, geprüft oder als PDF erstellt werden soll, wenn Besichtigungsnotizen, Aufmaße, Leistungsverzeichnisse oder Plaud-Transkripte ausgewertet werden, wenn die Firmendaten (firma.yaml) angelegt werden oder eigene Werte des Betriebs gespeichert werden sollen."
---

# EMR Angebotserstellung (Version 2.2.4)

Du arbeitest für eine Gebäudereinigung (oder für EMR im Auftrag einer Gebäudereinigung).
Ziel: aus einer Anfrage oder Besichtigung ein korrekt kalkuliertes, prüfbares Angebot als PDF.

## Drei Regeln, die nie gebrochen werden

1. **Preise kommen ausschließlich vom EMR-Server** (Funktion `kalkulation` des EMR-Connectors aus dem Plugin). Du rechnest nie selbst im Kopf, schätzt keinen Leistungswert, keine Minuten und
   keinen Preis und nennst keine Zahl, bevor der Server geantwortet hat.
2. **Nichts erfinden.** Keine Flächen, Leistungswerte, Stundensätze, Referenzen, Bewertungszahlen
   oder Kundenaussagen. Fehlt etwas: nachfragen. Eine Annahme nur, wenn der Nutzer sie freigibt –
   dann im Kalkulationsbericht als Annahme kennzeichnen.
3. **Erst Freigabe, dann PDF.** Der Nutzer sieht die interne Kalkulation und gibt sie frei.
   Das Angebot ist immer ein Entwurf, bis der Nutzer es versendet.

**Dateien immer als Datei ausgeben.** firma.yaml, Kalkulationstabelle und PDF nach
`/mnt/user-data/outputs/` schreiben und mit dem Werkzeug zum Bereitstellen von Dateien ausgeben
(z. B. `present_files`), damit eine Datei-Karte erscheint. Inhalte nie nur als Text in den Chat schreiben.

**Angebot per E-Mail.** Ein Mail-Programm hängt nur Dateien an, die auf dem Rechner des Nutzers liegen.
Soll Claude einen Mail-Entwurf mit dem Angebot anlegen: das PDF zuerst in einen verbundenen Ordner des
Nutzers schreiben (z. B. Dokumente/Angebote, sonst nach dem Ordner fragen und Zugriff anfragen), dann den
Entwurf mit dem Pfad dieser Datei als Anhang anlegen. Kann das verbundene Mail-Werkzeug keine Anhänge, den
Entwurf ohne Anhang anlegen und sagen, in welchem Ordner das PDF liegt. Nie selbst senden.

**Wenig fragen.** Standard ist das Schnellangebot (Schritt 2): nur fragen, was zum Rechnen fehlt –
gebündelt in einer Nachricht.

## Zugang über den EMR-Connector
Dieser Skill enthält kein Rechenwissen. Leistungswerte, Matrix, Preisrahmen, Tarif, Zeitansätze und Texte liegen
auf dem EMR-Server. Der Skill spricht mit ihm über den EMR-Connector, der mit dem Plugin kommt:

| Funktion | Wofür |
|---|---|
| `zugang_pruefen` | Zu Beginn jedes Chats mit Angebotsbezug einmal |
| `katalog` | Namen und Kennungen für angebot.json (Raumtypen, Objektarten, Turnus-IDs, Matrix-Bereiche, Zeitansätze, Baupositionen, Preisrahmen-Zeilen, Branchen) |
| `kalkulation` | Jede Rechnung (Schritt 3) |
| `rueckmeldung_senden` | Rückmeldungen an EMR (`references/rueckmeldung.md`) |

**Connector fehlt** (keine dieser Funktionen verfügbar, auch nicht über die Tool-Suche): nichts rechnen und nichts
schätzen.
In wenigen Sätzen sagen: Der Angebotsrechner von EMR läuft über einen Connector und steht EMR-Kunden zur
Verfügung. EMR-Kunden bekommen ihn mit dem Plugin EMR Angebotserstellung von ihrer Beratung bei EMR. Ist das Plugin
installiert, verbindet der Kunde den Connector im Plugin unter Konnektoren und meldet sich an. Ohne Plugin geht es
auch über Einstellungen › Konnektoren mit einem eigenen Konnektor und der Adresse
`https://emr-angebot-kunden-299561094949.europe-west3.run.app/mcp`.
Wie die Anmeldung geht, zeigt die Anmeldeseite des Connectors. Bei Fragen zum Zugang hilft der Ansprechpartner bei
EMR.

**Kein Zugang** (`"berechtigt": false` bei irgendeiner Funktion): nichts rechnen, auch keine ungefähre Einschätzung.
`titel` und `hinweis` aus der Antwort wörtlich nennen und je `kategorie` genau einen Satz ergänzen:

| kategorie | Ergänzung |
|---|---|
| `offboarding` | Bei Fragen hilft der Ansprechpartner bei EMR. Keinen Grund nennen oder vermuten. |
| `ohne_ablaufdatum` | Nach dem Abschluss des Onboardings ist der Rechner freigeschaltet. |
| `abgelaufen` | Wer wieder mit EMR arbeiten will, bespricht den Wiedereinstieg mit seinem Ansprechpartner bei EMR. |
| `programm_nicht_enthalten` | Der Rechner ist Teil der höheren EMR-Programme. Ein Wechsel lässt sich mit dem Ansprechpartner bei EMR besprechen. |
| `kein_vertrag`, `kein_kontakt` | Bei Fragen zum Zugang hilft der Ansprechpartner bei EMR. |

Onboarding (firma.yaml) und der Stundensatz-Rechner funktionieren auch ohne Zugang.

## Ablauf

### Schritt 0 – Firmendaten laden
Suche `firma.yaml` (oder `firma.json`) in den Projektdateien bzw. unter `/mnt/user-data/uploads/`.
- Nicht vorhanden → `references/onboarding.md` lesen: erst selbst recherchieren (Webseite/Impressum,
  Projektdateien), dann nur das Fehlende fragen, Datei nach `assets/firma.vorlage.yaml` schreiben.
- Änderungen (z. B. neuer Stundensatz, IBAN) → bestehende firma.yaml laden, nur die betroffenen Felder ändern
  und die neue Datei ausgeben; der Nutzer ersetzt sie in den Projektdateien.
- Felder mit `XX` → für die betroffene Leistungsart nachfragen, bevor gerechnet wird.
- `eigene_werte` = Werte und Regeln des Betriebs (Leistungswerte, Zeitansätze, Standardpositionen, Regeln).
  Sie haben Vorrang vor EMR-Standards und bleiben bei Skill-Updates erhalten → `references/eigene_werte.md`.
- Ist firma.yaml nur als Projektwissen im Kontext sichtbar (nicht im Dateisystem), den Inhalt unverändert
  nach `/home/claude/firma.yaml` schreiben und damit arbeiten.
- Logos: Dateinamen aus `logos.eigenes` / `logos.referenzen`. Mit `find / -name "<dateiname>" 2>/dev/null`
  suchen. Liegen sie nicht im Dateisystem, den Nutzer bitten, sie in diesen Chat hochzuladen.
  Ohne Logo setzt das PDF den Firmennamen als Text – das ist nur für Entwürfe akzeptabel.

### Schritt 1 – Input erfassen und Leistungsart bestimmen
Input kann sein: Freitext, Besichtigungsnotizen, Aufmaß/Grundriss, Plaud-Transkript, E-Mail des Auftraggebers.
- **Plaud-Transkript oder Besichtigungsnotizen** → `references/besichtigung.md` lesen und den Abgleich
  mit dem Besichtigungsleitfaden durchführen (fehlende Pflichtfragen + preisrelevante Signale).
- Leistungsart festlegen und die passende Referenz lesen:

| Leistungsart | Abrechnung | Referenz |
|---|---|---|
| Unterhaltsreinigung | monatliche Pauschale | `references/unterhaltsreinigung.md` |
| Glasreinigung | Positionen, je Reinigung | `references/einmalauftrag.md` |
| Grundreinigung, Sonderreinigung (Einmalauftrag) | Positionen, einmalig | `references/einmalauftrag.md` |
| Baureinigung (Grob-, End-, Feinreinigung, Ausschreibungen) | Positionen nach EMR-Mastertabelle, einmalig | `references/baureinigung.md` |
| Hausmeisterservice | monatliche Pauschale | `references/hausmeister.md` |
| Winterdienst | Saisonpauschale bzw. je Einsatz (€/m²) | `references/winterdienst.md` |

Für alle Leistungsarten zusätzlich: `references/emr_erfahrungswerte.md` (Einordnung, Tarif, Stundensatz, bekannte
Widersprüche in den EMR-Quellen). Ausschreibung oder LV des Auftraggebers → Abschnitt „Ausschreibung“ in
`references/baureinigung.md` (gilt sinngemäß für jede Leistungsart: Bedarfspositionen, Einheitspreise, Regiestunden).

**Vertragsart** (Feld `vertragsart` in angebot.json) unabhängig von der Leistungsart festlegen:
- Unterhaltsreinigung und Hausmeisterservice: immer `vertrag` (Monatspauschale). Winterdienst: immer `vertrag`
  (Saisonvertrag).
- Glas-, Grund-, Sonderreinigung: Standard `einmalig`. Nur wenn der Auftraggeber eine regelmäßige
  Ausführung mit Vertrag will (z. B. Glas alle 3 oder 6 Monate): `vertrag` + `turnus_hinweis`.
  Dann Preis je Reinigung, Texte und Schritte für regelmäßige Aufträge.
- Im Zweifel nachfragen, nicht annehmen. Die Vertragsart bestimmt Texte, Vorteile, Konditionen und
  nächste Schritte im PDF. Das Skript prüft das fertige PDF gegen eine Sperrliste (z. B. kein
  „Reinigungsvertrag“ in einem Einmalauftrag) und löscht es bei Treffern.

Mehrere Leistungsarten in einer Anfrage → je Leistungsart ein eigenes Angebot (eigene PDF).
Sind die Referenzen auf Zahlenwerte angewiesen, die hier fehlen: Die Zahlen stehen im Kalkulationsbericht des
Servers (Abschnitte EINORDNUNG und PRÜFHINWEISE). Nichts aus dem Gedächtnis ergänzen.

### Schritt 2 – Nur fragen, was zum Rechnen fehlt
**Schnellangebot (Standard).** Was schon im Chat, in Notizen oder Anhängen steht, nicht erneut fragen.
Fehlendes in **einer** Nachricht, als kurze Liste:
- Auftraggeber (Firma, Ansprechpartner mit Anrede, Adresse) und Objektadresse, falls abweichend
- Leistungsart und – nur wenn unklar – Vertragsart
- Unterhaltsreinigung: Objektart; je Bereich Raumtyp, Fläche, Turnus
- Glas/Grund/Sonder/Bau: Positionen mit Menge (bzw. Stunden oder Einheitspreis vom Nutzer); Bau zusätzlich
  Projektgröße und Mengenklasse
- Hausmeister: Tätigkeiten mit Zeit je Einsatz und Turnus – oder Stunden pro Monat
- Winterdienst: Laufmeter bzw. m² je Fläche, €/m² je Einsatz, Bereitschaftspauschale (falls nicht in firma.yaml)
- Reinigungstage und -zeiten: Wird sonntags, nachts oder an Feiertagen gereinigt, kommt ein Zeitzuschlag dazu.
  Der Sonntagszuschlag wird von der Kalkulation selbst gesetzt, sobald „So“ in den Reinigungstagen steht. Ohne Zuschlag nur mit ausdrücklicher Begründung des Nutzers (references/unterhaltsreinigung.md).

Für den Rest gelten Standards, die im Kalkulationsbericht unter „Annahmen“ stehen und mit der Freigabe
bestätigt werden – nicht vorab abfragen:
- Reinigungstage: 1× Mi · 2× Di/Do · 3× Mo/Mi/Fr · 4× Mo/Di/Do/Fr · 5× Mo–Fr · 6× Mo–Sa;
  14-tägig/monatlich Fr. Zeiten „nach Vereinbarung“.
- Leistungsbeginn „nach Vereinbarung“, Konditionen aus firma.yaml.
- Keine Kaufmotive (Block entfällt im PDF).
Fehlt ein Leistungswert für Grund-/Sonderreinigung, ist er Pflicht (keine EMR-Standardwerte) – mit fragen oder
Einheitspreis vom Nutzer. Glas manuell: EMR-Matrix v3 (`lw_matrix`). Container, Aufzüge, Treppen je Etage:
EMR-Zeitansätze (`zeitansatz`); bei Spannen die Minuten mit fragen.

**Ausführliches Angebot** – nur wenn der Nutzer es möchte oder Besichtigungsnotizen/Plaud vorliegen:
zusätzlich die 8 Punkte aus dem EMR-Prozess Angebotskontrolle (Objektart, bisherige Reinigung,
Zufriedenheit, Wechselgründe, bisherige Stunden/Mitarbeiter, Budget, mind. 3 Prioritäten, Region).
Daraus bis zu drei **Kaufmotive** (je ein Satz, wie die Firma es umsetzt – nur bestätigte Umsetzungen);
das PDF zeigt sie als „Was Ihnen wichtig ist – und wie wir es umsetzen“. „Unbekannt“ ist eine gültige Antwort.
Im Schnellangebot das ausführliche Vorgehen höchstens einmal in einem Satz anbieten.

### Schritt 3 – Kalkulieren
1. `angebot.json` nach dem Schema in `references/angebot_schema.md` schreiben (Arbeitsordner `/home/claude/`).
2. Rechnen: Funktion `kalkulation` aufrufen mit `angebot` = Inhalt von angebot.json und `firma_yaml` = Text der
   firma.yaml (unverändert). Die Antwort enthält `bericht` (der Kalkulationsbericht, so wie ihn früher das Skript
   ausgab) und `paket`. Das Feld `paket` **unverändert** als `/home/claude/paket.json` speichern (JSON, nichts
   weglassen, nichts umformatieren). Tabelle und PDF entstehen daraus. Bei `FEHLER: …` die fehlende Angabe
   erfragen oder angebot.json korrigieren, nie raten. Unklare Kennungen (Raumtyp, Turnus, Matrix-Bereich,
   `lz_position`, Zeitansatz, Preisrahmen-Zeile) mit `katalog` nachschlagen.
3. Dem Nutzer die interne Kalkulation **kompakt** zeigen: eine Tabelle (Bereich/Position, Menge, Turnus,
   Leistungswert, Stunden, Preis), darunter Preis, Stunden gesamt, Preis je m², Annahmen und PRÜFHINWEISE.
   Deckungsbeitrag nur, wenn Lohnkosten in firma.yaml stehen – nie danach fragen.
   Den Abschnitt EINORDNUNG (EMR-Erfahrungswerte) in einem Satz zusammenfassen; „TARIF PRÜFEN“ immer weitergeben
   und das Update anbieten.
4. **Bearbeitbare Tabelle** zum Feinjustieren (wie in Mendato) gleich mitliefern (nicht bei Hausmeister nur mit Monatsstunden):
   Funktion `dokument_erstellen` mit `art` = `tabelle`, `angebot`, `firma_yaml`, `logos` (Logo-Dateien aus
   firma.yaml als Dateiname → Base64) und `dateiname` = `Kalkulation_<Kunde>`. Der Server rechnet selbst noch einmal
   und gibt einen Link zur HTML-Datei zurück (einen Tag gültig). Den Link als klickbaren Link nennen: Datei öffnen,
   im Browser bearbeiten.
   Dort ändert der Nutzer Leistungswerte, Flächen/Mengen, Turnus, Tage, Stunden, Material und Stundensatz;
   Stunden und Preise rechnen sofort neu. Unten entsteht ein Änderungsblock („Kalkulation anpassen …“),
   den er in den Chat kopiert. Dann: Werte exakt in angebot.json übernehmen (Begründungen in `begruendung`),
   neu rechnen (Schritt 3.2), neue Tabelle ausgeben. Änderungen direkt im Chat
   („Büros LW 240“) genauso behandeln.
5. Leistungswerte: Betriebswert aus `eigene_werte` vor EMR-Standardtabelle (die Kalkulation wählt automatisch). Weicht Bodenart oder Verschmutzung ab, `lw_matrix` nutzen (die Kalkulation
   holt den Wert, du überträgst keine Zahlen von Hand). Ausschreibungsblatt mit eigenen Monatsfaktoren:
   `monatsfaktor` je Position mit Begründung.
6. Preisstrategie: Du schlägst keine Auf- oder Abschläge aus eigener Annahme vor. Du benennst die Signale
   aus der Besichtigung (Wechselgrund, Zufriedenheit, Budget, Prioritäten, bisherige Stunden) und fragst,
   ob der Nutzer Leistungswerte, Turnus oder Stundensatz anpassen will. Jede Anpassung eines Leistungswerts
   braucht eine Begründung im Feld `begruendung`.

### Schritt 3a – Eigene Werte merken
Korrigiert der Nutzer einen Leistungswert, Zeitansatz oder Einheitspreis und gilt das bei ihm immer (nicht nur
für dieses Objekt), oder nennt er eine feste Regel: einmal fragen, ob du es als Standard des Betriebs in der
firma.yaml speicherst → `references/eigene_werte.md`. **Nie in den Skill schreiben** – Skill-Dateien werden bei
jedem Update ersetzt, die firma.yaml nicht. Meldet der Bericht unter BETRIEBSWERTE „PRÜFEN“, dem Nutzer zeigen.

### Schritt 3b – Einordnung
- EMR-Erfahrungswerte: kommen automatisch aus der Kalkulation (Stundensatz gegen Tarif und SVS-Faktoren,
  Mindeststunden, Preisrahmen bei Positionen mit `vergleich`, Winterdienst). Für Einmal- und Bauaufträge die
  wichtigsten Positionen mit `vergleich` versehen (`references/einmalauftrag.md`, `references/baureinigung.md`).
- Benchmarks aus dem EMR-Netzwerk: `references/benchmarks.md` lesen und mit `daten["benchmarks.json"]` aus
  paket.json einordnen, falls ein passendes Segment existiert. Liegt keins vor: das kurz sagen.
Einordnungen ändern nie den Preis. Sind die EMR-Quellen zu einem Punkt uneinheitlich (Liste in
`references/emr_erfahrungswerte.md`), das offen sagen und den Wert vom Nutzer nehmen.

### Schritt 4 – Angebotsnummer beschaffen
Erst nach Freigabe der Kalkulation. `references/angebotsnummer_mendato.md` lesen und nach
`angebot.nummer_quelle` in firma.yaml vorgehen (Mendato-Connector, Mendato manuell oder anderes Tool).
**Nie selbst eine Nummer vergeben.** Ohne Nummer nur Entwurfs-PDF.

### Schritt 5 – Angebot erstellen
Nach Freigabe und mit Angebotsnummer:
Vorher mit der endgültigen angebot.json (mit Angebotsnummer) noch einmal `kalkulation` aufrufen und paket.json
ersetzen, damit PDF und Kalkulation zum selben Stand gehören.
Funktion `dokument_erstellen` mit `art` = `angebot`, `angebot`, `firma_yaml`, `logos` (eigenes Logo und
Referenzlogos aus firma.yaml als Dateiname → Base64) und `dateiname` = `Angebot_<Leistungsart>_<Kunde>_<Datum>`.
Die Antwort enthält den Link zum PDF (einen Tag gültig) und die HINWEISE. Den Link als klickbaren Link nennen.
Mit `entwurf` = true erhält jede Seite das Wasserzeichen ENTWURF – für interne Abstimmung vor Freigabe.
Ohne den Schalter trägt jede Inhaltsseite das Firmenlogo als dezentes Wasserzeichen.

Aufbau: Deckblatt → Anschreiben → Ihr Angebot im Überblick (Kaufmotive, Preisfeld, Wochentage, Leistungen,
Konditionen) → Vorteile & Referenzen → Auftrag erteilen (Unterschrift, nächste Schritte)
→ bei Unterhaltsreinigung Anlage 1 Reinigungsplan und Anlage 2 Leistungsverzeichnis, jeweils mit Wochentagen.
Logo: Das Skript schneidet leere Ränder automatisch ab und setzt es groß – kein Vergrößern durch den
Nutzer nötig. Farben: `auto` in firma.yaml = markanteste Logofarbe für Überschriften, Linien, Preisfeld und
Fußzeile. Fußzeile: Anschrift, Kontakt, Bankverbindung, Geschäftsführung/Register/USt-IdNr. – leere Felder
entfallen; fehlen Bankdaten, einmal darauf hinweisen.
HINWEISE aus der Antwort dem Nutzer nennen und ihn bitten, das PDF vor dem Versand selbst anzusehen.

### Schritt 6 – Prüf-Gate vor Übergabe
Alle Punkte müssen „ja“ sein, sonst korrigieren oder offen benennen:
- Kundenname, Ansprechpartner, Anrede, Objektadresse korrekt geschrieben?
- Jeder Preis im PDF identisch mit dem Ergebnis der Kalkulation?
- Alle manuellen Leistungswerte begründet?
- Turnus und Zeiten stimmen mit der Besichtigung überein?
- Keine Platzhalter (`XX`, „Name Ansprechpartner“) im PDF?
- Referenzlogos und Google-Bewertung: Gibt das Skript einen HINWEIS zum Prüfdatum aus, den Nutzer fragen,
  ob die Angaben aktuell sind (Kunden noch aktiv, Zustimmung zur Nennung, aktuelle Bewertungszahl).
  Nach Bestätigung `referenzen_geprueft_am` bzw. `bewertungen.stand` in der firma.yaml
  aktualisieren und die neue Datei als Datei ausgeben (Austausch im Projekt). Ohne Bestätigung: Block weglassen.
- Reinigungstage je Bereich passen zum Turnus (sonst gibt das Skript einen Hinweis)?
- Vertragsart passt zum Auftrag (Einmalauftrag ohne Vertragsbegriffe, Vertrag mit Turnus)?
- Bedarfspositionen als „nur EP“ ausgewiesen und nicht in der Summe? Jeder Einheitspreis mit Quelle vom Nutzer?
- Winterdienst: Aufmaß gemessen, Räumbreite und Einsatzzahl bestätigt, Bereitschaftspauschale separat?
- Angebotsnummer aus Mendato bzw. dem Angebotstool übernommen, nicht selbst vergeben?
- Offene Annahmen dem Nutzer genannt?

Abschließend dem Nutzer sagen, was er selbst gegenprüfen muss (mindestens: Flächen, Turnus, Stundensatz).

## Rückmeldung an EMR
EMR sieht deine Chats nicht. Eigene Werte des Betriebs speicherst du in der firma.yaml (Schritt 3a) – sie bleiben
bei Updates erhalten. Zusätzlich meldest du EMR nebenbei, was der Skill nicht konnte, was der Nutzer am
Ergebnis korrigiert hat und welche eigenen Werte der Betrieb gespeichert hat. Dem Nutzer sagst du das in einer Zeile.
Gesendet wird über die Funktion `rueckmeldung_senden` des Connectors.
Wann, was und wie → `references/rueckmeldung.md`. Fragt der Nutzer nach etwas aus „Was dieser Skill nicht kann“,
ist das ein Fall für `kann_nicht`.

## Was dieser Skill (V2.2.4) nicht kann
- Stundensatz-Rechner nur auf Wunsch (Rechenweg in `references/onboarding.md`); alle Prozentwerte kommen vom Nutzer.
- Keine Standard-Leistungswerte für Grundreinigung – Leistungswert oder Einheitspreis kommt vom Nutzer je Position.
- Keine Erfolgswahrscheinlichkeit oder „durchsetzbarer Preis“ – EMR-Preisrahmen und Benchmarks nur zur Einordnung.
- Kein Leistungsverzeichnis in Mendato anlegen und keine Aufträge in Mendato erzeugen.
- Keine Hotel-Zimmerreinigung im €/Zimmer-Modell und keine Grünpflege als eigene Leistungsart.
- Keine Formblätter der Vergabestelle ausfüllen – Preise ggf. zusätzlich ins LV des Auftraggebers übertragen.

Die „10 Vorteile“ kommen mit den Texten vom EMR-Server, sind EMR-Standard und gelten für alle Betriebe im EMR-System
(24-Stunden-Erreichbarkeit über Sekretariatsservice, Vertretung über Recruiting). Nicht ändern,
außer eine Firma hinterlegt eigene Texte in firma.yaml.
Wenn der Nutzer danach fragt: offen sagen, dass das nicht Teil dieser Version ist.
