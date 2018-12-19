Rollenmodell
============

Nachstehend werden die in OneGov GEVER enthaltenen Rollen erläutert.

Globale Rollen
~~~~~~~~~~~~~~
Globale Rollen gelten für einen physischen Mandanten. Die Rolle wird durch
4teamwork im System konfiguriert. Jeder Rolle wird einer AD-Gruppe zugewiesen.

Die Globalen Rollen und deren Charakteristik sind

-   Administrator: Sieht alle Dossiers, kann auf OS und Dossiers Rechte
    einrichten, kann Ordnungssystem anpassen/ergänzen, kann Vorlagen verwalten,
    kann :ref:`label-force-checkin` ausführen.

-   Rollenmanager: Darf in denjenigen Dossiers Rechte vergeben (einschränken
    oder erweitern), auf welche er mindestens lesend berechtigt ist.

-   Records Manager: Diese Rolle wird in der Regel einem kleinen Benutzerkreis,
    welche für die Aussonderung des entsprechenden Mandants zuständig sind,
    vergeben. Die Rolle erlaubt es Aussonderungsangebote zu erstellen. Die Rolle
    Records Managerer teilt keine zusätzlichen Rechte auf Dossiers, es können
    demnach nur Dossiers für Angebote selektiert werden, welche vom Benutzer
    eingesehen werden dürfen.

-   Archivist: Die Rolle Archivist wird in der Regel Archiv-Mitarbeitenden
    vergeben, welche dazu berechtigt sind Angebote des Records Managers zu
    bewerten und diese ins Langzeitarchiv zu überführen. Benutzer mit der Rolle
    Archivist können alle angebotenen und archivierten Dossiers sehen, auch wenn
    Sie nicht dem entsprechenden Mandanten zugewiesen sind. Dies ermöglicht eine
    Prüfung der Dossiers durch die Archiv-Mitarbeitenden während der
    Bewertungsphase. Dies ist somit die Rolle für die Archivierung von Dossiers
    sowie zur Bewertung eines Aussonderungsangebots.

-   Sonderrolle Eingangskorb pro physischen und/oder virtuellen Mandanten: Die
    Rolle wird von 4teamwork konfiguriert. Sie dient auch as unpersönlicher
    Empfänger pro physischen und virtuellen Mandanten bei Aufgaben. Personen in
    dieser Rollen können einen Posteingang erfassen, Dokumente weiterleiten,
    Unpersönliche Aufgaben an Eingangskorb verwalten sowie sind diese
    Stellvertretung bei Aufgaben. Zudem sind sie automatisch für alle Aufgaben
    an den Mandanten mitberechtigt.

Grundsätzlich gilt, dass die Globalen Rollen Rollenmanager und Recordsmanager
ein Grundrecht erteilen, jedoch keine Sichtrechte auf Dossiers per se.

Weiter gilt, dass die Rollen Rollenmanager und Recordsmanager nur in denjenigen
Dossiers wahrgenommen werden können, in welchen die Person durch andere
Berechtigungen über mindestens Sichtrechte verfügen.


Rechte innerhalb der Ordnungsstruktur
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Innerhalb der Ordnungsstruktur können Rechte zugewiesen werden für
-   Dossier lesen
-   Dossier hinzufügen
-   Dossier bearbeiten
-   Dossier abschliessen
-   Dossier reaktivieren

Diese Rechte werden jeweils AD-Gruppen zugewiesen. Damit werden faktisch
"Benutzergruppen" gebildet.

Best Practice ist, innerhalb der Organisation eine Gruppe von Personen
(Benutzergruppe) zu bilden die jeweils alle obgenannten Rechte exkl.
"reaktivieren" besitzt. Dabei handelt es sich um generell formuliert
"Sachbearbeitende".

Das Recht "reaktivieren" von Dossiers wird in der Regel einer separaten Gruppe
zugewiesen, da das Reaktivieren Einfluss auf die Rückbehaltungsperiode hat.
Dieses Recht wird in der Regel nur GEVER-Verantwortlichen innerhalb der
jeweiligen Organisation oder alternativ der Rolle Administrator übertragen.

Entsprechende Rollen (Best Practice) sind:

-   Sachbearbeitende: Zuweisung der Benutzer zu Mandant(en) Rechte für lesen, hinzufügen, bearbeiten und abschliessen von Dossiers

-   GEVER-Verantwortliche: Zuweisung der Benutzer zu Mandant(en). Alle Rechte (lesen, hinzufügen, bearbeiten, abschliessen, reaktivieren von Dossiers)

Anschauen der Rechte auf Dossierstufe
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Im Dossier Info-Tab sowie unter Aktionen --> Freigabe findet sich eine Übersicht
über die Rollen und deren Rechte pro Dossier.  Der Tool-Tipp mit einem blauen
„?“ gibt bei Klick darauf Auskunft, warum der Benutzende resp. die Gruppe eine
Berechtigung erhalten hat. Nebst initialer Berechtigung via LDAP oder manueller
Anpassung, besteht auch die Möglichkeit, dass für die Dauer einer Aufgabe,
eine Berechtigung erteilt werden kann. Mehr dazu können Sie unter :ref:`label-aufgaben-workflow` lesen.

|img-rollenmodell-1|

.. |img-rollenmodell-1| image:: img/media/img-rollenmodell-1.png


.. disqus::
