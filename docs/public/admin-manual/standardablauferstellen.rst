.. _label-standardablauf-admin:

Einen Standardablauf erstellen
==============================

Standardablauf generell
-----------------------
Wiederkehrende Aufgabenketten können unter *Vorlagen* hinterlegt werden. Diese
vordefinierten Aufgabenfolgen werden Standardabläufe genannt. Diese können nur
durch (Admin-)Benutzer, welche im Vorlagenbereich schreibberechtigt sind,
erstellt oder bearbeitet werden. Sie können aber durch alle Benutzer in den
jeweiligen Dossiers ausgelöst werden. Details zum Auslösen finden Sie daher in
der :ref:`Benutzerdokumentation <label-standardablauf-benutzer>`.

Standardablauf erstellen
------------------------
Dazu kann wie gewohnt unter *Vorlagen->Hinzufügen* einen neuen Standardablauf
erstellt werden.

|img-standardablauf-20|

In der allgemeinen Maske wird dem Standardablauf einen Titel gegeben sowie ein
kurzer, optionaler Beschrieb hinzugefügt.

Es wird zwischen parallelen und sequentiellen Standardabläufen unterschieden.
Parallel bedeutet in diesem Fall, dass mehrere Aufgaben gleichzeitig ausgelöst
werden. Sequentiell bedeutet, dass Aufgaben nacheinander ausgelöst werden.
Dabei gilt, dass die nächste Aufgabe erst ausgelöst wird, wenn die Aufgabe davor
abgeschlossen wurde. Der Benutzer kann im Dropdown wählen, welchen Ablauf er
benutzen möchte.

|img-standardablauf-30|

Danach können beliebig viele Aufgabenvorlagen hinzugefügt werden. Diese werden
via *Hinzufügen->Aufgabenvorlage* hinzugefügt.

|img-standardablauf-22|

Die Eingabemaske ist analog der :ref:`normale Aufgaben <label-aufgaben_erstellen>` auszufüllen.

|img-standardablauf-23|

Bei der Eingabe von Auftraggeber und Auftraggeber steht aber neben den
registrierten Benutzern und Eingangskörben der OneGov GEVER Installation auch
ein sogenannter *interaktiver Benutzer* zur Verfügung.

Wird in der Aufgabenvorlage für den Auftraggeber oder -nehmer der
*interaktive Benutzer* ausgewählt, muss nicht eine konkrete Person ausgewählt
werden, sondern eine *Rolle*. Als Rollen stehen die federführende Person
(*Federführender*) oder der zuständige *Sachbearbeiter* zur Auswahl.
Erst beim Auslösen des Standardablaufs in einem Dossier werden dann die Rollen
automatisch durch konkrete Benutzer ersetzt. Die federführende Person
entspricht dann dem Benutzer, der im entsprechenden Dossier die Federführung
inne hat. Der Sachbearbeiter entspricht dem Benutzer, der den Standardablauf
auslöst.

.. note::
   Interaktive und normale Benutzer können in einer Aufgabenvorlage
   kombiniert werden. Z.B. kann für den Auftraggeber der interaktive
   Benuter *Sachbearbeiter* und für den Auftragnehmer ein konkreter
   Benutzer hinterlegt werden.

Nachdem die Aufgabenvorlage gespeichert wurde, erscheint diese automatisch im
Standardablauf. Danach können beliebg viele weitere Aufgabenvorlagen erstellt
werden. Per Drag'n'Drop kann die Reihenfolge (primär relevant bei sequentiellen
Abläufen) verändert werden.

|img-standardablauf-24|
|img-standardablauf-25|

Ein Standardablauf muss nach Erfassung über *Aktionen->Aktivieren* aktiviert
werden, damit dieser dann in der Auswahl in einem Dossier resp. Subdossier
erscheint.

|img-standardablauf-31|


.. |img-standardablauf-20| image:: img/media/img-standardablauf-20.png
.. |img-standardablauf-22| image:: img/media/img-standardablauf-22.png
.. |img-standardablauf-23| image:: img/media/img-standardablauf-23.png
.. |img-standardablauf-24| image:: img/media/img-standardablauf-24.png
.. |img-standardablauf-25| image:: img/media/img-standardablauf-25.png
.. |img-standardablauf-30| image:: img/media/img-standardablauf-30.png
.. |img-standardablauf-31| image:: img/media/img-standardablauf-31.png

.. disqus::
