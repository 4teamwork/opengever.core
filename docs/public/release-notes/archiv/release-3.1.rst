OneGov GEVER Release 3.1
========================

Neu können Dokumente von Benutzern mit der entsprechenden Berechtigung
unter bestimmten Bedingungen gelöscht werden.

|img-release-notes-3.1-1|

Dokumente können dann gelöscht werden, wenn:

- Der Benutzer die entsprechende Berechtigung besitzt

- Sich das Dokument bereits im Papierkorb befindet

- Das Dokument eingecheckt ist

- Für das entsprechende Dokument keine Verweise mehr existieren

|img-release-notes-3.1-2|

Bevor Objekte vom System gelöscht werden, muss der Benutzer auf einer
entsprechenden Seite den Löschvorgang nochmals **bestätigen**.

|img-release-notes-3.1-3|

Jegliches Löschen von Objekten wird **journalisiert**. Formulierungen im Journal
wurden vereinheitlicht, und Journaleinträge für das Löschen von Objekten sind klar
unterscheidbar von Einträgen zum Verschieben in den Papierkorb.

Weiter wurde im Rahmen dieses Releases das **Löschen von Ordnungspositionen** überarbeitet.

- Konsistentere Einbindung in das User-Interface

- Anzeige einer Bestätigungsseite vor dem Löschen (analog zu Dokumenten)

Weitere Anpassungen
-------------------

- Das Aktualisieren von DocProperties beim Ablegen von Weiterleitungen mit Dokumenten im Jahresordner wurde unterbunden, damit der ursprüngliche Kontext vor dem Ablegen erhalten bleibt.

- Diverse kleinere Korrekturen und Verbesserungen

.. |img-release-notes-3.1-1| image:: ../../_static/img/img-release-notes-3.1-1.png
.. |img-release-notes-3.1-2| image:: ../../_static/img/img-release-notes-3.1-2.png
.. |img-release-notes-3.1-3| image:: ../../_static/img/img-release-notes-3.1-3.png

.. disqus::
