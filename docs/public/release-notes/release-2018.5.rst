OneGov GEVER Release 2018.5
===========================

Mit dem Release 2018.5 wurden die OGIPs 46 (Persönliche Aufgabe) sowie 27
(Aufsplittung Dokumentdatum) umgesetzt. Weiter steht ab diesem Release die
OneOffixx Schnittstelle für Dokumentvorlagen zur Verfügung. Neu kann auch in
einer Aufgabe eine Erinnerung gesetzt werden. Eine weitere Neuerung ist, dass
beim Abschluss eines Dossiers zur Vollständigkeit automatisch ein Aufgaben-PDF
abgelegt wird.

OGIP 46 – Persönliche Aufgaben
------------------------------
`OGIP 46  <https://my.teamraum.com/workspaces/onegov-gever-innovation-session/ogip?overlay=5d34894850db46fdae0d166ce94668e0#documents>`_ ermöglicht, dass bei einer Aufgabe die Stellvertreter-Berechtigungen für die Eingangskorb-Gruppe deaktiviert wird.
Diese Funktion kann z.B. bei Aufgaben mit personenbezogenen Daten hilfreich sein.
Mehr dazu können Sie :ref:`hier <label-stellvertretung>` nachlesen.


|img-stellvertretung-1|


OGIP 27 – Aufsplittung Dokumentdatum
------------------------------------
Mit dem `OGIP 27  <https://my.teamraum.com/workspaces/onegov-gever-innovation-session/ogip/ogip27-aufsplittung-dokumentdatum/file_view>`_ wurde ein Änderungsdatum bei Dokumenten und Mails eingeführt.
Damit erhält das Dokumentdatum seinen ursprünglichen Zweck zurück und wird
nicht mehr vom System automatisch verändert. Weiter wird der Dossierabschluss
vom Dokumentdatum entkoppelt und stattdessen das Änderungsdatum verwendet.
Weitere Informationen können Sie direkt im OGIP 27 oder in der Diskussion
im `Feedbackforum  <https://feedback.onegovgever.ch/t/sortieren-von-resultaten-nach-dokumentsdatum-ogip-27-aufsplittung-dokumentdatum/817/19>`_ nachlesen.


Aufgaben-PDF bei Dossier-Abschluss
----------------------------------
Mit diesem Release wird beim Abschluss eines Dossiers neu ein PDF mit allen im
Dossier bearbeiteten Aufgaben generiert und direkt im Dossier abgelegt. Das
Feature ist per default deaktiviert. Bei Interesse können wir dieses gerne
aktivieren. Nehmen Sie mit uns Kontakt auf. Mehr dazu können
Sie :ref:`hier <label-dossier-bearbeiten>` nachlesen.

|img-dossiers-103|

OneOffixx Schnittstelle
-----------------------

Neu bietet OneGov GEVER eine Schnittstelle zur Vorlagenmanagement Applikation
`OneOffixx <https://oneoffixx.com/>`_ unseres Partners Sevitec.

|img-release-notes-2018.5-1|


Erinnerung bei Aufgaben
-----------------------
Mit dem Release 2018.5 kann bei Aufgaben eine Erinnerungs-Funktion aktiviert
werden. Dadurch kann beispielsweise für den Morgen des Fälligkeitsdatums eine
Erinnerung (Benachrichtigung in OneGov GEVER oder per Mail) gesetzt werden.
Mehr dazu können Sie :ref:`hier <label-pendenzenkontrolle>` nachlesen.

|img-aufgaben-39|

Diverses
--------

-	Bei der Erstellung eines Teams können nur noch mandanteninterne Organisationseinheiten und Gruppen ausgewählt werden.

-	Alle Benachrichtigungsmails kommen nun in einem aufgefrischten, einheitlichen Design daher.

-	Docproperties werden neu automatisch aktualisiert, das Word-Makro wird somit überflüssig. Weiter besteht das neue Docproperty «external_reference».

-	Die Performance wurde verbessert, insbesondere beim Statuswechsel von Dossiers.

-	Im Aussonderungsmodul wird nun auch eine Benachrichtigungsfunktion mitsamt Konfigurationsoptionen bereitgestellt.

-	Das User-Interface wurde in einzelnen Bereichen optimiert.


Sitzungs- und Protokollverwaltung
---------------------------------

Zip-Export von Sitzung mit PDFs
-------------------------------
Neu kann von einer Sitzung ein Zip generiert werden, in welchem alle Dokumente
direkt als PDF eingefügt werden. Der Zip-Export der Originaldatei steht
selbstverständlich nach wie vor zur Verfügung.

Diverses
--------

- Mitgliedschaften eines Gremiums können neu nach Status der Mitgliedschaft gefiltert werden.

- Das Tab *Anträge* ist neu auch im Ordnungssystem sichtbar.

- Neu werden Anträge erst beschlossen, wenn der Protokollauszug ins Ursprungsdossier abgelegt wurde.

- Ad-Hoc Traktanden erhalten nicht mehr automatisch das Präfix *Traktandum*.

- Diverse Korrekturen und Optimierungen


.. |img-stellvertretung-1| image:: ../user-manual/img/media/img-stellvertretung-1.png
.. |img-dossiers-103| image:: ../user-manual/img/media/img-dossiers-103.png
.. |img-release-notes-2018.5-1| image:: ../_static/img/img-release-notes-2018.5-1.png
.. |img-aufgaben-39| image:: ../user-manual/img/media/img-aufgaben-39.png

.. disqus::
