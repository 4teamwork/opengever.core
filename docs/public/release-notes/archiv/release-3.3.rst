OneGov GEVER Release 3.3
========================

Benachrichtigung direkt in der Applikation
------------------------------------------

|img-release-notes-3.3-1|

Benachrichtigung per E-Mail
---------------------------

|img-release-notes-3.3-2|

Sicherheit und Berechtigungen / Workflows
-----------------------------------------

- Bugfix: Kleinere Korrekturen an der Implementierung des CSRF-Schutzmechanismus
  (engl. Cross-Site Request Forgery).

- Bugfix: Korrektur am Workflow, welche sicherstellt, dass der Ersteller von
  Objekten keine besonderen Berechtigungen erhält.

- Dossiers, welche noch nicht abgeschlossene Aufgaben enthalten, können
  neu nicht mehr abgeschlossen werden.

User-Interface
--------------

- Der Mandanten-Wechsler wird nur noch in Installationen mit mehreren Ämtern dargestellt

- Der Sprachauswahl wird neu als Dropdown-Menu dargestellt anstatt einer Liste von Links

- In der Dossier-Übersicht wird nun die Dossier-Struktur (Verschachtelung von Subdossiers) dargestellt

- Bugfix: Ein Darstellungsfehler der Aktionen in der Übersicht einer Aufgabe wurde korrigiert

- Bugfix: Darstellung der Icons für Benutzer in der Auflistung von Gruppen wurde korrigiert

- Optimierung der Darstellung des Hilfetexts im Navigationsbaum

- Der Status-Filter ist nun auch auf Subdossiers verfügbar

- Deutsche und französische Übersetzungen wurden aktualisiert

- Bugfix: Korrektur eines Darstellungsfehlers bei den Icons für Favoriten im Navigationsbaum

Dokumente
---------

- Bugfix: Korrekturen beim Kopieren & Einfügen:

  - Es wird neu auch in der ID / URL des Dokuments die korrekte (neue) Laufnummer verwendet

  - Beim Kopieren von E-Mails wird nun auch dem Titel des Mails der Text "Kopie
    von" vorangestellt (gleich wie bei Dokumenten)

- Nach dem Verschieben eines Dokuments in den Papierkorb wird neu auf den
  Reiter "Dokumente" weitergeleitet anstelle des Reiters "Papierkorb"

Aufgaben
--------

- Bugfix: Abgeschlossene Aufgaben werden nicht mehr als "überfällig" markiert

- Hinzufügen eines Mails zu einer Aufgabe erzeugt nun einen Eintrag im Verlauf der Aufgabe

- Die Aktion "Kopieren" wurde für Aufgaben-Auflistungen deaktiviert, da sie dort
  nicht sinnvoll genutzt werden kann

- Bugfix: Korrektur in der Synchronisierung von mandantenübergreifenden Aufgaben-Paaren
  beim Verschieben einer Aufgabe

.. |img-release-notes-3.3-1| image:: ../../_static/img/img-release-notes-3.3-1.png
.. |img-release-notes-3.3-2| image:: ../../_static/img/img-release-notes-3.3-2.png

.. disqus::
