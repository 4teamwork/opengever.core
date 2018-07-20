OneGov GEVER Release 2017.5
===========================

Zahlreiche visuelle Verbesserungen in OneGov GEVER und Ausbau der vorhandenen RESTful API.

Übersichtlichere Darstellung des Klickpfads
-------------------------------------------

|img-release-notes-2017.5-1|

Die Darstellung des Klickpfads wurde überarbeitet und optimiert. Einerseits hebt
sich die neue Darstellung optisch besser von den übrigen Inhaltsbereichen ab,
andererseits kann mit der Einbindung von Icons die verschiedenen Inhaltstypen
besser unterschieden werden. Um auch bei grossen, tief verschachtelten Ordnungssystemen
eine übersichtliche Darstellung zu gewährleisten, wird der Pfad innerhalb des Ordnungssystems gruppiert dargestellt.

Weblinks und Formatierungen
---------------------------

|img-release-notes-2017.5-2|

Die Darstellung von Beschreibung und Kommentar zu einer Aufgabe wurde aufgewertet.
OneGov GEVER erkennt neu automatisch Weblinks und stellt diese verlinkt dar. Zudem
werden auch Zeilenumbrüche beachtet, so dass Beschreibungen bzw. Antworten schöner formatiert werden.

Weblinks, die in Dossierkommentaren verwendet werden, werden neu auch automatisch verlinkt.

Neues Metadatum "Externe Referenz"
----------------------------------

Beim Inhaltstyp Dossier steht neu ein zusätzliches Feld *Externe Referenz* zur
Verfügung. Dies kann verwendet werden, um Fremdschlüssel und Verknüpfungen auf
Daten in Drittsystemen zu speichern. Dies ist besonders nützlich, wenn Dossiers
automatisch über die RESTful API von Drittsystemen erstellt werden. Über die API
kann dann sehr einfach nach einem bestehenden Dossier über die "Externe Referenz" gesucht werden.

Weitere Informationen finden Sie in unserer `API-Dokumentation <https://docs.onegovgever.ch/dev-manual/api/>`_ .

RESTful API
-----------

Die RESTful API bietet neu auch Endpoints für die Bearbeitung inkl. Versionierung
von Dokumenten inkl. Checkout/Checkin-Funktionalität. So können bestehende Dokumente
von Drittanwendungen direkt über die API bearbeitet werden.

|img-release-notes-2017.5-3|

Zudem stehen die folgenden kleineren Anpassungen zur Verfügung:

- Die Aktion 'Anhänge speichern' steht neu in der Detailansicht eines Mails zur Verfügung

- Der "Sprachwechsler" wurde ins persönliche Menü des angemeldeten Benutzers verschoben.

- Suchbegriffe werden bei der Darstellung der Suchresultate markiert.

- Korrekturen bei der Eingabemöglichkeit von Schlagworten.

- Der Import und Export von Dossiers gemäss eCH-Standards eCH-0147 und eCH-0039 kann nun aktiviert werden.

- Diverse kleinere Anpassungen und Korrekturen.

.. |img-release-notes-2017.5-1| image:: ../_static/img/img-release-notes-2017.5-1.png
.. |img-release-notes-2017.5-2| image:: ../_static/img/img-release-notes-2017.5-2.png
.. |img-release-notes-2017.5-3| image:: ../_static/img/img-release-notes-2017.5-3.png

.. disqus::
