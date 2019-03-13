OneGov GEVER Release 3.10
=========================

Der Release 3.10 beinhaltet als grösste Erneuerung die persönliche Ablage (sog. persönliches Dossier).
Damit wird jedem Benutzer die Möglichkeit geboten, persönliche Dokumente in einem
eigenen Bereich in OneGov GEVER abzulegen und GEVER-like zu verarbeiten. Zum Beispiel
können so Dokumente bereits in GEVER vorregistriert werden, ohne dass bereits ein
entsprechendes Dossier im Registraturplan gebildet werden muss. Diese Dokumente
können dann zu einem späteren Zeitpunkt in ein Dossier verschoben oder wieder
gelöscht werden. Dabei gilt, dass die persönliche Ablage nur für den
jeweiligen Benutzer zugänglich ist.

Natürlich beinhaltet dieser Release wiederum zahlreiche weitere allgemeine Anpassungen und Korrekturen.

Persönliche Ablage
------------------

|img-release-notes-3.10-1|

Unter dem neuen Hauptreiter "Meine Ablage" steht mit diesem neuen Feature für jeden
Benutzer ein persönlicher Bereich zur Verfügung. Dieser verhält sich bezüglich Funktionalität
und Aussehen ähnlich wie eine gewöhnliche Ordnungsposition, in der Dossiers mit
Dokumenten erstellt werden können. Auch die Mail-in Funktionalität steht bei einem
persönlichen Dossier zur Verfügung. Die persönliche Ablage ist jedoch nur vom
jeweiligen Benutzer einsehbar und nicht öffentlich.

Die persönliche Ablage ist standardmässig nicht aktiviert und kann pro Mandant eingerichtet werden.

`Dokumentation <https://docs.onegovgever.ch/meine_ablage/>`_

Defaultwerte
------------

- Werte werden neu auch gespeichert, wenn sie dem Default-Wert entsprechen.

- Beim Erstellen neuer Inhalte werden Default-Werte und Missing-Werte auch für
  Felder gesetzt, die keinen vom Benutzer eingegebenen Wert einhalten.

Sitzungs- und Protokollverwaltung
---------------------------------

- Für den Jahresabschluss können neu Inhaltsverzeichnisse aller Anträge
  eines Kalenderjahres erstellt werden.

- Der Editor der Sitzungs- und Protokollverwaltung wird nun deutlich schneller
  geladen. Dies steigert die Performance und Usability bei der Protokollierung.

- Start- und End-Datum einer Periode müssen neu zwingend angegeben werden.

- Ein neues Tab listet alle Perioden eines Gremiums übersichtlich auf.

Kleinere Anpassungen
--------------------

|img-release-notes-3.10-2|

Zudem wurden folgende weiteren kleineren Anpassungen für diesen Release umgesetzt:

- In jedem Dossier können neu manuelle Journaleinträge hinzugefügt werden (siehe Screenshot).

- Wird eine Ordnungsposition auf gleicher Stufe wie ein Dossier erstellt, wird ein Warnhinweis eingeblendet.

- Weitere Verbesserungen beim Kopieren und Einfügen von Objekten, Dossiers können
  nicht mehr auf gleicher Stufe wie eine Ordnungsposition eingefügt werden.

- Verbesserung beim Schreiben von DocProperties, diese können neu DocProperties
  eines falschen Typs überschreiben.

- Die Dateinamen der Beilagen eines Antrags stehen neu beim Erstellen der Protokolle zur Verfügung.

- Die Dokumentauflistung eines Dossiers oder Subdossiers kann neu als Excel-Report exportiert werden.

- Fehlerbehandlung beim Drag&Drop Upload wurde verbessert, so dass keine Dateien
  zurückbleiben, wenn beim Upload ein Fehler aufgetreten ist. Dies bedeutet auch, dass
  keine passwortgeschützten Dokumente oder korrupte Dateien mehr hochgeladen werden können.

Bugfixes
--------

- Ein Problem beim Navigieren einer Seite mittels der Zurück-Funktion des Browsers
  wurde behoben. Es war unter Umständen erforderlich, den Zurück-Button zweimal zu betätigen.

- Ein Bug beim Extrahieren von Anhängen eines Mails im Eingangskorb wurde behoben.

- Bei der visuellen Suche werden die korrekten Fallback-Bilder dargestellt.

- Nach dem Kopieren von Dossiers werden die Aktenzeichen von Subdossiers des kopierten Dossiers korrekt generiert.

- XSS Sicherheitslücke bei der Antragsübersicht entfernt.

- Die Sortierung der Journaleinträge wurde korrigiert.

- Berechtigungsproblem beim Bearbeiten von Verweisen einer mandantübergreifenden Aufgabe wurde behoben.

- Ein Problem mit der Grösse des Vorschaubildes wurde behoben.

- Ein Problem beim Filtern der Benutzer bei der OGDS-Synchronisation wurde behoben.

.. |img-release-notes-3.10-1| image:: ../../_static/img/img-release-notes-3.10-1.png
.. |img-release-notes-3.10-2| image:: ../../_static/img/img-release-notes-3.10-2.png

.. disqus::
