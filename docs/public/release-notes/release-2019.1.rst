OneGov GEVER Release 2019.1
===========================

Durch den Release 2019.1 erhielt vor allem das Element «Dossier» neue
Funktionalitäten: einen Schlagwortfilter für Dossierauflistungen und einen
Filter sowie Benachrichtigungsmöglichkeit für überfällige Dossiers. Weiter
wurde eine Vielzahl von Korrekturen eingespielt sowie generelle Verbesserungen
vorgenommen.

Schlagwortfilter für Dossierauflistungen
----------------------------------------
Neu erscheint bei Dossierauflistungen ein Schlagwortfilter. Dadurch kann mittels
Schlagwort(en) nach einem Dossier gesucht werden.


Überfällige Dossiers: Filter und Benachrichtigung
-------------------------------------------------
Nach überfälligen Dossiers kann ab diesem Release mittels Filter gesucht werden.

|img-release-notes-2019.1-1|

Weiter kann in den Benachrichtigungs-Einstellungen eine Erinnerung gesetzt werden,
damit der Benutzende benachrichtigt wird, wenn ein Dossier überfällig wird.

|img-benachrichtigungs-einstellungen-5|

Diverse Verbesserungen:
-----------------------

-	Abgeschlossene Dossiers stehen beim Verschieben nicht mehr zur Auswahl

-	Berechtigungen werden beim Kopieren von Inhalten übernommen

-	Aufgaben werden beim Koiper-Vorgang nicht mitkopiert

-	Performanceverbesserung beim OfficeConnector

-	Verbesserte Darstellung der Beschreibung in der Dokumentvorschau

-	Teammitglieder können analog zu Gruppenmitgliedern aufgelistet werden

-	Ausbau der OneOffixx Schnittstelle

- API-Erweiterung: Mittels der API können ab diesem Release Servicebenutzende Inhalte im Namen bestehender Benutzer erstellen

Sitzungs- und Protokollverwaltung (SPV):
----------------------------------------

- Die Beschreibung für Traktanden stehen im Inhaltsverzeichnis neu zur Verfügung

- Gremium: Die hinterlegten Vorlagen werden übersichtlicher dargestellt

- Neue Inhaltsverzeichnis mit unterschiedlichen Gruppierungs-Möglichkeiten: 1.) Gruppierung nach Positionsnummer der Ursprungs-Ordnungsposition 2.) Gruppierung nach Aktenzeichen des Ursprungs-Dossiers

- Abwesende Mitglieder können im Protokoll eingefügt werden

- Traktandennummer kann ohne Punkt in Protokoll/Traktandenlisten eingefügt werden

- Beim Erstellen eines Antrages ab bestehendem Dokument werden nur noch docx-Dateien als Antragsdokumente vorgeschlagen

Bugfixes
--------

- Darstellung Favoriten-Button bei langen Titeln korrigiert

- Sortierung der Favoriten beim Löschen von Favoriten korrigiert

- Keine Möglichkeit mehr, leere Aufgaben-PDFs beim Dossierabschluss zu erstellen

- Mails im Eingangskorb für Auftragnehmer nun immer sichtbar

- Mails im Eingangskorb generell wieder korrekt bearbeitbar

- Korrektur Inhalt-Sortierung

- Korrektur Vorschau für die Dokumenttypen: 'xls' 'indd', 'vsdx', 'vstx', 'vssx'

- SPV: Automatisches Aktualisieren der Doc-Properties von Protokoll und Traktandenliste

- SPV: Änderungsdatum von Protokoll und Traktandenliste werden korrekt aktualisiert

- SPV: Darstellung Protokollauszug korrigiert, falls Benutzer keine Rechte hat, die Sitzung zu sehen

- SPV: Korrektur Darstellung der Mitglieder einer Sitzung

- Tooltip im Eingangskorb erscheint korrekt

- Filter-Eingabe von Bindestrichen korrigiert, wenn Enterprise Search aktiviert ist

- Problem bei E-Mail Benachrichtigungen beim Einreichen von Anträgen korrigiert

- Private Aufgaben können nicht mehr fälschlicherweise erstellt werden

- Zip-Export garantiert nun eindeutige Dateinamen

- Zip-Export überspringt nun Dokumente ohne Datei

- Doc-Properties erscheinen beim Aktualisieren nicht mehr doppelt in Word-Dokumenten

- Benutzerkürzel für Mail-Autor wird korrekt aufgelöst

- Subdossier-Link in Auflistungen wird nun korrekt dargestellt

.. |img-release-notes-2019.1-1| image:: ../_static/img/img-release-notes-2019.1-1.png
.. |img-benachrichtigungs-einstellungen-5| image:: ../user-manual/img/media/img-benachrichtigungs-einstellungen-5.png

.. disqus::
