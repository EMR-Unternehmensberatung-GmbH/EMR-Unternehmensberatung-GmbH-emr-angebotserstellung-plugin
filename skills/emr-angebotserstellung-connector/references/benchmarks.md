# Benchmarks aus dem EMR-Netzwerk

Datei: `daten["benchmarks.json"]` in paket.json. Sie enthält ausschließlich **aggregierte** Werte (Spannen und Mediane) aus
abgeschlossenen Angeboten im EMR-Netzwerk – nie einzelne Angebote, Betriebe oder Auftraggeber.

Nutzung:
- Nach der Kalkulation den Preis je m² (bzw. Stundensatz) mit dem passenden Segment vergleichen
  (Leistungsart × Objektart × Region). Nur einordnen: „liegt im unteren/mittleren/oberen Bereich“.
- Benchmarks ändern nie den Preis. Sie sind ein Hinweis für die Preisstrategie des Nutzers.
- Gibt es für ein Segment keinen Eintrag oder ist `stand` leer: sagen, dass noch keine Vergleichsdaten
  vorliegen. Nie aus anderen Segmenten hochrechnen, nie Werte schätzen.
- Immer Stand und Anzahl der zugrundeliegenden Angebote nennen.
