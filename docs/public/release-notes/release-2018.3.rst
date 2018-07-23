OneGov GEVER Release 2018.3
===========================

Mit dem Release 2018.3 wurde der OGIP 32, welcher sich um das Setzen von
Favoriten-Elementen kümmert, umgesetzt. Neu ist auch die bessere Erkennung eines
ausgecheckten Dokumentes mittels orangem Punkt am Icon. Weiter wurde die
GEVER-Schnittstelle (API) erweitert sowie diverse Korrekturen vorgenommen.

OGIP 32 - Favoriten
-------------------

Mit der Umsetzung des OGIP 32 können neu Dossiers und Dokumente als Favoriten
gesetzt werden. Eine Ordnungsposition zu favorisieren bleibt natürlich weiterhin
bestehen. Die gesetzten Favoriten können in einer zentralen Übersicht betrachtet,
bearbeitet oder gelöscht werden. Ausgeschlossen von der Favorisierung sind Inhalte
der Sitzungs- und Protokollverwaltung. Mehr Details finden Sie in unserer `Dokumentation <https://docs.onegovgever.ch/user-manual/favoriten/>`_ .

|img-release-notes-2018.3-1|

|img-release-notes-2018.3-2|

Kennzeichnung eines ausgecheckten Dokumentes
--------------------------------------------

Neu wird ein ausgechecktes Dokument orange markiert, damit der Verfügbarkeits-Status
des Dokuments für GEVER-Benutzende schneller ersichtlich wird:

- Ein gefüllter oranger Punkt falls der Benutzende selbst das Dokument ausgecheckt hat

- Ein oranger Ring, wenn das Dokument durch einen anderen Benutzer ausgecheckt wurde

|img-release-notes-2018.3-3|

Aufgabenmodul: Benachrichtigunsmail
-----------------------------------

Das per default automatisch ausgelöste Mail bei Zuweisung einer neuen Aufgabe
enthält neu die zusätzliche Information, wer Auftraggeber und wer Auftragnehmer dieser Aufgabe ist.

|img-release-notes-2018.3-4|

Diverses
--------

- Im Reiter Info (Ansicht, welche Gruppen welche Rollen resp. Freigaben besitzen) kann neu
  der Gruppentitel anstelle der teilweise kryptischen Gruppenbezeichnung angezeigt werden.

- Bei den `Teamaufgaben <https://docs.onegovgever.ch/user-manual/aufgaben/teamaufgaben>`_ kann
  der Administrator ab sofort neue Teams erfassen. Zuvor war dies nur durch Mitarbeitende von 4teamwork AG möglich.

- Soll ein Checkout wiederrufen werden, muss dies neu nochmals bestätigt werden

- Bei der Sitzungs- und Protokollverwaltung wird die Protokollführung neu direkt
  beim Erstellen der Sitzung definiert. Neu ist auch, dass nicht nur Gremiums-Mitglieder
  die Protokollführung übernehmen können, sondern alle die ein GEVER-Login dieses
  Unternehmen/Verwaltung besitzen.

.. |img-release-notes-2018.3-1| image:: ../_static/img/img-release-notes-2018.3-1.png
.. |img-release-notes-2018.3-2| image:: ../_static/img/img-release-notes-2018.3-2.png
.. |img-release-notes-2018.3-3| image:: ../_static/img/img-release-notes-2018.3-3.png
.. |img-release-notes-2018.3-4| image:: ../_static/img/img-release-notes-2018.3-4.png

.. disqus::
