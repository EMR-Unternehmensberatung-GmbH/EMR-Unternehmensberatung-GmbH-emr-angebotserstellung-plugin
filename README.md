# EMR Angebotserstellung

Kalkulation und Angebotserstellung für Gebäudereinigungen nach EMR-Standard, für Kunden der EMR
Unternehmensberatung GmbH mit laufendem Programm. Das Plugin enthält den Skill emr-angebotserstellung-connector und
den EMR-Angebots-Connector. Der Skill führt durch das Gespräch, fragt die nötigen Angaben zum Objekt ab und
erstellt Kalkulationstabelle und Angebot als PDF im Design der eigenen Firma. Gerechnet wird auf dem Server von EMR.

## So geht es

1. Das Plugin in Claude unter Anpassungen › Plugins hinzufügen, aus dem Verzeichnis oder als Datei hochladen.
2. Im Plugin unter Konnektoren den Connector EMR Angebotserstellung verbinden. Es öffnet sich die Anmeldeseite von
   EMR. Dort die E-Mail-Adresse der EMR-Akademie eingeben und den Code aus der E-Mail eintragen.
3. In einem neuen Chat eine Anfrage beschreiben oder Besichtigungsnotizen hochladen. Claude rechnet über den
   Connector und erstellt Kalkulationstabelle und Angebot als PDF.

## Was das Plugin sendet und speichert

- Anmeldung: Die eingegebene E-Mail-Adresse geht an den Server von EMR. Der Server prüft im Kundensystem von EMR,
  ob es dazu ein Kundenkonto gibt, und schickt einen Code an diese Adresse.
- Kalkulation: Für jede Kalkulation schickt Claude die Angaben zum Objekt (Flächen, Turnus, Leistungen) und die
  Werte aus der firma.yaml an den Server von EMR. Der Server rechnet und schickt das Ergebnis zurück.
- Rückmeldungen: Kann der Skill etwas nicht oder korrigiert der Nutzer ein Ergebnis, schickt Claude eine kurze
  Meldung ohne Namen und Kontaktdaten von Auftraggebern an EMR. Claude sagt dem Nutzer das jeweils in einer Zeile.
- Das PDF und die Kalkulationstabelle entstehen in Claude. Sie werden nicht an EMR geschickt.

Der Server läuft bei Google Cloud in Frankfurt. Ein Konto bei EMR und einen laufenden Vertrag braucht, wer rechnen
will. Fragen an die EMR Unternehmensberatung GmbH: info@emr-unternehmensberatung.de
