# Angebotsnummer und Übergabe an Mendato

Grundsatz: **Der Skill vergibt nie selbst eine Angebotsnummer.** Ohne Nummer gibt es nur das Entwurfs-PDF
(`--entwurf`); das finale PDF bricht ohne `angebots_nr` ab. Das Mendato-PDF und der Mendato-Versand werden
nicht genutzt – an den Auftraggeber geht ausschließlich das PDF dieses Skills.

Die Variante steht in `firma.yaml` → `angebot.nummer_quelle`. Reihenfolge immer:
Kalkulation → Freigabe durch Nutzer → Nummer beschaffen → finales PDF.

## Variante mendato_manuell / anderes_tool
1. Nach Freigabe eine **Übertragungsliste** ausgeben (kurz, kopierbar):
   Auftraggeber/Interessent, Objektadresse, Leistungsart, je Position bzw. Bereich: Bezeichnung, Fläche,
   Turnus (Einsätze je Woche), Stunden (Monat bzw. je Einsatz), Stundensatz, Preis; Summe netto.
2. Nutzer legt das Angebot in Mendato bzw. seinem Tool an und nennt die Angebotsnummer.
3. Nummer exakt übernehmen (nicht umformatieren), in `angebot.json` setzen, finales PDF erzeugen.

## Variante mendato_mcp (Mendato-Connector verbunden) – live getestet 14.10.2026
Im EMR-Testkonto vollständig durchlaufen (UR mit 7 Räumen und Glas einmalig). Mendato rechnet mit derselben
Systematik (Einsätze/Woche × 4,35): 45,90 Std, 1.468,65 € – identisch mit unserem Skript vor Rundung.

Regeln:
- Vor dem ersten Schreiben `get_schema` (Domain costing/quote/prospect) aufrufen, falls ein Aufruf scheitert.
- Vor den schreibenden Aufrufen dem Nutzer in einem Satz sagen, was angelegt wird, und bestätigen lassen.
- Beträge in Cent (1.469 € = 146900), Prozent als Zahl. Datum JJJJ-MM-TT.
- Mendato-PDF und Versand nicht verwenden (`completeQuote`, `sendQuote` nie aufrufen).

Ablauf (Aufrufe in dieser Reihenfolge, Felder exakt so getestet):
1. Interessent suchen: `prospects(query: "<Firmenname>")`. Nicht vorhanden → anlegen:
   `createProspect(input: {type: COMPANY, companyName, streetAddress, zip, city, country: "DE",
   contactPersons: [{isDefault: true, salutation, firstName, lastName}], createObject: true,
   source: "Claude-Angebotserstellung"})` → `prospect { id objects { id } }`.
   Ist der Auftraggeber schon Kunde: `customers(query: …)` und `customerId` + `objectId` statt prospect.
2. Leistung suchen: `services(query: "Unterhaltsreinigung")` → `id` (ebenso Glasreinigung, Grundreinigung …).
3. `createCosting(input: {name: "<Leistungsart> – <Kunde>", note: "Preisquelle: Claude-Kalkulation …",
   prospectId, prospectObjectId, plannedStartDate})` → `costing { id }`.
4. `createCostingService(input: {costingId, serviceId, title, billingModel, hoursSource,
   manualSellingRate: <Stundensatz in Cent>, …})`:
   - Unterhaltsreinigung: `MONTHLY`, `ROOMS`; danach `createCostingRooms(input: {costingServiceId, rooms: [
     {name, sizeInSquareMeters, performanceValue: <unser Leistungswert>, weeklyFrequency: <Einsätze/Woche>}]})`
     (14-tägig 0,5 · monatlich 0,23 · 2× monatlich 0,46). Raumliste immer als Variable übergeben.
   - Hausmeister: `MONTHLY`, `DIRECT`, `hours: <Monatsstunden>`.
   - Einmalauftrag: `ONE_TIME`, `DIRECT`, `hours: <Stunden gesamt>` (je Position ein Block oder Summe).
   - Glas mit Vertrag: `PER_OPERATION`, `DIRECT`, `hours` je Einsatz, `executionsPerYear`.
5. Ergebnis lesen: `costing(id) { result { incompleteRows { roomName reasons } services { hours price }
   totals { monthly { hours price } oneTime { hours price } } } }`. Stunden mit unserem Skript vergleichen
   (Toleranz 0,01 Std). Weicht etwas ab → dem Nutzer nennen, nicht still übergehen.
6. Unseren gerundeten Preis festschreiben: `updateCostingService(input: {costingServiceId,
   manualSellingPrice: <unser Preis in Cent>})`.
7. `generateQuoteFromCosting(input: {costingId, taxRate: 19})` → `quote { id number numberPrefix status }`.
   Angebotsnummer für das PDF = `numberPrefix` + `number` (Test: „AG“ + 14). Schreibweise einmal mit dem
   Nutzer abgleichen, wie sie in Mendato angezeigt wird, und dann gleich verwenden.
8. Kosten-, Angebots- und Interessenten-ID im Chat nennen, damit eine Überarbeitung dieselben Datensätze trifft.

Überarbeitung: bestehende Kalkulation ändern (`updateCostingService`, `updateCostingRoom`) und
`generateQuoteFromCosting` erneut aufrufen. Getestet: gleiche Angebots-ID, gleiche Nummer. **Nie eine zweite
Kalkulation für dasselbe Angebot anlegen.**

Grenzen: Kalkulationen sind an das Mendato-Paket gebunden (Monatslimit). Fehlermeldung wörtlich nennen und
auf mendato_manuell ausweichen. Auftrag (`createOrderFromCosting`) erst nach Umwandlung in einen Kunden –
macht der Betrieb in Mendato, nicht dieser Skill. Kein Leistungsverzeichnis in Mendato in dieser Version.

## Nach der manuellen Variante nachpflegen (optional)
Wer Mendato ohne Connector nutzt und später planen will, legt in Mendato zur Angebotsnummer eine Kalkulation
mit den Werten der Übertragungsliste an: je Bereich Fläche, Leistungswert, Einsätze je Woche, Stundensatz;
Preis als manuellen Verkaufspreis eintragen.
