OneGov GEVER Release 3.5
========================

Sitzungs- und Protokollverwaltung
---------------------------------
Das Modul „Sitzungs- und Protokollverwaltung“ wurde seit Herbst 2014 von
4teamwork in Zusammenarbeit mit diversen **Gemeinden und Verwaltungen**
entwickelt und steht nun ab Release 3.5 für den produktiven Einsatz zur
Verfügung.

Die Sitzungs und Protokollverwaltung wurde vollständig in OneGov GEVER
integriert. Sie bietet eine Mitglieder- und Kommissionsverwaltung, Anträge
und Sitzungsplanung und Protokollierung.

Kommissionen, Sitzungen und Anträge sind eng mit dem Ordnungssystem und mit
Dossiers verknüpft. Sitzungsdossiers werden automatisch erstellt,
Sitzungsdokumente wie Protokolle und Protokollauszüge können einfach im
Ordnungssystem abgelegt werden. Traktandenlisten, Protokolle und
Protokollauszüge können einfach per WYSIWYG-Editor direkt im Webbrowser sehr
rasch und unkompliziert erfasst werden. Über hinterlegbare Wordvorlagen können
daraus die entsprechenden Dokumente per Knopfdruck erzeugt und in den
zugehörigen Dossiers abgelegt werden. Die Verwaltung von Sitzungen und
Protokollen wird so zum Kinderspiel!


Kommissions- und Gremienverwaltung
----------------------------------
- Pro Kommission (oder Gremium) kann eine eigene Berechtigungsgruppe
  festgelegt werden, die diese Kommission verwalten und einsehen kann.
- Kommissionen sind mit einer Ablageposition im Ordnungssystem verknüpft.
  Dort wird automatisch ein neues Sitzungsdossier erstellt, in welches alle
  Sitzungsunterlagen und -protokolle abgelegt werden.
- Pro Kommission können eigene Wordvorlagen für Protokolle und
  Protokollauszüge hinterlegt werden.
- Für jede Kommission können Geschäftsperioden definiert und Mitglieder und
  deren Rollen erfasst werden.

|img-release-notes-3.5-1|


Anträge
-------
- Anträge werden dossiergebunden erstellt. Soll ein Geschäft in einer
  Kommission behandelt werden, muss in einem Geschäftsdossier ein neuer
  Antrag erstellt und bei einer Kommission zur Behandlung eingereicht werden.
- Pro Antrag kann eine beliebige Auswahl an Anhängen aus dem
  Geschäftsdossier an die Kommission mitgeliefert werden.
- Nach der Erstellung eines Antrags kann dieser noch erweitert oder
  angepasst werden. Sind alle nötigen Informationen erfasst, wird der Antrag
  durch den Antragsteller eingereicht und steht dann in Sitzungsverwaltung
  der jeweiligen Kommission zur Verfügung.
- Jede Veränderung an einem noch nicht eingereichten Antrag wird
  journalisiert; bereits eingereichte Anträge können durch den Antragsteller
  nicht mehr verändert werden.

|img-release-notes-3.5-2|


Sitzungen vorbereiten und traktandieren
---------------------------------------

- Für jede neue Sitzung wird vom System automatisch ein entsprechendes
  Sitzungsdossier in der mit der Kommission verknüpften Rubrik im
  Ordnungssystem erstellt.
- In der Sitzungsplanung ist es möglich, eingereichte Anträge der Kommission
  einfach zu traktandieren. Des Weiteren können neue Freitext-Traktanden
  definiert und mit Abschnitten (z.B. A- und B-Geschäfte) strukturiert werden.
- Traktanden können mit Drag&Drop verschoben und neu geordnet werden.
- Sämtliche Nummerierungen (Sitzungen, Traktanden, Beschlüsse) werden
  automatisch durch OneGov GEVER vorgenommen.

|img-release-notes-3.5-3|


Protokollieren und Sitzungsabschluss
------------------------------------
- In der Protokollansicht steht für jedes Traktandum alle Felder für die
  direkte Bearbeitung zur Verfügung. So kann während der Sitzung das
  Protokoll (pro Traktandum) laufend direkt im Webbrowser ergänzt werden.
  Ausgewählte Formatierungsmöglichkeiten stehen über den eingebauten
  WYSIWYG-Editor zur Verfügung.
- Die Protokollansicht ist so aufgebaut, dass die Protokollierung sehr
  einfach direkt im Webbrowser möglich ist. Über die eingebaute
  Traktandennavigation kann sehr rasch zwischen verschiedenen Protokollen
  hin- und hernavigiert werden.
- Weitere Sitzungsinformationen wie teilnehmende Personen, Protokollführer,
  etc. können ebenfalls erfasst werden.
- Traktanden können einzeln abgeschlossen werden. Beim Abschluss wird
  automatisch ein Protokollauszug generiert und ins Dossier des
  Antragstellers zurückgespielt.
- Bei Sitzungsabschluss wird zudem automatisch ein generiertes
  Beschlussprotokoll im Sitzungsdossier abgelegt.

|img-release-notes-3.5-4|


Nachvollziehbarkeit
-------------------
Die Sitzungs- und Protokollverwaltung gewährleistet, wie überall in OneGov
GEVER, die Nachvollziehbarkeit und Transparenz aller relevanten Aktionen, wie
dies von Records Management Systemen gefordert wird.

|img-release-notes-3.5-5|


Mehrsprachigkeit
----------------
Die Hauptelemente und das Ordnungssystem von OneGov GEVER können neu
mehrsprachig geführt werden.


Verbesserungen der Security
---------------------------
Plone hat in einem `Patch <https://plone.org/download>`_ den Schutzmechanismus
gegen Cross-Site-Request-Forgery (`CSRF <https://de.wikipedia.org/wiki/Cross-Site-Request-Forgery>`_)
verbessert. Wir haben diesen Schutzmechanismus mit demjenigen von GEVER aus
dem :doc:`Release 3.2 <release-3.2>` zusammengeführt.


Benachrichtigungssystem
-----------------------
Am Benachrichtigungsystem wurden diverse kleinere Bugfixes und Verbesserungen
vorgenommen.

.. |img-release-notes-3.5-1| image:: ../../_static/img/img-release-notes-3.5-1.png
.. |img-release-notes-3.5-2| image:: ../../_static/img/img-release-notes-3.5-2.png
.. |img-release-notes-3.5-3| image:: ../../_static/img/img-release-notes-3.5-3.png
.. |img-release-notes-3.5-4| image:: ../../_static/img/img-release-notes-3.5-4.png
.. |img-release-notes-3.5-5| image:: ../../_static/img/img-release-notes-3.5-5.png
