Allgemein
=========

Allgemeine Informationen zum Deployment und Betrieb von GEVER-Installationen,
die sowohl für SaaS wie auch On-Premise Installationen gelten.

Cron-Jobs
---------

Für produktive GEVER-Installationen müssen folgende Cron-Jobs eingerichtet
werden:


OGDS-Synchronisierung
^^^^^^^^^^^^^^^^^^^^^

Standardmässig konfigurieren wir die OGDS-Synchronisierung so, dass sie drei
mal täglich durchgeführt wird:

.. code:: bash

    # GEVER Demo: OGDS sync
    0 4 * * * /home/zope/server/01-gever.example.org/bin/instance0 sync_ogds >/dev/null 2>&1
    0 12 * * * /home/zope/server/01-gever.example.org/bin/instance0 sync_ogds >/dev/null 2>&1
    0 18 * * * /home/zope/server/01-gever.example.org/bin/instance0 sync_ogds >/dev/null 2>&1

**Hinweis:** Pro Verbund (Gruppe von Mandanten mit gemeinsamem OGDS) sollte
die OGDS-Synchronisierung nur einmal durchgeführt werden! Die Konvention ist,
diese jeweils auf dem ersten Mandanten / Deployment des Verbunds durchzuführen.


Inhaltsstatistiken (ftw.contentstats)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Die Inhaltsstatistiken werden einmal pro Tag mittels dem
``bin/dump-content-stats`` Script in ein Logfile gedumpt.

**Wichtig:** Dem Script muss die ID der Plone-Site angegeben werden!

.. code:: bash

    # Dump content stats
    0 22 * * * /home/zope/server/01-gever.example.org/bin/dump-content-stats -s <plone_site_id> >/dev/null 2>&1


Daily Digest
^^^^^^^^^^^^

Die Daily Digest mails können via zopectl handler `send_digest` generiert und versandt werden. Da sie automatisch alle Benachrichtigungen der letzen 24h behandelt, sollte auch der Cronjob so eingericht werden das er alle 24h ausgeführt wird.

.. code:: bash

    # GEVER Demo: Send daily digest
    0 5 * * * /home/zope/server/01-gever.example.org/bin/instance0 send_digest >/dev/null 2>&1


**Hinweise:** Pro Verbund (Gruppe von Mandanten mit gemeinsamem OGDS) darf
der Daily Digest nur einmal durchgeführt werden! Es ist zu empfehlen die gleiche Konvention wie bei der OGDS Synchronisierung zu verwenden, also jeweils auf dem ersten Mandanten / Deployment des Verbunds durchführen.


Aufgaben-Erinnerungen erstellen
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Aufgaben-Erinnerungen können via zopectl handler `generate_remind_notifications` generiert werden.
Es werden nur Erinnerungen für den aktuellen Tag erstellt. Der Cronjob sollte somit so früh wie möglich an einem neuen Tag ausgeführt werden und in jedem Fall **vor** dem "Daily Digest"-Job.

.. code:: bash

    # Generate remind notifications
    0 4 * * * /home/zope/server/01-gever.example.org/bin/instance0 generate_remind_notifications >/dev/null 2>&1


**Hinweise:** Pro Verbund (Gruppe von Mandanten mit gemeinsamem OGDS) darf
der Job "Aufgaben-Erinnerungen erstellen" nur einmal durchgeführt werden! Es ist zu empfehlen die gleiche Konvention wie bei der OGDS Synchronisierung zu verwenden, also jeweils auf dem ersten Mandanten / Deployment des Verbunds durchführen.


Benachrichtigung für überfällige Dossiers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Ein überfälliges Dossier ist ein Dossier im Status offen, welches das End-Datum überschritten hat.

Benachrichtigungen für überfällige Dossiers können über den zopectl handler `generate_overdue_notifications` generiert werden. Dabei wird für jedes überfällige Dossier eine Benachrichtigung an die federführende Person versendet.

Der Cronjob sollte somit in jedem Fall **vor** dem "Daily Digest"-Job ausgeführt werden.

.. code:: bash

    # Generate notifications for overdue dossiers
    30 4 * * * /home/zope/server/01-gever.example.org/bin/instance0 generate_overdue_notifications >/dev/null 2>&1

**Hinweise:** Der Job "Benachrichtigung für überfällige Dossiers" muss **für jeden Mandanten** eines Clusters einzeln ausgeführt und eingerichtet werden.
