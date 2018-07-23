OneGov GEVER Release 2017.7
===========================

Im Release 2017.7 konnten wir gleich drei `OGIPs <https://docs.onegovgever.ch/user-manual/glossary/#term-ogip>`_ umsetzen: Die persönliche
Einstellung des Benachrichtigungs-Systems (OGIP 29), die flexiblere Rechtevergabe
mittels Schützen eines Dossiers (OGIP 23) sowie die Teamaufgaben (OGIP 24).
Weiter ist mit diesem Release auch unsere neue Sitzungs- und Protokollverwaltung verfügbar.
Weitere kleine Anpassungen wurden am User-Interface, der Aussonderungsschnittstelle
sowie der privaten Ablage vorgenommen. Wie immer haben wir auch diverse kleine
Fehlerkorrekturen (Bugfixes) durchgeführt.

Individuelle Benachrichtigungs-Einstellungen
--------------------------------------------

Mit der Umsetzung des `OGIP 29 <https://my.teamraum.com/workspaces/onegov-gever-innovation-session?overlay=7467927462404ef09d17a1982aefb543#documents>`_
kann nun die `Benachrichtigung pro Aktivität <https://docs.onegovgever.ch/user-manual/benachrichtigung/>`_
individuell eingestellt werden. Dadurch können Sie definieren, ob Sie beispielsweise
bei einer neuen Aufgabe als Auftraggeber oder als Auftragnehmer benachrichtigt
werden möchten sowie ob dies direkt in OneGov GEVER gemacht werden soll oder via
E-Mail. Die untenstehende Übersicht zeigt jeweils den aktuellen Stand der geltenden Regeln.

|img-release-notes-2017.7-1|

Dossier schützen
----------------

Mit der Umsetzung des `OGIP 23 <https://my.teamraum.com/workspaces/onegov-gever-innovation-session?overlay=b8e6f9e71d764d93a270cbd729a27254#documents>`_ können neu die übergreifend definierten Berechtigungen
unterbrochen werden. Dadurch kann die Rechte-Vergabe vor allem in grossen Organisationseinheiten
flexibler gestaltet werden. Benutzer mit der neuen Berechtigung "Dossier verwalten"
können die Vererbung unterbrechen und neuen Benutzern "lesend" oder "lesend und schreibend"
Zugriff auf eine Ordnungsposition oder ein Dossier geben. Details können in der Dokumentation
unter `"Dossier schützen" <https://docs.onegovgever.ch/admin-manual/berechtigungoe/>`_ nachgelesen werden.

|img-release-notes-2017.7-2|

Admin-Ansicht für geschützte Objekte
------------------------------------

Als Administrator erscheint neu unter Ordnungssystem das zusätzliche Tab "Geschützte Objekte".
Darunter werden alle Ordnungspositionen und Dossiers aufgelistet, bei welchen die
übergeordnete Berechtigung unterbrochen wurde. Die Berechtigung unterbrechen können
Personen die entweder `Rollenmanager <https://docs.onegovgever.ch/admin-manual/rollenmanager/>`_ sind oder die Berechtigung
haben, `"Dossiers zu schützen" <https://docs.onegovgever.ch/admin-manual/berechtigungoe/>`_ .

|img-release-notes-2017.7-3|

Teamaufgaben
------------

Mit den `Teamaufgaben <https://docs.onegovgever.ch/user-manual/aufgaben/teamaufgaben/>`_ können Aufgaben an AD-Gruppen adressiert werden. Die Aufgaben
werden wie gewohnt erfasst, als Auftragnehmer wird das Team hinterlegt. Die Aufgabe
erscheint dann bei allen Teammitgliedern als pendente Aufgabe. Sobald ein Teammitglied
die Aufgabe akzeptiert, wird dieser Benutzer alleiniger Auftragnehmer und die Aufgabe
erscheint bei den anderen Teammitgliedern nicht mehr. Somit können mehrere potentielle
Auftragnehmer mit einer Aufgabe adressiert werden. Dieses Bedürfnis wird
in `OGIP 24 <https://my.teamraum.com/workspaces/onegov-gever-innovation-session?overlay=a5f98fa002784d7084dff6360e223674#documents>`_ im Detail spezifiziert.

|img-release-notes-2017.7-4|

Sitzungs- und Protokollverwaltung 2.0
-------------------------------------

Mit diesem Release ist auch die neue Sitzungs- und Protokollverwaltung 2.0 verfügbar.
Damit steigen wir von der Web-Protokollierung auf die Word-Protokollierung um,
womit Word-Funktionalitäten wie das Einfügen von Bildern oder das Erstellen von
Tabellen neu möglich sind. Weiter können nun Antragsvorlagen individuell pro Gremium
erstellt werden. Auch das Design - konkret die Sitzungsansicht - wurde überarbeitet
und benutzerfreundlicher gestaltet. Neu können auch mehrere Protokollauszüge pro
Traktandum auf einfache Art erstellt werden. Ebenfalls neu ist die Möglichkeit, eine
Aufgabe direkt aus einem Traktandum zu erstellen (Protokollauszug als Anhang).

Ein detaillierter Beschrieb zum Funktionsumfang der Sitzungs- und Protokollverwaltung
finden Sie `hier <https://docs.onegovgever.ch/user-manual/spv/>`_ in unserer Dokumentation.

|img-release-notes-2017.7-5|

Diverse Anpassungen
-------------------

- Design: `neue Mimetype-Icons <https://feedback.onegovgever.ch/t/bereitstellung-neuer-icons/779/7>`_

- Aussonderungs-Schnittstelle: Verbesserung des Dateinamens beim Download der Bewertungsliste

- Private Ablage: private Dokumente und Dossiers in der privaten Ablage können neu gelöscht werden

- Sonstige kleine Fehlerkorrekturen (Bugfixes)

.. |img-release-notes-2017.7-1| image:: ../_static/img/img-release-notes-2017.7-1.png
.. |img-release-notes-2017.7-2| image:: ../_static/img/img-release-notes-2017.7-2.png
.. |img-release-notes-2017.7-3| image:: ../_static/img/img-release-notes-2017.7-3.png
.. |img-release-notes-2017.7-4| image:: ../_static/img/img-release-notes-2017.7-4.png
.. |img-release-notes-2017.7-5| image:: ../_static/img/img-release-notes-2017.7-5.png

.. disqus::
