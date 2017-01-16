Aktivierung Bumblebee
=====================

Vorgehen Aktivierung Bumblebee
------------------------------

Nachfolgend die nötigen Schritte zur Aktivierung von Bumblebee bei einem Mandanten, der schon vor dem Release 3.9 aufgesetzt wurde. Falls bei einem ab Release 3.9 (oder grösser) aufgesetzen Mandanten Bumblebee aktiviert wird sind die Schritte 3. bis 5. nicht nötig.

1. Bumblebee-Konfiguration: sicherstellen, dass die notwendigen Umbegungsvariablen gesetzt sind, siehe auch `ftw.bumblebee <https://github.com/4teamwork/ftw.bumblebee>`_::

    [instance0]
    environment-vars +=
        BUMBLEBEE_APP_ID gever_demo
        BUMBLEBEE_INTERNAL_PLONE_URL https://demo.onegovgever.ch
        BUMBLEBEE_PUBLIC_URL https://demo.onegovgever.ch
        BUMBLEBEE_SECRET [the secret]

2. Sicherstellen, dass `bumblebee.cfg` im `extends` ist::

    extends =
        [...]
        https://raw.githubusercontent.com/4teamwork/ftw-buildouts/master/bumblebee.cfg

3. Falls noch nötig OneGovGEVER Release 3.9 installieren und Upgrade-Steps ausführen. Sicherstellen, dass `opengever.maintenance` aktuell ist.

4. Die `bumblebee_checksum` für alle Dokumente berechnen, dies reindiziert auch `object_provides`. Das Skript kann nicht mit Konflikten umgehen, die Site daher falls möglich offline nehmen::

    bin/instance0 run src/opengever.maintenance/opengever/maintenance/scripts/bumblebee_installation.py -m reindex

5. Die `bumblebee_checksum` für archvierte Dokumente berechnen. Das Skript kann nicht mit Konflikten umgehen, die Site daher falls möglich offline nehmen::

    bin/instance0 run src/opengever.maintenance/opengever/maintenance/scripts/bumblebee_installation.py -m history

6. Bumblebee in der Registry aktivieren (kann auch Through-the-web konfiguriert werden)::

    bin/instance0 run src/opengever.maintenance/opengever/maintenance/scripts/bumblebee_installation.py -m activate

7. Alle Dokumente in Bumblebee ablegen. Das Skript kann mit Konflikten umgehen und kann daher währen dem produktiven Betrieb ausgeführt werden. Für Dokumente, welche noch nicht in der Bumblebee App registriert sind, wird ein Platzhalter dargestellt::

    bin/instance0 run src/opengever.maintenance/opengever/maintenance/scripts/bumblebee_installation.py -m store


Abschätzung benötigte Zeit
--------------------------

Die benötigte Zeit für das Update kann gemäss Erfahrungswert linear approximiert werden:


  - ``4:`` 124 Sekunden für 1243 Dokumente
  - ``5:`` 207 Sekunden für 1243 Dokumente
  - ``7:`` 234 Sekunden fur 1243 Dokumente

.. disqus::