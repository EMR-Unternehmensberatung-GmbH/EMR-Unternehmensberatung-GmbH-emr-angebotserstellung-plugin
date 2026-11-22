# EMR-Erfahrungswerte: Einordnung, Tarif, Stundensatz

Alle Werte stammen aus EMR-Live-Calls und EMR-Kalkulationsvorlagen (Stand 2026). Sie **ordnen ein** – der Preis
entsteht immer aus den Werten des Betriebs (firma.yaml) bzw. des Nutzers und dem Kalkulationsskript.

## Was das Skript automatisch ausgibt (Abschnitt EINORDNUNG im Bericht)
- Stundensatz gegen Tariflohn der passenden Lohngruppe × EMR-SVS-Faktoren (Tarifdaten auf dem EMR-Server) in den Stufen Ziel,
  Optimiert, Aggressiv und Minimum. Unter Minimum → Prüfhinweis (nur Markteintritt, zeitlich begrenzt). Zu niedrige
  Sätze → Hinweis Ausschlussrisiko bei öffentlichen Ausschreibungen.
- UR: Ø Stunden je Einsatztag gegen EMR-Mindeststunden; optional Stundensatz-Matrix nach `branche`.
- Positionen mit `vergleich` und Winterdienst: €/Einheit gegen EMR-Preisrahmen.
Dem Nutzer die Einordnung in einem Satz nennen. Liegt etwas außerhalb: Signal benennen und fragen, ob er Leistungswerte,
Turnus oder Stundensatz anpassen will – nie selbst einen Auf- oder Abschlag vorschlagen.

## Tarif
Tarifdaten auf dem EMR-Server enthält Lohngruppen, Gültigkeit und RTV-Zuschläge. Ist der Stand älter als 6 Monate, meldet das
Skript „TARIF PRÜFEN“. Dann: dem Nutzer sagen, dass geprüft werden muss, ob ein neuer Lohntarifvertrag gilt oder der
alte nachwirkt; Update anbieten (Stundensätze in firma.yaml prüfen) und EMR Rückmeldung geben. Tariflöhne nie aus dem
Gedächtnis nennen – nur aus der Datei oder einer geprüften Quelle mit Link.

## Stundensatz-Rechner
Rechenweg in `references/onboarding.md` (Grundlohn, Lohnnebenkosten, Gemeinkosten, Wagnis/Gewinn, Material) – alle
Prozentwerte vom Nutzer. Danach Satz bestätigen lassen; die nächste Kalkulation ordnet ihn automatisch ein.

## Bekannte Widersprüche in den EMR-Quellen (offen, Experte entscheidet)
- Büro-Leistungswert: Standardtabelle und Matrix v3 gegen ältere EMR-Unterlagen mit niedrigeren Werten. Die
  EMR-Mindeststunden passen eher zu den niedrigeren Werten. Der Server rechnet mit dem Standard und zeigt die Lücke.
- Treppenhaus MFH: Zeit je Einsatz.
- Grundreinigung und Beschichtung: Preis je m².
- Glas manuell: Leistungswert der Matrix gegen ältere Faustregeln.
- Nachtzuschlag: Tarif gegen einzelne Verträge.
- Tariflohn der untersten Lohngruppe: eine abweichende Zelle in einer EMR-Vorlage.
Bei diesen Punkten im Chat offen sagen, dass die EMR-Quellen uneinheitlich sind, und den Wert vom Nutzer nehmen.

## Was bewusst nicht im Skill steckt
- Hotel-Zimmerreinigung im €/Zimmer-Modell (Auslastung, Zimmerkategorien, Stewarding): keine eigene Leistungsart.
  Öffentliche Bereiche als Unterhaltsreinigung rechnen. Für die Zimmerreinigung offen sagen, dass der Skill sie
  noch nicht abbildet, und Rückmeldung an EMR geben – nicht improvisieren.
- Personal-, Verhandlungs- und Akquise-Regeln aus den Bibeln – kein Kalkulationswissen.
