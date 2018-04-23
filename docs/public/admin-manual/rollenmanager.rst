Der Rollenmanager
=================

Wozu dient der Rollenmanager?
-----------------------------

Die Zugriffsberechtigungen eines Mandanten sind auf Stufe
Ordnungsposition hinterlegt und werden auf die darunter liegenden
Dossiers vererbt.

Der Rollenmanager ist eine zusätzliche Rolle, die ausgewählten Benutzern
zugeteilt werden kann; es ist dazu kein separates Login notwendig.
Benutzern, die diese Rolle besitzen, ist es erlaubt, auf
Ordnungspositionen und Dossiers die Berechtigungen anzupassen, d.h.
einzuschränken oder zu erweitern. Auf Stufe Dokument gelten die
Berechtigungen, wie sie auf dem Dossier vergeben sind.

Beispiele:

1. Auf eine Ordnungsposition soll nebst der Leitung auch die Gruppe
   Sekretariat Einsicht nehmen können. Mit der Berechtigung
   Rollenmanager kann diese Erweiterung auf Stufe Ordnungsposition
   vorgenommen werden.

2. Unter einer Ordnungsposition befindet sich ein Dossier, das in
   Abweichung zur Regel nicht von allen Gruppen, die auf die übrigen
   Dossiers dieser Position Zugriff haben, eingesehen werden soll.
   Personen mit der Berechtigung Rollenmanager können die Zugriffsrechte
   für dieses Dossier einschränken.

.. note::
   Änderungen, die der Rollenmanager an den Berechtigungen vornimmt, werden
   im Journal protokolliert.

   Die Rolle "Rollenmanager" sollte nur Personen zugeteilt werden, die alle
   Dossiers eines Mandanten sehen dürfen. Der Grund ist, dass Personen mit
   dieser Rolle automatisch auf jene Dossiers oder Ordnungspositionen
   Zugriff erhalten, bei denen sie eine Änderung vornehmen.

   Es sollten immer Gruppen, nicht einzelne Personen auf Dossiers oder
   Ordnungspositionen berechtigt werden. Auf diese Weise ist bei einer
   personelle Mutation die Kontinuität gewährleistet.

Bedienung
---------

Änderung der Berechtigungen bei einem Dossier
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Öffnen Sie das gewünschte Dossier und klicken Sie auf *Aktionen →
   Freigabe*. Die Aktion *Freigabe* erscheint nur bei Personen mit der
   Berechtigung Rollenmanager.

   |img-rollenmanager-1|

-  Hierauf öffnet sich folgende Maske, aus der ersichtlich, ist, welche
   Gruppen in welcher Weise auf diesem Dossier berechtigt
   sind:

   |img-rollenmanager-2|

Berechtigungen einschränken
~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Soll bei einem Dossier die Berechtigung eingeschränkt werden,
   entfernen Sie das Häklein *Berechtigungen von übergeordneten Ordnern
   übernehmen* und speichern Sie. Dies hat zur Folge, dass die
   Berechtigungen für dieses Dossier nicht mehr von der übergeordneten
   Ordnungsposition geerbt werden, sondern spezifisch für dieses Dossier
   vergeben werden können.

   |img-rollenmanager-3|

-  Es wird nun nur noch diejenige Person angezeigt, die mithilfe des
   Rollenmanagers die Zugriffsberechtigungen bearbeitet (evtl.
   zusätzlich der Eingangskorb).

-  Geben Sie im Suchfeld das Kürzel Ihres Mandanten ein (im untenstehenden
   Beispiel generell gehalten mit "_benutzer"). Klicken Sie anschliessend auf
   "Suche". Es werden nun alle Gruppen ohne Berechtigungen angezeigt.

   |img-rollenmanager-4|

-  Klicken Sie bei den gewünschten Gruppen auf die Berechtigungen, die
   vergeben werden sollen. Mit dem Speichern werden die Änderungen
   übernommen. Die Person mit der Berechtigung Rollenmanager, welche die
   Änderungen vorgenommen hat, bleibt automatisch ebenfalls auf dem
   Dossier berechtigt. Zusätzlich werden die Änderungen im Dossier-Journal
   dokumentiert.

Berechtigungen erweitern
~~~~~~~~~~~~~~~~~~~~~~~~

-  Soll bei einem Dossier die Berechtigung erweitert werden,
   entfernen Sie das Häklein *Berechtigungen von übergeordneten Ordnern
   übernehmen* und speichern Sie. Dies hat zur Folge, dass die
   Berechtigungen für dieses Dossier nicht mehr von der übergeordneten
   Ordnungsposition geerbt werden, sondern spezifisch für dieses Dossier
   vergeben werden können.

   |img-rollenmanager-3|

-  Fügen Sie die gewünschten Berechtigungen hinzu und speichern Sie. Mit
   dem Speichern wird die Änderung der Zugriffsberechtigung übernommen.
   Die Person, welche die Änderung vorgenommen hat, bleibt automatisch
   ebenfalls auf dem Dossier berechtigt. Zusätzlich werden die Änderungen im
   Dossier-Journal dokumentiert.

Wiederherstellen von Berechtigungen auf Stufe Dossier
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Fügt man bei einem Dossier, bei dem man die Berechtigungen erweitert
oder eingeschränkt hat, das Häklein *Berechtigungen von übergeordneten
Ordnern übernehmen* wieder hinzu, werden wieder die Berechtigungen von
der übergeordneten Ordnungsposition geerbt. Die Person mit der
Berechtigung Rollenmanager wird dennoch angezeigt, da sie die Änderung
vorgenommen hat. Auch die Wiederherstellung der Vererbung wird im
Journal aufgezeichnet.

Änderung der Berechtigungen bei einer Ordnungsposition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Die Erweiterung und die Einschränkung der Berechtigungen bei einer
Ordnungsposition erfolgen gleich wie bei den Dossiers.

-  Klicken Sie auf der gewünschten Position auf *Aktionen → Freigabe*.

|img-rollenmanager-3|

-  Nun werden die Gruppen angezeigt, die auf dieser Position berechtigt
   sind. Das Häklein *Berechtigungen von übergeordneten Ordnern
   übernehmen* bezieht sich auf die übergeordnete Position.

|img-rollenmanager-4|

-  Um eine Einschränkung vorzunehmen, entfernen Sie das Häklein
   *Berechtigungen von übergeordneten Ordnern übernehmen*. Bei einer
   Erweiterung muss das Häklein nicht entfernt werden. Das weitere
   Vorgehen entspricht demjenigen bei der Bearbeitung von Berechtigungen
   bei Dossiers.

Rollenmodell
------------
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


Rollen innerhalb der Ordnungsstruktur
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Innerhalb der Ordnungsstruktur können Rechte zugewiesen werden für
-   Dossier lesen
-   Dossier hinzufügen
-   Dossier bearbeiten
-   Dossier abschliessen
-   Dossier reaktivieren

Diese Rechte werden jeweils AD-Gruppen zugewiesen. Damit werden faktisch
"Benutzergruppen" gebildet.

Best Practice ist, innerhalb der Organisation ein Gruppe von Personen
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

.. |img-rollenmanager-1| image:: img/media/img-rollenmanager-1.png
.. |img-rollenmanager-2| image:: img/media/img-rollenmanager-2.png
.. |img-rollenmanager-3| image:: img/media/img-rollenmanager-3.png
.. |img-rollenmanager-4| image:: img/media/img-rollenmanager-4.png

.. disqus::
