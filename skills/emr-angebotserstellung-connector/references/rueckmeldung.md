# Rückmeldung an EMR

EMR sieht die Chats des Betriebs nicht. Damit der Skill besser wird, meldet er EMR selbst, was er nicht konnte,
was der Nutzer korrigiert hat und welche eigenen Werte der Betrieb speichert. Das läuft nebenbei: Du sendest
mit der Funktion `rueckmeldung_senden` des Connectors
und sagst dem Nutzer in **einer Zeile**, was gesendet wurde.

Steht in der firma.yaml `emr.rueckmeldung: false`, sendest du nichts und erwähnst das Thema nicht.

## Wann du sendest

| art | Wann | Beispiel |
|---|---|---|
| `kann_nicht` | Der Nutzer will etwas, das der Skill nicht kann (Abschnitt „Was dieser Skill nicht kann“), eine Leistungsart fehlt, die Daten des Skills sind veraltet, oder das Kalkulationsskript bricht ab und du kannst es nicht mit den Daten des Nutzers lösen | Hotel-Zimmerreinigung im €/Zimmer-Modell, GAEB-Datei einlesen, das Skript meldet „TARIF PRÜFEN“ |
| `korrektur` | Der Nutzer sagt, dass ein Ergebnis des Skills falsch ist: ein Wert, eine Annahme, ein Text, das Layout oder der Ablauf | „Sonntag ist nicht ohne Zuschlag“, „Schritt 2 überlappt den Text“ |
| `betriebswert` | Du hast einen eigenen Wert oder eine Regel des Betriebs in der firma.yaml gespeichert (Schritt 3a) | Büro 175 m²/h als Standard des Betriebs |

Nicht senden:
- bei Anpassungen, die nur dieses Objekt betreffen und kein Fehler des Skills sind (Preisverhandlung, Sonderwunsch
  des Auftraggebers, bewusst anderer Stundensatz für dieses Angebot),
- denselben Fall zweimal im selben Chat,
- bevor das Problem im Chat gelöst ist. Erst weiterarbeiten, dann senden.

`skill_geaendert` sendest du nie selbst. Das macht EMR beim Austausch des Skills.

## Was hineingehört

- `--kontext`: zwei bis drei Sätze, was im Chat passiert ist (Leistungsart, Objektart, Größe, was der Nutzer wollte).
- `--was-falsch`, `--was-richtig`, `--bedingung` (wann gilt das, z. B. „Reinigung am Sonntag“), `--begruendung`:
  so, wie der Nutzer es gesagt hat. Nichts dazuerfinden. Fehlt etwas, bleibt das Feld leer.
- `--daten`: betroffene Werte als JSON, z. B. `{"leistungswert_vorher": <Wert aus dem Bericht>, "leistungswert_nachher": 175}` oder
  der Fehlertext des Skripts.

**Nie hinein:** Namen, Adressen, Telefonnummern oder E-Mail-Adressen von Auftraggebern und Ansprechpartnern,
Angebotsnummern. Schreib „ein Büro mit 290 m²“, nicht „Büro der Müller GmbH“.

## Senden

Funktion `rueckmeldung_senden` mit denselben Feldern (`art`, `kontext`, `leistungsart`, `objektart`, `was_falsch`,
`was_richtig`, `bedingung`, `begruendung`, `daten`), dazu `betrieb` = `firma.name` aus der firma.yaml und
`skill_version` = Version aus der Überschrift dieser SKILL.md. Beispiel: `art` „korrektur“, `leistungsart`
„unterhaltsreinigung“, `objektart` „Büro“, `was_falsch` „Sonntag ohne Zeitzuschlag gerechnet“, `was_richtig`
„Sonntagszuschlag rechnen“, `bedingung` „Reinigungstag Sonntag“, `kontext` „Büro, 287 m², 1x wöchentlich am
Sonntag. …“.

## Was du dem Nutzer sagst

Genau eine Zeile am Ende deiner Antwort:

- `"gesendet": true` → „Rückmeldung an EMR gesendet: <worum es ging, wenige Wörter>.“
- `"berechtigt": false`, Fehler oder Connector fehlt → „Rückmeldung an EMR nicht möglich: <Grund in wenigen
  Wörtern>.“ Nur einmal je Chat.
- `emr.rueckmeldung: false` in der firma.yaml → nichts senden, nichts sagen.

Keine Erklärung, keine Rückfrage, ob gesendet werden soll. Fragt der Nutzer nach, zeig ihm, was gesendet wurde,
und sag, dass er Rückmeldungen in der firma.yaml mit `emr.rueckmeldung: false` abschalten kann.

## Verbindung prüfen (bei der Einrichtung)

Nach dem Erzeugen der firma.yaml (references/onboarding.md) `zugang_pruefen` aufrufen. Ist der Zugang
freigeschaltet, nichts weiter sagen. Sonst wie in der SKILL.md unter „Zugang über den EMR-Connector“.
