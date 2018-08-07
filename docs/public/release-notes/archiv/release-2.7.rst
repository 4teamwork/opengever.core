OneGov GEVER Release 2.7
========================

|img-release-notes-2.7-1|

Der OneGov GEVER Release 2.7 beinhaltet zahlreiche Bugfixes und Optimierungen.
OneGov GEVER wird noch zuverlässiger:

- Im Reiter "Vorlagen" wurden unlogische Aktionen wie "Als E-Mail versenden" und "Auschecken" deaktiviert.

- Nicht mehr benötigter Reiter und Index der referenzierten Aufgaben wurden entfernt.

- Die Aktion "Einfügen" wurde für Template-Dossiers und Kontakt-Ordner deaktiviert.

- Im Tab "Meine Dokumente" wurden die **Checkboxen zur Auswahl** aktiviert (Bild oben).

- Optimierungen bei der Darstellung von Personennamen in der OGDS-Auflistung.

- LDAP Import: Verschiedene Anpassungen um den Import aus Microsoft AD robuster zu machen.

- Caching-Optimierungen des Volltexts bei versionierten Dokumenten.

- LDAP Import: Unterstützung von verschachtelten Gruppen aus Microsoft AD.

- LDAP Import: Diverse Anpassungen zur Verbesserung der Performance.

- Flexiblere Volltextindexierung: Je nach Bedürfnissen des Kunden kann der
  Volltext aus einer **PDF-Vorschau** von Dokumenten oder aus den **Originaldokumenten** extrahiert werden.

- Unterstützung für **Volltextindexierung** von Dokumenten mit **Tika**.

- Anpassung am LDAP Import: Benutzer, welche von einer importierten Gruppe
  referenziert werden, sich aber ausserhalb der importierten Users-Base befinden, werden übersprungen.

- Styling-Anpassungen am Logout-Button im Logout-Overlay, um eine **einheitlichere Darstellung** zu erreichen.

|img-release-notes-2.7-2|

- Implementierung einer eigenen Titelzeile für die persönliche Übersicht.

- Die Länge der SQL Spalte für Benutzer- und Gruppennamen im OGDS wurde auf 255 Zeichen verlängert.


- **Bugfix**: Der Link auf dem Icon im Tooltip von Dokumenten wurde korrigiert.

- **Bugfix**: Die Ladereihenfolge von Drittprodukten wurde so korrigiert, dass Anpassungen am User-Interface von versionierten Objekten in jedem Fall korrekt geladen werden.

- **Bugfix**: Die URL für das Logout Overlay wurde so angepasst, dass sie auch in einem speziellen Fall mit Virtual Hosting im IE korrekt funktioniert.

- **Bugfix**: Anpassung der Darstellung von zugewiesenen Aufgaben im Eingangskorb.

- **Bugfix**: Anpassung der Meldung nach dem Abschliessen eines Subdossiers.

- **Bugfix**: In der Übersicht des Eingangskorbs werden nur noch aktive Aufgaben und Weiterleitungen angezeigt.

- **Bugfix**: Es wird nur noch der lokale Teil eines Vorgänger/Folgeaufgabe-Paars angezeigt.

- **Bugfix**: Der Link auf die erweiterte Suche wurde korrigiert.

- **Bugfix**: Kontakte können nun auch mit Umlauten durchsucht werden.

.. |img-release-notes-2.7-1| image:: ../../_static/img/img-release-notes-2.7-1.png
.. |img-release-notes-2.7-2| image:: ../../_static/img/img-release-notes-2.7-2.png

.. disqus::
