# Glasreinigung, Grundreinigung, Einmal-/Sonderaufträge

## Formel (EMR-Standard, „Kalkulationstool Einmalauftrag“)
- Stunden = Menge ÷ Leistungswert (m²/h) – oder Stunden direkt, wenn nach Aufwand kalkuliert
- Positionspreis = Stunden × Stundensatz + Material
- oder Einheitspreis-Position: Menge × Einheitspreis (+ Material) – `einheitspreis`, `einheit`, `ep_quelle`
- Bedarfspositionen (`"bedarfsposition": true`): berechnet, im PDF „nur EP“, nicht in der Summe
- Rundung: je Position kaufmännisch auf volle Euro; Gesamt = Summe der gerundeten Positionen
  plus Material- und Fahrtkostenpauschale.

## Leistungswerte
- **Glas manuell**: EMR-Matrix v3 `lw_matrix: {"bereich": "Glasreinigung manuell (1 Person)", "verschmutzung":
  "mittel"}`. Osmose-Stiel und Spiegel/Glas innen ebenfalls in der Matrix. Ältere EMR-Faustregeln liegen für feste
  Elemente deutlich höher – Widerspruch. Im Zweifel Wert vom Nutzer.
- **Grundreinigung**: keine EMR-Standard-Leistungswerte. Leistungswert je Position beim Nutzer erfragen oder mit
  Einheitspreis (€/m²) vom Nutzer rechnen. Einflussfaktoren in der Positionsbezeichnung festhalten:
  Bodenbelag, Verschmutzung, Beschichtung ja/nein, maschinell/manuell, Möblierung.
- Glas: ein- oder beidseitig, mit/ohne Rahmen, Verschmutzungsgrad, Höhe und Hilfsmittel (Leiter, Teleskop,
  Osmose, Arbeitsbühne), Sprossen, Jalousien/Rollläden. Aufmaß einseitig messen, beidseitig reinigen.

## EMR-Regeln Grundreinigung (Skript prüft die ersten beiden)
- Immer zwei Positionen: (1) Grundreinigung/Beschichtung, (2) Aus- und Einräumen des Mobiliars (Pauschale oder
  Stunden). Leerer Raum: `"ohne_moebel": true`.
- Beschichtungsmittel immer separat ausweisen (bodenspezifisch, kein Universalmittel).
- Beschichtung nur nach Grundreinigung; Trocknungszeit je Schicht einplanen; Linoleum mindestens 2-fach.
- Keine hochalkalischen Reiniger auf Linoleum/Gummi; Parkett mit wenig Wasser und Spezialreiniger.
- Starke Verkalkung im Sanitär: Grundreinigung vor Start der Unterhaltsreinigung anbieten.

## Einordnung in EMR-Preisrahmen (`katalog` → `preisrahmen`)
Position mit `vergleich` versehen, das Skript zeigt, ob der €/Einheit-Preis im, unter oder über dem EMR-Rahmen liegt:
- Grundreinigung: `{"tabelle": "grundreinigung_boden", "zeile": "Linoleum (klassisch)", "stufe": "mittel"}`
  (inkl. Flächenkorrektur) oder `{"spanne": "gr_elastisch"}`
- Beschichtung: `{"tabelle": "beschichtung", "zeile": "...", "stufe": "2_schichten"}`
- Glas: `{"tabelle": "glas", "zeile": "Fenster Standard 2-Seiten", "frequenz": "quartal"}`; kleine Flächen
  `{"tabelle": "glas_pauschal", "zeile": "Bürofenster zweiseitig"}` (kleine Glasflächen laut EMR immer Pauschale)
Die EMR-Quellen zur Grundreinigung je m² widersprechen sich teils – beide sind Orientierung, keine Preisvorgabe.

## Wiederkehrende Glasreinigung
Preis gilt je Reinigung. Turnus (z. B. 4× jährlich) im Feld `turnus_hinweis` ausweisen.

## Stundensatz
Je Leistungsart aus firma.yaml (`glasreinigung`, `grundreinigung`, `einmalauftrag`).
Abweichend je Position möglich (`stundensatz` in der Position), z. B. für Arbeitsbühnen-Einsätze –
nur auf Anweisung des Nutzers. Hubsteiger/Bühne als eigene Position (Miete vom Nutzer).

## Prüfung
Lohnkosten in firma.yaml → Deckungsbeitrag wird ausgewiesen.
