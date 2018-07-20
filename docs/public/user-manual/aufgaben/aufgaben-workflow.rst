.. _label-aufgaben-workflow:

Übersicht über den typischen Aufgabenworkflow
---------------------------------------------

Nach dem Speichern ist eine Aufgabe im Status *Offen*.

**Typische Reihenfolge der Aufgabenerledigung**

-   Auftragsgeber erstellt eine Aufgabe: Status Offen

-   Auftragnehmer akzeptiert die Aufgabe: Status In Arbeit

-   Auftragnehmer erledigt die Aufgabe: Status Erledigt

-   Auftraggeber schliesst die Aufgabe ab: Status Abgeschlossen


.. note::
   Bei den Auftragstypen "Zur Kenntnisnahme" sowie "Zur direkten Erledigung"
   ist der Workflow abgekürzt, da der Auftraggeber in diesen Fällen keine
   Antwort erwartet, die überprüft werden muss.

   - "Zur Kenntnisnahme": Diese Aufgabe kann ohne Akzeptieren direkt
     abgeschlossen werden.

   - "Zur direkten Erledigung": Diese Aufgabe kann nach dem Akzeptieren direkt
     abgeschlossen werden.

   Mitarbeitende, die Zugriff auf den Eingangskorb haben, können zusätzliche
   Aufgabenaktionen auslösen, auch wenn sie nicht Auftragnehmer sind.

**Spezialfälle**

-   Auftragnehmer lehnt eine Aufgabe ab. Die Aufgabe wird automatisch dem Auftraggeber zurück zugewiesen: Status *Abgelehnt*

-   Auftraggeber storniert/bricht eine Aufgabe ab: Status *Abgebrochen*

-   Auftragsgeber öffnet eine Aufgabe nochmals, nachdem sie bereits
    erledigt war oder zurückgewiesen worden ist: Status *Offen*

-   Auftraggeber weist Aufgabe neuer Person zu: Status *Offen*

**Sequentieller Aufgabenablauf**

Wird ein Standardablauf mit sequentiellen Ablauftyp ausgelöst, kommen noch die
Status *Geplant* und *Übersprungen* dazu. Wird ein solcher Standardablauf
ausgelöst, werden die Aufgaben nacheinander ausgelöst. Das bedeutet, dass sich
die nächste Aufagbe erst aktiviert, wenn jene davor abgeschlossen wurde. Die
erste Aufgabe wird dadurch automatisch in den Status *Offen* gesetzt. Alle
weiteren, nachfolgenden Aufgabe erhalten den Status *Geplant* bis diese dann an
der Reihe sind. Solche Aufgaben können auch *Übersprungen* werden und erhalten
entsprechend auch diesen Status.

**Berechtigung bei den verschiedenen Auftragstypen**

Die nachfolgend über Aufgaben definierten Rechte an Dokumenten ergänzen die
bestehenden Berechtigungen auf Stufe Ordnungsposition und Dossier während
der Dauer einer Aufgabe. Sobald die Aufgabe abgeschlossen wird, werden auch
diese Rechte dem Auftragnehmer wieder entzogen.

======================== =================
Auftragstyp               Auftragnehmende
                          Person ist
                          berechtigt
======================== =================
Zur Kenntnisnahme         zu lesen

Zur direkten Erledigung   zu lesen

Zum Bericht/Antrag        zu überarbeiten


Zur Genehmigung           zu überarbeiten


Zur Prüfung/Korrektur     zu überarbeiten


Zur Stellungnahme         zu überarbeiten

======================== =================

Mit der auftragnehmenden Person wird auch die Eingangskorbgruppe des
auftragnehmenden Mandanten mitberechtigt. Dies im Sinne der
Stellvertreter-Regelung.

**Aufgaben-Workflow-Diagramm**

Nachstehend ist das Zusammenspiel aller Status bei Aufgaben grafisch
dargestellt.

|img-aufgaben-workflow-1|

.. |img-aufgaben-workflow-1| image:: ../img/media/img-aufgaben-workflow-1.png

.. disqus::
