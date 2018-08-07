OneGov GEVER Release 2017.3
===========================

Mit dem Release 2017.3 konnten weitere Erneuerungen in verschiedenen Bereichen von
OneGov GEVER vorgenommen werden. Vor allem hervorzuheben ist die neue Funktionalität
der Sammelaufgaben, welche im Rahmen des `OGIP <https://docs.onegovgever.ch/user-manual/glossary/#term-ogip>`_ 15 umgesetzt wurde. Ebenfalls wurde
im User Interface das Autocomplete Widget modernisiert und mit grösstmöglicher
Benutzerfreundlichkeit ausgestattet.

Technische Optimierungen
------------------------

Übergreifend wurden folgende Anpassungen vorgenommen:

- **Deutlich verbesserte Gesamtperformance** durch die Verwendung einer optimierten Templating Engine (Chameleon)

- Update auf die neuste Version von Plone (4.3.x)

- Aktualisierung diverser Software-Komponenten von Drittanbietern

Vorlagenverwaltung
------------------

Im Bereich Vorlagen konnten folgende Verbesserungen vorgenommen werden:

- Verschieben von Dokumenten ist neu auch im Vorlagenbereich möglich

- Leere Vorlagen werden bei der Auswahl von Vorlagen nicht mehr angezeigt

Sitzungs- und Protokollverwaltung
---------------------------------

Bei der Sitzungs- und Protokollverwaltung konnte Nachstehendes verbessert werden:

- Korrektur bei der Erstellung von Jahresinhaltsverzeichnissen

- Vereinheitlichte Darstellung von Personennamen

- Alphabetische Sortierung der Sitzungsteilnehmenden im Protokoll

Dokumente und E-Mails
---------------------

Im Bereich der Dokumente kommen folgende Erweiterungen dazu:

- In der Dokumentauflistung steht neu eine Spalte „Aktenzeichen“ zur Verfügung.
  Wie bei Spalten gewohnt, können neu Dokumente auch nach diesem Kriterium sortiert werden.

- Bei der Erstellung einer Dokument-Kopie werden die bestehenden Journal-Einträge nicht mehr mitkopiert.

- E-Mails, die per Drag'n'Drop nach OneGov GEVER übernommen werden, werden neu
  auch **als MSG-Datei (Outlook-Format) abgelegt**. Die EML-Konvertierung bleibt
  weiterhin bestehen (wegen Archivierung).

- Alle Anhänge einer E-Mail werden auch im Übersichtsreiter dargestellt.

Aufgaben
--------

Mit der Einführung von Sammelaufgaben gibt es eine weitere grosse Erneuerung.

Mittels Sammelaufgaben wird dem Benutzer die Möglichkeit gegeben, eine Aufgabe
an mehrere Empfänger zu richten. Für jeden Auftragnehmer erstellt dann OneGov GEVER
automatisch eine einzelne, losgelöste Aufgabe. Sammelaufgaben dienen einzig dem
Zweck, in wenigen Schritten (Klicks) mehrere gleiche Aufgaben an mehrere Personen
zu erzeugen (z.B. "Zur Kenntnisnahme" an 10 Personen). Details dazu finden Sie auf `docs.onegovgever.ch <https://docs.onegovgever.ch/>`_ .

|img-release-notes-2017.3-1|

Auch können jetzt Aufgabenvorlagen im Status „aktiv“ überarbeitet werden.

Dossier
-------

- Die Darstellung der Subdossierstruktur im Übersichtsreiter eines Dossiers wurde
  verbessert und stellt nur noch die aktuell ausgewählte Position ausgeklappt dar.

- Schlagwörter sind neu verlinkt mit der entsprechenden Schlagwort-Suchabfrage.
  Diese zeigt alle Inhalte an, denen das ausgewählte Schlagwort zugewiesen ist.

- Die Geschäftsregel zum Dossierabschluss kann neu pro Mandant konfiguriert werden:
  Dabei kann eingestellt werden, ob alle Dokumente bei Dossierabschluss
  in Subdossiers abgelegt werden müssen oder nicht.

User Interface
--------------

Auch die Bedienung von OneGov GEVER (User Interface) gewinnt bei diesem Release
weiter an Benutzerfreundlichkeit:

- Verbesserung des Autocomplete Widgets: Einfachere Eingabe, Darstellung aller
  Resultate, schnellere Suche nach betreffenden Personen.

- Das Widget für Datumsfelder (Zeitpunkt) wurde ebenfalls durch ein moderneres Eingabeelement ersetzt.

PDF Vorschau
------------

Bei der Vorschau-Ansicht der PDFs können folgende Neuerungen verzeichnet werden:

- Bessere Gesamtplatzierung

- Ein-/Ausblendung der Detailspalte rechts möglich

- Overlay Darstellung wurde abgelöst

|img-release-notes-2017.3-2|

Diverse Optimierungen
---------------------

- LDAP-Anbindung: Bei der Anbindung an Active Directories wurden die Einstellungsmöglichkeiten erweitert.

- Performance-Verbesserungen beim Kopieren bzw. Verschieben von Inhalten

- Im Rahmen eines ausführlichen Security Audits durch eine beauftragte externe
  Firma wurden potentielle Sicherheitslücken präventiv ermittelt und geschlossen.

Korrekturen
-----------

- Korrektur bei erneuter Bearbeitung eines Dokuments

- Korrektur Caching-Issue bei der Darstellung des Mandantenwechslers

- Diverse weitere kleine Korrekturen und Anpassungen

  .. |img-release-notes-2017.3-1| image:: ../_static/img/img-release-notes-2017.3-1.png
  .. |img-release-notes-2017.3-2| image:: ../_static/img/img-release-notes-2017.3-2.png

.. disqus::
