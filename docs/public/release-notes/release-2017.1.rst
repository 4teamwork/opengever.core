OneGov GEVER Release 2017.1
===========================

Mit diesem **Major-Release** beschreitet OneGov GEVER neue Wege im Records
Management und bietet zahlreiche Neuerungen. Nebst den vielfältigen
Möglichkeiten von **Dossiervorlagen**, einem persönlichen Ablagebereich, **Notizmöglichkeiten**
sowie **Dossier-Tagging** mittels Schlagwörtern steht nun der vollständige
**Aussonderungsprozess** von Dossiers mittels Standardschnittstelle **eCH-0160** zur Verfügung.

Über die neu definierte **Importspezifikation OGGBundle** können bestehende Datenbestände
aus Drittsystemen noch unkomplizierter in OneGov GEVER übernommen werden.
Die überarbeitete Version des **OfficeConnectors** für Windows sowie Mac OS X bietet
eine noch stärkere Integration in die Office Umgebung des Benutzers.

Schlagwörter
------------

|img-release-notes-2017.1-1|

Das Tagging von Dossiers (oder Dossiervorlagen) kann neu deutlich komfortabler
vorgenommen werden. Dabei werden bereits vergebene Schlagwörter automatisch zur
Auswahl vorgeschlagen. Zudem kann über die Suche mittels Schlagwörtern nach
Dossiers gesucht werden. Die Schlagwörter eines Dossiers werden neu auch im
Übersichtsreiter des Dossiers eingeblendet.

Dossiervorlagen
---------------

|img-release-notes-2017.1-2|

Vordefinierte **Dossiervorlagen** eröffnen neue Möglichkeiten, um gleichartige Geschäfte
auf die gleiche Art und Weise zu erfassen und zu strukturieren. So können für typische
Geschäftsfälle (z.B. Informatikprojekt, Baugesuch, Personaldossier, etc.)
sogenannte Dossiervorlagen im Vorlagenbereich von OneGov GEVER erstellt werden.
Eine Dossiervorlage kann dabei beliebige Subdossiers und Dokumente beinhalten, die
dann bei der Erstellung eines Dossiers im Ordnungssystem ab dieser Vorlage kopiert werden.
So kann sichergestellt werden, dass gleichartige Geschäfte in OneGov GEVER immer gleich
strukturiert werden.

Damit die Titel gleichartiger Geschäfte immer gleich aufgebaut werden, kann in der
Dossiervorlage zusätzlich eine **Titelhilfe** (z.B. "<Personalnummer> - <Nachname>, <Vorname> - <Geburtsdatum
in der Form TT.MM.JJJJ>") hinterlegt werden, die dem Benutzer bei der Erstellung eines neuen Dossiers
aus einer Vorlage angezeigt wird. Dies hilft ihm oder ihr, alle relevanten Informationen eines Geschäfts
im Titel des Dossiers aufzuführen, wobei der Titel immer gleich aufgebaut wird
(z.B. "04329.1 - Muster, Hans - 18.09.1980").

Jede Dossiervorlage kann bereits vordefinierte Schlagwörter ("Personaldossier",
"Baugesuch", etc.) besitzen, die bei Dossiererstellung entweder automatisch
vergeben werden oder zur Auswahl stehen.

Im Vorlagenbereich können beliebig viele Dossiervorlagen durch entsprechend
berechtigte Benutzer erstellt und gepflegt werden. Ausserdem kann der Records
Manager **pro Rubrik** im Ordnungssystem die **Auswahl an möglichen Dossiervorlagen
beschränken**, so dass in dieser Rubrik nur noch neue Dossiers gemäss erlaubten
Dossiervorlagen erstellt werden können.

Dossierkommentare
-----------------

|img-release-notes-2017.1-3|

Kommentare und kurze persönliche Notizen zu einem Geschäft können neu sehr rasch
über den Reiter Dossier-Übersicht erfasst werden. Das Notizblock-Symbol neben
dem Dossiertitel zeigt auf einen Blick, ob zum Dossier bereits Notizen vorhanden
sind. Dabei kann das Kommentarfeld direkt durch Anklicken des Symbols
aufgerufen und bearbeitet werden.

Persönliche Ablage
------------------

Neu kann für jeden Benutzer mit der **persönlichen Ablage** ein persönlicher Ablagebereich
für Dokumente eingerichtet werden. Dort kann der Benutzer Dokumente und E-Mails
ablegen (vorregistrieren), ohne sich bereits über den konkreten Ablageort innerhalb
des Ordnungssystems Gedanken machen zu müssen. Die Dokumente können danach aus
der persönlichen Ablage, die nur dem Benutzer selber zugänglich ist, in ein Dossier
innerhalb des Ordnungssystems verschoben werden.

Der zur Verfügung stehende Speicherplatz pro persönliche Ablage kann limitiert
werden (z.B. auf 200 MB), wobei der Benutzer bereits vor Erreichen der Speicherbegrenzung
gewarnt wird, falls sein persönlicher Speicherplatz knapp wird. Ist der Speicher
ausgeschöpft, kann der Benutzer keine weiteren Dokumente mehr hinzufügen.

Aussonderung
------------

Als optional aktivierbares Modul wird neu in OneGov GEVER auch der **komplette
Aussonderungsprozess** von Dossiers unterstützt! Von der Angebotserstellung über
die Angebotsbewertung bis hin zur SIP-Paketierung gemäss Standard **eCH-0160** wurde
der gesamte Prozess inkl. automatischer Erzeugung von archivtauglichen Dokumentformaten
vollständig in OneGov GEVER integriert.

Der Aussonderungsprozess wurde von 4teamwork **gemeinsam mit mehreren Staatsarchiven**
entwickelt und umgesetzt. Da sich der Aussonderungsprozess sehr umfangreich gestaltet,
wird an dieser Stelle für weitere Informationen auf
die `Online-Dokumentation <https://docs.onegovgever.ch/admin-manual/aussonderung/>`_ verwiesen.

Sitzungs- und Protokollverwaltung
---------------------------------

|img-release-notes-2017.1-4|

Alle Unterlagen zu einer Sitzung können neu als Zip-Datei heruntergeladen werden.
Die Zip-Datei beinhaltet neben der Traktandenliste das Vorprotokoll sowie
sämtliche Anhänge zu den Traktanden. Dies erleichtert die Sitzungsvorbereitung,
da alle Sitzungsunterlagen als Zip-Datei an die Teilnehmenden verteilt werden können.

Office Connector
----------------

Der Office Connector wurde noch weiter ausgebaut, so dass nach der Bearbeitung
von Dokumenten diese über den Office Connector direkt eingecheckt werden können.
Zudem können Dokumente aus OneGov GEVER über Outlook versendet werden, wobei eine
Kopie der versendeten E-Mails automatisch wieder in OneGov GEVER abgelegt wird.

Der Office Connector Windows ist abwärtskompatibel zum bestehenden External Editor,
bietet aber deutlich weitergehende Möglichkeiten bei der Bearbeitung von Dokumenten.

Importspezifikation OGGBundle
-----------------------------

Mit sog. OGGBundles (kurz für OneGov GEVER Bundle) bieten wir neu ein standardisiertes
Importformat für den initialen Datenimport in OneGov GEVER an. Über ein Bundle können
beim Aufsetzen von OneGov GEVER Daten in einer für grosse Datenmengen optimierten
Pipeline importiert werden. Dies macht eine Datenmigration aus einem Drittsystem
nach OneGov GEVER noch viel einfacher.

Die aktuelle Spezifikation des OGGBundle ist in
der `Entwicklerdokumentation <https://docs.onegovgever.ch/dev-manual/oggbundle/>`_ öffentlich verfügbar.

Weitere Anpassungen und Neuerungen
----------------------------------

Der Release enthält weitere zahlreiche kleinere Anpassungen und Bugfixes, u.a.:

- Falls noch kein End-Datum eines Dossiers eingegeben wurde, wird
  dieses beim Abschliessen des Dossiers automatisch gesetzt.

- Wird ein bereits abgeschlossenes Dossier wieder eröffnet oder ein storniertes
  Dossier reaktiviert, so wird das End-Datum wieder zurückgesetzt.

.. |img-release-notes-2017.1-1| image:: ../_static/img/img-release-notes-2017.1-1.png
.. |img-release-notes-2017.1-2| image:: ../_static/img/img-release-notes-2017.1-2.png
.. |img-release-notes-2017.1-3| image:: ../_static/img/img-release-notes-2017.1-3.png
.. |img-release-notes-2017.1-4| image:: ../_static/img/img-release-notes-2017.1-4.png

.. disqus::
