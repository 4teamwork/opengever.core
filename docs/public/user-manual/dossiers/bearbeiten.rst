.. _label-dossier-bearbeiten:

Ein Dossier bearbeiten
----------------------

Metadaten eines Dossiers bearbeiten
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Klickt man auf *Bearbeiten*, öffnet sich die Dossiermaske, und die
Eigenschaften (Metadaten des Dossiers) können bearbeitet werden.

Deckblatt oder Geschäftsdetails ausdrucken
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

|img-dossiers-12|

Über *Aktionen* kann das Deckblatt oder die Geschäftsdetails gedruckt
werden.

Dossier-Eigenschaften anzeigen
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Wählt man die Aktion *Eigenschaften anzeigen*, werden sämtliche
Metadaten des Dossiers angezeigt. Referenzierte Dossiers können von hier
aus direkt ausgewählt werden.

|img-dossiers-13|

.. _label-beteiligungen:

Einem Dossier Beteiligte hinzufügen
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In OneGov GEVER werden standardmässig vier Dossier-Rollen unterschieden.
Obligatorisch ist nur die Rolle „Federführung“. Weitere Rollen können
fakultativ zu Dokumentationszwecken vergeben werden.

+----------------------+--------------------------------------------------------------------------------------------------------------------------+
| **Dossier-Rolle**    | **Erläuterung**                                                                                                          |
+======================+==========================================================================================================================+
| *Federführung*       | Verantwortliche(r) SachbearbeiterIn, führt das Dossier, ist für die Vollständigkeit des Dossierinhalts verantwortlich.   |
+----------------------+--------------------------------------------------------------------------------------------------------------------------+
| *Mitwirkung*         | Interne oder externe Beteiligte, die an der Durchführung des Geschäfts aktiv beteiligt sind.                             |
+----------------------+--------------------------------------------------------------------------------------------------------------------------+
| *Schlusszeichnung*   | Besondere Form der Mitwirkung.                                                                                           |
+----------------------+--------------------------------------------------------------------------------------------------------------------------+
| *Kenntnisnahme*      | Keine aktive Beteiligung am Geschäft, erhaltene Dokumente dienen lediglich der Information.                              |
+----------------------+--------------------------------------------------------------------------------------------------------------------------+

.. note::
   - Federführend ist immer eine Person aus dem eigenen Mandanten
   - Weitere Beteiligte können aus demselben oder aus einem anderen Mandanten
     stammen. Externe Beteiligte können ebenfalls ausgewählt werden,
     vorausgesetzt sie sind unter dem Anwendungsbereich Kontakt erfasst.
   - Eine Beteiligung hat keine zusätzlichen *Zugriffsrechte* auf das Dossier
     zur Folge.

Während die :term:`Federführung` direkt in der Eingabemaske des Dossiers
eingegeben wird, werden die übrigen Beteiligungen über *Hinzufügen →
Beteiligung hinzufügen* oder über den Dossier-Reiter *Beteiligungen*
ergänzt.

|img-dossiers-14|

Zunächst wird die gewünschte Person ausgewählt und ihr danach die entsprechende
Rolle zugewiesen. Die Beteiligung wird schliesslich mit *Erstellen* erstellt.

|img-dossiers-15|

Ein Dossier abschliessen und ablegen
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Die Möglichkeit, Dossiers abzuschliessen ist je nach Konfiguration allen
Benutzern zugänglich oder aber nur für
speziell berechtigte Sachbearbeiter/innen. Ansonsten erscheint
diese Aktion nicht.

Wählen Sie die Aktion *Abschliessen*:

|img-dossiers-16|

Darauf erscheint folgendes Formular:

1. **Ablage-Präfix:** Im Pulldownmenü kann eine Ablage ausgewählt
   werden, z.B. Amt, Leitung, Direktionssekretariat, Regierungsrat.

2. **Ende:** OneGov GEVER schlägt als Ende-Datum das Datum des jüngsten
   Dokuments im Dossier vor (sofern Dokumente im Dossier vorhanden
   sind). Dieses Datum kann mit dem Kalender angepasst werden. (Das
   Ende-Datum kann auch direkt im Geschäftsdossier über Bearbeiten
   eingetragen werden.)

3. **Ablage-Jahr:** Das Ablage-Jahr entspricht dem Jahr, in dem das
   jüngste Dokument des Dossiers erstellt wurde. OneGov GEVER schlägt
   das Ablagejahr automatisch vor, sofern im Dossier Dokumente vorhanden
   sind; ansonsten muss es manuell eingetragen werden.

4. **Aktion:** Beim Abschliessen kann zwischen zwei Aktionen gewählt
   werden:

   -  Abschliessen und Ablagenummer vergeben: Beim Speichern wird das
      Dossier in den Status Abgeschlossen gesetzt und die Ablagenummer
      automatisch vergeben. Pro Ablage wird eine eigene Nummernserie
      geführt.

      *Aufbau der Ablagenummer:*

      Mandantenbezeichnung (1), Ablage (2), Ablagejahr (3), Laufnummer (4)

   -  Nur abschliessen (keine Ablagenummer vergeben): Das Dossier wird in
      den Status Abgeschlossen gesetzt, ohne dass eine Ablagenummer
      vergeben wird.

Mit dem Speichern werden die Informationen in der Byline angepasst:

Regeln für den Abschluss eines Dossiers:

- Abschluss eines elektronischen Dossiers, wenn kein physisches Dossier
  vorhanden ist:

  1. Aktion "Abschliessen" wählen

  2. Feld Ablage:
     Direktionssekretariate: Ablage Direktionssekretariat oder
     Regierungsrat setzen (Ablagejahr stehen lassen). Die Vergabe der
     Ablage ist notwendig, damit man unterscheiden kann, ob es sich um
     ein Regierungsrats- oder ein Direktionsgeschäft handelt.

     Amtsstellen: Ablage ausfüllen, wenn zur Unterscheidung der
     Geschäftsart sinnvoll.

  3. Ablagejahr stehen lassen

  4. Keine Ablagenummer vergeben (Aktion "Nur abschliessen, keine
     Ablagenummer vergeben")

- Abschluss eines elektronischen Dossiers, wenn ergänzend oder
  massgebend ein physisches Dossier vorhanden ist:

  1. Aktion "Abschliessen" wählen

  2. Ablage und Ablagenummer vergeben, Vergabe des Ablagejahres bestätigen
     bzw. korrigieren

  3. Physisches Dossier entsprechend ablegen


Ein Dossier wieder eröffnen und wieder ablegen
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dossiers wieder eröffnen können (je nach Konfiguration) nur Personen mit
Sekretariatsrechten bzw. Sachbearbeiter/innen mit entsprechender Berechtigung.
Um ein Dossier wieder zu reaktivieren, wählen Sie *Aktionen → Wieder öffnen*.
Dadurch wird der Status wieder *In Bearbeitung* gesetzt, und das Dossier
kann weiterbearbeitet werden.

Nehmen Sie die gewünschten Änderungen im Dossier vor und wählen Sie
*Aktionen → Abschliessen*.

Falls sich das Ablagejahr nicht verändert hat, wählen Sie *Abschliessen
und die existierende Ablagenummer verwenden*. Andernfalls wählen Sie
*Abschliessen und Ablagenummer neu vergeben*. Einmal gelöschte
Ablagenummern stehen nicht mehr zur Verfügung.

Ein Dossier stornieren
~~~~~~~~~~~~~~~~~~~~~~

Wurde ein Dossier versehentlich eröffnet, kann es mit *Aktionen →
Stornieren* storniert werden. Stornierte Dossiers können nicht mehr
bearbeitet werden. Personen mit Sekretariatsrechten bzw.
Sachbearbeiter/innen mit entsprechender Berechtigung können (je nach
Konfiguration) stornierte Dossiers wieder aktivieren (*Aktionen → Aktivieren*).

Wer hat Zugriff auf das Dossier – der Reiter „Info“
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Unter dem Reiter *Info* ist ersichtlich, welche Gruppen auf das Dossier
Zugriff haben.

Klickt man auf eine Gruppe, werden die Mitglieder angezeigt.

Die Berechtigungen werden auf Stufe Ordnungsposition vergeben und von
dort auf die korrespondierenden Dossiers vererbt.

|img-dossiers-17|

Wer hat wann, was gemacht – der Reiter „Journal“
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Unter dem Reiter *Journal* wird angezeigt, wer wann welche Veränderungen
am Dossier vorgenommen hat. Das Journal dient der :term:`Nachvollziehbarkeit`.
Es kann nicht bearbeitet werden.

|img-dossiers-18|

ZIP-Export
~~~~~~~~~~

Ein komplettes Dossier kann als ZIP-Datei verpackt und heruntergeladen werden.

1. Navigieren Sie in das Dossier, welches Sie exportieren wollen.

2. Öffnen Sie das "Aktionen" Menü und klicken auf "Als ZIP-Datei
   exportieren"

3. Wählen Sie den Speicherort für die ZIP-Datei aus.

.. note::

   Es besteht ebenfalls die Möglichkeit, eine Auswahl von Dokumenten als
   ZIP-Datei zu exportieren. Die Anleitung hierzu finden Sie unter
   :ref:`label-dokumente-zip-export`.

.. |img-dossiers-12| image:: ../img/media/img-dossiers-12.png
.. |img-dossiers-13| image:: ../img/media/img-dossiers-13.png
.. |img-dossiers-14| image:: ../img/media/img-dossiers-14.png
.. |img-dossiers-15| image:: ../img/media/img-dossiers-15.png
.. |img-dossiers-16| image:: ../img/media/img-dossiers-16.png
.. |img-dossiers-17| image:: ../img/media/img-dossiers-17.png
.. |img-dossiers-18| image:: ../img/media/img-dossiers-18.png

.. disqus::
