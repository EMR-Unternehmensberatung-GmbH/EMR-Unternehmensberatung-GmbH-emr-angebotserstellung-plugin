# Eigene Werte des Betriebs merken (firma.yaml › eigene_werte)

Ziel: Was der Betrieb an eigenen Werten und Regeln festlegt, bleibt erhalten – auch wenn EMR eine neue
Skill-Version liefert. **Deshalb steht es nie im Skill, sondern immer in der firma.yaml des Betriebs.**
Ein Skill-Update ersetzt nur den Skill. firma.yaml, Logo und Projektanweisungen bleiben unverändert.

## Was hineingehört
| Bereich | Wofür | Beispiel |
|---|---|---|
| `leistungswerte` | Unterhaltsreinigung, m²/h je Raumtyp (alle Objektarten oder je Objektart) | `Büro: 175` · `Sanitär: {Schule: 135, alle: 145}` |
| `zeitansaetze` | Minuten je Einheit; ersetzt EMR-Spannen oder legt eigene Ansätze an | `treppenhaus_etage: 12` · `waschstrasse: {minuten: 45, einheit: Stk, label: Waschstraße}` |
| `positionen` | eigene Standardpositionen für Glas/Grund/Sonder/Bau – Einheitspreis **oder** Leistungswert | `glas_zweiseitig: {bezeichnung: Glasreinigung beidseitig, einheit: m², einheitspreis: 3.20}` |
| `regeln` | feste Regeln in Klartext, die das Skript nicht rechnet | „Treppenhäuser mindestens 1,25 Std. je Einsatz“ |

Nicht hinein: Stundensätze (stehen in `kalkulation.stundensaetze`), Daten eines einzelnen Auftraggebers
(gehören in angebot.json), geschätzte oder nicht bestätigte Werte.

## Vorrang beim Rechnen
1. Wert, der im Angebot manuell gesetzt ist (`leistungswert`, `minuten`, `einheitspreis`)
2. ausdrücklich gewählte EMR-Matrix (`lw_matrix`)
3. **Betriebswert** aus `eigene_werte`
4. EMR-Standard

Der Bericht kennzeichnet Betriebswerte mit `b` und listet sie im Abschnitt BETRIEBSWERTE. Regeln stehen dort
ebenfalls – du beachtest sie und weist auf Konflikte hin; sie ändern den Preis nie automatisch.
Positionen ruft das Angebot mit `"betriebswert": "<schlüssel>"` plus `menge` auf (siehe angebot_schema.md).

## Wann du fragst, ob ein Wert gemerkt werden soll
- Der Nutzer korrigiert einen Leistungswert, Zeitansatz oder Einheitspreis **und** sagt oder zeigt, dass es bei
  ihnen immer so ist („bei uns rechnen wir Büros immer mit 175“).
- Der Nutzer nennt eine feste Regel seines Betriebs.
- Einmalige, objektbezogene Abweichungen (starke Verschmutzung, Sonderwunsch) **nicht** merken – die gehören mit
  Begründung nur ins Angebot.
Frage einmal, kurz: „Soll ich das als Standard eures Betriebs in der firma.yaml speichern? Dann gilt es für alle
künftigen Angebote und bleibt bei Updates erhalten.“ Ohne Ja nichts speichern.

## Speichern
1. Nur die Änderung als JSON nach `/home/claude/firma_daten.json`, z. B.
   `{"eigene_werte": {"leistungswerte": {"Büro": 175}, "regeln": ["…"], "stand": "TT.MM.JJJJ"}}`.
   Regel löschen: `{"eigene_werte": {"regeln_entfernen": ["<genauer Text>"]}}`. Wert außer Kraft setzen: `null`.
2. ```bash
   python3 <skill-pfad>/scripts/firma_erstellen.py --daten /home/claude/firma_daten.json \
     --alt <pfad>/firma.yaml --out /mnt/user-data/outputs/firma.yaml
   ```
   Regeln werden ergänzt, nie überschrieben. Meldet das Skript „WARNUNG: … weniger Betriebswerte“, die Datei
   nicht übergeben, sondern den Fehler suchen.
3. Datei als Datei ausgeben. Dem Nutzer sagen: alte firma.yaml in den Projektdateien durch die neue ersetzen.
   Claude kann Projektdateien nicht selbst ändern – erst nach dem Ersetzen gilt der Wert in neuen Chats.
4. Rückmeldung `betriebswert` an EMR senden (`references/rueckmeldung.md`): welcher Wert oder welche Regel, wofür
   sie gilt und die Begründung des Nutzers.

## Nie
- Skill-Dateien ändern oder eigene Werte in den Skill schreiben – sie gingen beim nächsten Update verloren.
- Werte eines anderen Betriebs übernehmen.
- Einen Betriebswert stillschweigend verwerfen. Meldet der Bericht unter BETRIEBSWERTE „PRÜFEN“ (z. B. Raumtyp
  gibt es in dieser Version nicht mehr), dem Nutzer zeigen und die Zuordnung klären.
