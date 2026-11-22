# Baureinigung

Quelle der Methode und aller Leistungswerte: EMR-Mastertabelle Baureinigung (Erfahrungswerte aus EMR-Live-Calls,
validiert an realen Projekten). Texte nach der EMR-Angebotsvorlage Baureinigung.
Leistungsart `baureinigung`, Abrechnung einmalig
(Festpreis je Position). Vertragsart Standard `einmalig`.

## Ablauf
1. **Unterlagen klären**: Bauvorhaben, Auftraggeber (Bauträger, GU, Architekt, Endkunde), Termin der Abnahme/Übergabe,
   Bauphasen (Grobreinigung zwischen Phasen, Bauendreinigung, Baufeinreinigung), Aufmaß bzw. Pläne, Zugang, Strom/Wasser,
   Gerüst/Hebebühne, Schutzfolien, Entsorgung. Liegt ein LV oder eine Ausschreibung vor → Abschnitt „Ausschreibung“.
2. **Projektgröße** festlegen: klein | mittel | gross | xl (der Server setzt je Klasse den Faktor F1). Die Schwellen
   sind im EMR-Material nicht festgelegt → Klasse vom Nutzer bestätigen lassen, nie selbst wählen.
3. **Positionen** aus `katalog` → `baureinigung` (`lz_position`) mit Menge in der dort genannten Einheit
   (m², Stk, lfdm, Lauf, Stufe) und **Mengenklasse** der Position (sehr_klein … sehr_gross, Eigenmenge dieser Position).
   Auch hier: Klasse vom Nutzer bestätigen lassen. Positionen nach Bauphase gruppieren (`gruppe`).
4. Rechnung (Skript): LZ = Wert[Mengenklasse] × F1; Stunden = Menge ÷ LZ; Preis = Stunden × Verrechnungssatz
   + Material, je Position auf volle Euro. Anfahrt/Material über `zusatz`.
5. Fehlt eine Position in der Tabelle: Leistungswert vom Nutzer (Experte) erfragen und als `leistungswert` mit
   `menge` + `einheit` übergeben; im Chat als „ohne EMR-Quelle“ kennzeichnen. Nie schätzen.
6. Manuell geänderte Leistungswerte meldet das Skript; Grund dokumentieren (im Feld `begruendung`).

## Verrechnungssatz
`kalkulation.stundensaetze.baureinigung` aus firma.yaml (Vollkosten inkl. Gemeinkosten und Gewinn). Die EMR-Referenz
für LV-Stundenbasis-Positionen ist nur Orientierung – **nie als Ersatz für den Satz des Betriebs verwenden.**
<!-- CONNECTOR-END --> Regie-/Stundenlohnsätze für Vorarbeiter und Facharbeiter nicht
aus dem Kalkulationssatz ableiten; immer beim Nutzer erfragen.

## Prüfhinweise aus der Mastertabelle
- Positionen mit Sensitivität HIGH (Glas, Böden manuell und maschinell, Bodenanstrich, HD-Reinigung) reagieren stark auf
  Projekt- und Mengengröße. Kleinmengen kosten je Einheit deutlich mehr. Mengenklasse deshalb sorgfältig bestätigen.
- Glas Bauend zweiseitig wird nach einseitigem Aufmaß kalkuliert.
- Glas mit Folien und starkem Schmutz: eigene Position, nicht über den normalen Glaswert.
- Außentürelemente Alu/Glas: eigene Position je Stück – nicht wie Innentüren rechnen.
- Wohnobjekte: „Baufeinreinigung Wohnung (nach Bauendreinigung)“ wird oft vergessen und ist ein spürbarer Teil des
  Auftrags.
- Filzpappe/Schutzabdeckung entfernen ist eine eigene Position vor der Bauendreinigung.
- Querprüfung (neu in 1.5): Position mit `vergleich` versehen – das Skript ordnet den €/Einheit-Preis in die
  EMR-Preisrahmen ein (`katalog` → `preisrahmen`: Tabelle `bauend` nach Auftragstyp und Fläche, optional `region`;
  Spannen `bauend_*`). Einordnung ändert nie den Preis. Glas immer als eigene Position, Sanitärobjekte je Stück.

## Umsatzsteuer (§ 13b UStG)
Standard: netto zzgl. gesetzlicher MwSt. Ob für einen Auftraggeber die Steuerschuldnerschaft des Leistungsempfängers
gilt, entscheidet nicht der Skill. Bei Bauunternehmen, Bauträgern oder Generalunternehmern als Auftraggeber einmal
nachfragen: „Soll das Angebot mit Umkehr der Steuerschuld nach § 13b UStG ausgestellt werden? Bitte im Zweifel mit dem
Steuerberater klären.“ Nur auf ausdrückliche Anweisung `"steuer": "13b"` setzen – dann zeigt das PDF den Hinweis
„Steuerschuldnerschaft des Leistungsempfängers“ und keine MwSt.

## Ausschreibung / LV des Auftraggebers
Vorgehen nach EMR-Ausschreibungskalkulation:
- Positionsfolge, Mengen und Einheiten exakt wie im LV übernehmen (`bezeichnung` = LV-Text, eigene `gruppe` je LV-Titel).
- **Bedarfs-/Eventualpositionen** („Bedarfspos.“, „nur Einheitspreis“): `"bedarfsposition": true` – wird berechnet,
  im PDF mit „nur EP“ gezeigt und nicht in die Angebotssumme genommen.
- **Einheitspreis-Positionen** (Stück, lfm, m³, t, kg, Regiestunden): `einheitspreis` + `menge` + `einheit` +
  `ep_quelle`. Den Einheitspreis nennt der Nutzer (oder er ergibt sich aus Leistungswert x Stundensatz – dann
  lieber `lz_position`/`leistungswert` nutzen). Nie selbst festlegen.
- **Stundenlohnarbeiten** (Vorarbeiter, Facharbeiter, Helfer): als Einheitspreis-Position mit Einheit „h“ und dem
  Regiesatz des Nutzers.
- Jede Position einer Mastertabellen-Position zuordnen oder als „ohne Quelle“ markieren.
- Offene Punkte vor dem Preis klären und dem Nutzer als Liste geben, Rang je Punkt:
  SPERRE (ohne Klärung kein Preis), WESENTLICH (Preis möglich, Risiko offen), FORMAL (Verfahren).
  Typisch: Pauschalposition mit „ca.“-Fläche (Mengenrisiko beim Auftragnehmer), fehlende Mengen, Widerspruch Gerüst vs.
  Höhenarbeiten, fehlende Höhenangaben, Stundenlohnsätze.
- Bieterfragen fristgerecht an die Vergabestelle – der Skill formuliert sie, versendet nichts.
- Das PDF dieses Skills ersetzt kein vorgeschriebenes Formblatt der Vergabestelle. Preise ggf. zusätzlich in das LV des
  Auftraggebers übertragen lassen.

## Mendato
Leistung „Baureinigung“ (`services(query: "Baureinigung")`), `ONE_TIME`, `DIRECT`, Stunden gesamt bzw. je Bauphase ein
Block. Ablauf wie in `angebotsnummer_mendato.md`.
