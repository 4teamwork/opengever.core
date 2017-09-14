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

    # GEVER Demo: Dump content stats
    0 22 * * * /home/zope/server/01-gever.example.org/bin/dump-content-stats -s <plone_site_id> >/dev/null 2>&1
