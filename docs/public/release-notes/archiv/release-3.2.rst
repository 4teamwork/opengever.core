OneGov GEVER Release 3.2
========================

Ein neuer **Schutzmechanismus gegen sogenannte Cross-Site-Request-Forgery** (`CSRF <http://de.wikipedia.org/wiki/Cross-Site-Request-Forgery>`_)
Angriffe schützt den Benutzer vor Angriffen auf seine GEVER-Session via Links in
E-Mails oder externen Webseiten.

Dieser Angriff zielt darauf ab, die Session eines an einer Web-Applikation
angemeldeten Benutzers zu missbrauchen. Beispielsweise versendet der Angreifer ein
irreführendes E-Mail an einen Benutzer, welches einen Link enthält, der bei einem
Klick eine Aktion in der Web-Applikation durchzuführen versucht. Ist nun kein
Schutzmechanismus gegen diesen Angriff vorhanden, wird diese Aktion im Kontext des
Benutzers durchgeführt wenn dieser an der Webanwendung angemeldet ist.

In GEVER ist darum neu ein Mechanismus enthalten, der jede einzelne Anfrage (Request)
mit einem kryptographischen Token versieht, und dieses vor dem Ausführen vor
Datenmanipulationen validiert. So ist sichergestellt, dass Aktionen welche Daten
verändern nur innerhalb von GEVER durchgeführt werden können, und immer auf eine
bewusste Handlung des Benutzers zurückzuführen sind.

Weitere Anpassungen
-------------------

- Administratoren haben neu standardmässig auch die Berechtigung, stornierte
  Dossiers wiederzueröffnen.

- Diverse Verbesserungen an Migrationen der SQL-Schemas bei Upgrades

- Verschiedene Korrekturen an Schema-Migrationen mit Oracle

- Unterstützung für PostgreSQL als SQL-Datenbank

Bugfixes
--------

- Bugfix: Darstellung des Erledigungsdatums in der Aufgaben-Übersicht wurde korrigiert

- Bugfix: Das Widget zum Auswählen von Dossier-Beteiligungen wurde auf ein Checkbox-Widget
  geändert. Dies behebt ein Problem bei der Auswahl von Beteiligungen mit IE10 und IE11.

- Bugfix: Folgeaufgaben behalten neu die korrekte OrgUnit der Hauptaufgabe

- Bugfix: Leeres Hinzufügen-Menü bei Aufgaben im Status "abgeschlossen" wurde entfernt

- Bugfix: Problem bei der Darstellung von Dokumenten mit Umlauten in Aufgaben behoben

- Bugfix: Die Aktion "Einfügen" wird nur noch dargestellt wenn die Objekt-Typen in
  der Zwischenablage am aktuellen Ort eingefügt werden dürfen.

- Bugfix: Verschieben-Formular: Bessere Behandlung von doppelt abgesendeten Formularen

- Bugfix: Ein Subdossier kann nicht mehr wiedereröffnet werden wenn
  das Hauptdossier storniert ist.

- Bugfix: Fallback-Mechanismus bei der Auswahl der aktuellen
  Organisationseinheit wurde korrigiert.

- Bugfix: Korrektur von ungültigen Suchabfragen bei bestimmten
  Kombinationen von Start- und End-Datum.

- Bugfix: Ein Fehler bei der Sortierung basierend auf User/Kontakt-Namen
  in Tabellen wurde behoben.

  .. disqus::
