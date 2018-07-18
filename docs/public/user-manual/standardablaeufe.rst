.. _label-standardablauf-benutzer:
.. _kapitel-standardablaeufe:

Mit Standardabläufen arbeiten
=============================

Was ist ein Standardablauf
--------------------------

Wiederkehrende Aufgabenketten (z.B. vorgegebene Projektschritte) können
in OneGov GEVER unter der Anwendungskomponente Vorlagen hinterlegt
werden. Diese vordefinierten Aufgabenketten bzw. Aufgabenfolgen werden
Standardabläufe genannt.

Standardabläufe können normalerweise (je nach Berechtigungen) durch Personen mit
Administrator-Rolle definiert werden. Daher wird die Erstellung von Standardabläufen in der :ref:`Admin-Dokumentation <label-standardablauf-admin>` behandelt.

|img-standardablauf-1|

Klickt man auf einen Standardablauf unter *Vorlagen*, werden die einzelnen
Aufgaben und deren Details angezeigt:

a) Titel der Aufgabe

b) Auftragstyp

c) Auftraggeber

d) Auftragnehmer

e) Frist in Tagen ab Auslösung der Aufgabe

f) Vorselektion: Angabe, ob die Aufgabe automatisch ausgewählt werden
   soll, wenn man den Standardablauf in einem Dossier auslöst.

|img-standardablauf-2|

Parallele und sequentielle Abläufe
-----------------------------------
Es wird zwischen parallelen und sequentiellen Standardabläufen unterschieden.
Parallel bedeutet in diesem Fall, dass mehrere Aufgaben gleichzeitig ausgelöst
werden. Sequentiell bedeutet, dass Aufgaben nacheinander ausgelöst werden. Dabei
gilt, dass die nächste Aufgabe erst ausgelöst wird, wenn die Aufgabe davor
abgeschlossen wurde.

Der Ersteller der Standardablauf-Vorlage kann zu Beginn eines neuen
Standardablaufs wählen, welche Ablaufart er möchte. Der Benutzer, welcher die
Standardablauf-Vorlage dann in einem Dossier einsetzt, übernimmt diese Ablaufart
automatisch. Auf die Unterschiede der beiden Ablauf-Typen wird weiter unten
noch genauer eingegangen.

Einen Standardablauf auslösen
-----------------------------

Wählen Sie innerhalb eines Dossiers oder Subdossiers
*Hinzufügen → Standardablauf auslösen*.

|img-standardablauf-32|

Wählen Sie den gewünschten Standardablauf aus und klicken Sie
*Weiter*.

|img-standardablauf-33|

Die in der Vorlage mit *Vorselektiert* bezeichneten Aufgaben sind
bereits ausgewählt. Mit der gedrückten :kbd:`Ctrl` können weitere
Aufgaben hinzu- oder weggeklickt werden.

|img-standardablauf-34|

Falls noch nicht vorhanden, muss in diesem Schritt zwingend
für jede Aufgabe einen Auftragnehmer (Team oder Person) erfasst werden.

|img-standardablauf-35|

Mit *Speichern* werden die ausgewählten Aufgaben ins Dossier übernommen.
Nun stehen die Aufgaben wie gewohnt zur weiteren Bearbeitung bereit (siehe
:ref:`kapitel-aufgaben`). Ab hier werden auch die Unterschiede von einem
parallelen zu sequentiellen Ablauf vorallem beim Status und der Frist deutlich.

**Status**

Beim Auslösen eines parallelen Standardablaufs wird eine Hauptaufgabe mit
mehreren Unteraufgaben erstellt. Auf der Hauptaufgabe ist ersichtlich, dass es
sich um einen parallelen Standardablauf handelt. Wird ein paralleler
Standardablauf ausgelöst, so werden alle Aufgaben automatisch in den Status
"Offen" versetzt und somit gleichzeitig ausgelöst.

Beim Auslösen eines sequentiellen Standardablaufs wird auch eine Hauptaufgabe
mit mehreren Unteraufgaben erstellt. Auf der Hauptaufgabe ist ersichtlich, dass
es sich um einen sequenziellen Standardablauf handelt. Wird ein sequenzieller
Standardablauf ausgelöst, so wird die erste Aufgabe im Ablauf automatisch
geöffnet, alle weiteren werden im Zustand «Geplant» initialisiert, sind aber zu
diesem Zeitpunkt noch nicht sichtbar. Wird eine Aufgabe erledigt, so wird die
nächste Aufgabe im Ablauf automatisch geöffnet resp. in den Status "Offen"
versetzt und somit sichtbar.

**Frist**

Bei einem parallelen Ablauf wird die Frist der Hauptaufgabe aus dem spätesten
Termin der Unteraufgaben plus 10 Tage gesetzt.

Bei einem sequentiellen Ablauf wird die Frist der ersten Aufgabe plus 10 Tage ab
Auslöse-Datum gesetzt. Wird diese geschlossen und die nächste Aufgabe so
automatisch ausgelöst, erhält auch diese eine Frist plus 10 Tagen ab dem
Abschluss der vorherigen Aufgabe.

|img-standardablauf-36|

Zu beachten bei sequentiellen Aufgaben
--------------------------------------

-   Wird eine Aufgabe abgelehnt, wird sie dem Auftraggeber zugewiesen. Dieser
    hat die Möglichkeit, die Aufgabe wieder zu öffnen (und dann «Neu zuweisen»,
    «Abschliessen»). Bei sequentiellen Aufgaben hat er aber zudem auch die
    Möglichkeit, die Aufgabe zu «überspringen» oder den «Ablauf abbrechen».

|img-standardablauf-38|

-   Auf der Ansicht der Hauptaufgabe eines sequenziellen Standardablaufs kann in
    der Auflistung der Teilaufgaben direkt eine neue Aufgabe eingefügt werden.
    Der Standardablauf kann also individuell ergänzt werden. Das anschliessend
    geöffnete Hinzufügen-Formular der Aufgabe verhält sich wie das :ref:`normale Aufgaben-Formular <label-aufgaben_erstellen>` und klinkt sich automatisch in den Standardablauf ein.

|img-standardablauf-37|

.. |img-standardablauf-1| image:: img/media/img-standardablauf-1.png
.. |img-standardablauf-2| image:: img/media/img-standardablauf-2.png
.. |img-standardablauf-32| image:: img/media/img-standardablauf-32.png
.. |img-standardablauf-33| image:: img/media/img-standardablauf-33.png
.. |img-standardablauf-34| image:: img/media/img-standardablauf-34.png
.. |img-standardablauf-35| image:: img/media/img-standardablauf-35.png
.. |img-standardablauf-36| image:: img/media/img-standardablauf-36.png
.. |img-standardablauf-37| image:: img/media/img-standardablauf-37.png
.. |img-standardablauf-38| image:: img/media/img-standardablauf-38.png

.. disqus::
