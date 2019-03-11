OneGov GEVER Release 2018.1
===========================

Der Release 2018.1 ist vollgepackt mit Neuerungen und Verbesserungen. So konnte
der `OGIP 19 – Persönliche Ablage <https://my.teamraum.com/workspaces/onegov-gever-innovation-session/ogip?overlay=9f478d4a654948889bf0383e98c0d05b#documents>`_ fertiggestellt sowie
der `OGIP 29 - Benachrichtigungsfunktion <https://my.teamraum.com/workspaces/onegov-gever-innovation-session/ogip?overlay=7467927462404ef09d17a1982aefb543#documents>`_ erweitert werden. Weiter haben wir auch
die `SPV <https://docs.onegovgever.ch/user-manual/spv/>`_ optimiert und viele kleine Korrekturen vorgenommen, die Ihren GEVER-Alltag erleichtern.

OGIP 19 - Persönliche Ablage
----------------------------

Mit diesem Release wird durch die Ergänzung des Präfix „P“ beim Aktenzeichen in
der privaten Ablage der `OGIP 19 <https://my.teamraum.com/workspaces/onegov-gever-innovation-session/ogip?overlay=9f478d4a654948889bf0383e98c0d05b#documents>`_ finalisiert.

|img-release-notes-2018.1-1|

Folgende Erweiterungen wurden durch den `OGIP 19 <https://my.teamraum.com/workspaces/onegov-gever-innovation-session/ogip?overlay=9f478d4a654948889bf0383e98c0d05b#documents>`_ durchgeführt:

- Löschen von Dokumente und Dossiers ermöglichen

- Funktion Deckblatt und Details entfernen

- Position in der Hauptnavigation überarbeiten

- Präfix „P“ beim Aktenzeichen

Erweiterung `OGIP 19 <https://my.teamraum.com/workspaces/onegov-gever-innovation-session/ogip?overlay=9f478d4a654948889bf0383e98c0d05b#documents>`_ : Zudem wurde das Rollenkonzept verbessert. Die neue Rolle
„MemberAreaAdministrator“ hat den Zugriff auf alle Ablagen zu Support-Zwecken,
dafür hat der Administrator neu keinen Zugriff mehr. Bei Bedarf dieser Erweiterung
nehmen Sie bitte via Support-Ticket Kontakt mit uns auf, um dies zu aktivieren.

Erweiterung OGIP 29 - Benachrichtigungsfunktion
-----------------------------------------------

Der `OGIP 29 <https://my.teamraum.com/workspaces/onegov-gever-innovation-session/ogip?overlay=7467927462404ef09d17a1982aefb543#documents>`_ wurde um die Möglichkeit erweitert, sich eine Tageszusammenfassung
(Daily Digest) per Mail zuschicken zu lassen. Die Details zu allen
Benachrichtigungsfunktionen finden Sie in der `Dokumentation <http://docs.onegovgever.ch/user-manual/benachrichtigung/>`_ .

|img-release-notes-2018.1-2|

Neue Tabs
---------

Auf Ordnungspositionsstufe werden neu auch die Tabs "Dokumente" und "Aufgaben"
angezeigt, um eine bessere Übersicht zu gewährleisten, was innerhalb dieser Position abgelegt ist.

|img-release-notes-2018.1-3|

Batching-Container
------------------

Der Batching-Container zur Navigation über viele Inhalte (Anzeiger, wie lange Liste
mit Elementen noch ist) wird nun zusätzlich auch am Anfang (oben) an der Tabelle angezeigt.

|img-release-notes-2018.1-4|

Office Connector / Mit Dokumenten arbeiten
------------------------------------------

Neu wird die Möglichkeit zum Auschecken/Bearbeiten nur für Dateien dargestellt,
die vom Office Connector unterstützt werden. Dies muss entsprechend konfiguriert
werden. Bei Interesse nehmen Sie bitte via Support-Tracker Kontakt mit uns auf.

Zudem steht für Administratoren neu die Aktion "Vorschau neu generieren" zur Verfügung.

|img-release-notes-2018.1-5|

Die Aktions-Buttons für Dokumente wurden ebenfalls überarbeitet und haben dadurch
eine neue Positionierung erhalten, damit die relevanten Informationen besser ersichtlich sind.

|img-release-notes-2018.1-6|

Cross-Tab Logout
----------------

Annahme: Ein Benutzender arbeitet mit mehreren Tabs. Meldet er sich in einem Tab
ab, wird er neu in allen Tabs automatisch auch abgemeldet. Diese Funktion fand
ihren Ursprung am `Fedex Day 2017 <https://www.4teamwork.ch/blog/onegov-gever-fedex-day-2017>`_ . Abgrenzung: Die Funktion tritt nur
in den Browsern Firefox und Chrome in Kraft.

Sitzungs- und Protokollverwaltung
---------------------------------

- Antragsdokumente können neu auch an Aufgaben angehängt werden

- Freitext-Traktanden sind nun auch im Zip-Export enthalten

- Mitgliedschaften werden neu nach Nachnamen sortiert

- Beilagen für Anträge werden neu alphabetisch sortiert

- Bei den `Sablon-Vorlagen <https://docs.onegovgever.ch/admin-manual/meeting/mergefields/>`_ kann neu Vor- und Nachname separat ausgewiesen werden.
  Natürlich bleibt die Möglichkeit beide zusammen zu nehmen (fullname) noch bestehen.

- Problem beim Aktualisieren der Doc-Properties behoben

- Diverse kleinere Verbesserungen

Diverses
--------

- Diverse Performanceverbesserungen vorgenommen

- Neues `Doc-Property <https://docs.onegovgever.ch/admin-manual/docproperties/list/#doc-properties-dokument>`_ verfügbar: ogg.document.version_number

- Neue Mime-Type Icons für Keynote, Numbers und Pages verfügbar

- Live-Suche zeigt neu das Mime-Type Icon an

- Dateiname und Dateigrösse wird neu in der Dokument-Vorschau im Overlay angezeigt

- Vorlagen-Ordner können neu durch Administratoren und Editoren entfernt werden

- Problem mit falscher Anzahl der ungelesenen Benachrichtigungen behoben

- Probleme bei Kommas in LDAP-Pfad behoben

- Neueste REST API aktiviert ( `Release 1.0.0 <https://www.4teamwork.ch/blog/endlich-restful-api-release-1-0.0>`_ )

- Dokumentvorschau für \*.bmp und \*.ini Dateien neu verfügbar

- Diverse Bugfixes und kleinere Verbesserungen vorgenommen

.. |img-release-notes-2018.1-1| image:: ../_static/img/img-release-notes-2018.1-1.png
.. |img-release-notes-2018.1-2| image:: ../_static/img/img-release-notes-2018.1-2.png
.. |img-release-notes-2018.1-3| image:: ../_static/img/img-release-notes-2018.1-3.png
.. |img-release-notes-2018.1-4| image:: ../_static/img/img-release-notes-2018.1-4.png
.. |img-release-notes-2018.1-5| image:: ../_static/img/img-release-notes-2018.1-5.png
.. |img-release-notes-2018.1-6| image:: ../_static/img/img-release-notes-2018.1-6.png

.. disqus::
