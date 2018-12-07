Aktivierung SOLR
================

Folgend eine kurze Beschreibung wie bei einem bestehenden GEVER Deployment die SOLR Suche aktiviert werden kann.

Voraussetzungen
---------------
Voraussetzung ist im Minimum die GEVER Version 2018.1, es wird aber empfohlen die Version 2018.4 oder neuer einzusetzen.

Buildout
--------
Die folgenden Anpassungen müssen im Kunden Buildout vorgenommen.


1. ``solr.cfg`` in die Buildout extends aufnehmen (vor dem production-v2.cfg)::

    [buildout]
    extends =
        ...
        https://raw.githubusercontent.com/4teamwork/gever-buildouts/master/solr.cfg
        ...

2. ``solr-core-name`` definieren. Wir verwenden hierzu die Policy-Bezeichnung, also z.B. ``edk``::

    [buildout]
    ...

    solr-core-name = edk

3. Solr Version definieren, sofern diese nicht bereits via opengever.core's ``versions.cfg`` definiert wurde::

    [solr]
    url = http://archive.apache.org/dist/lucene/solr/7.3.1/solr-7.3.1.tgz
    md5sum = 042a6c0d579375be1a8886428f13755f


Policy Anpassung
----------------
Obwohl das für die Solr Aktivierung eingesetzte Script, dass Feature-Flag automatisch setzt, soll der Konfigurationswechsel in der Policy (z.B. ``opengever.demo/opengever/demo/profiles/default/registry.xml``) festgehalten werden. Ein Upgradestep ist aber nicht notwendig::

  <records interface="opengever.base.interfaces.ISearchSettings">
    <value key="use_solr">True</value>
  </records>


Deployment
----------
Nach erfolgreich durchgeführtem Buildout und Neustart des Supervisors, sollte nun auch der solr im supervisor aufgenommen und automatisch gestartet werden::

  $ bin/supervisorctl
  ...
  instance1                        RUNNING   pid 6014, uptime 2 days, 18:32:40
  instance2                        RUNNING   pid 5918, uptime 2 days, 18:33:41
  solr                             RUNNING   pid 5556, uptime 2 days, 18:37:01
  ...


Aktivierung
-----------
Die Aktivierung von Solr soll in zwei Schritten erfolgen, zuerst indexieren wir alle Daten mittels dem ``solr-maintenance`` Script::

  sudo -u zope bin/instance0 run src/opengever.maintenance/opengever/maintenance/scripts/solr_maintenance.py reindex


Anschliessend kann die eigentliche Aktivierung gestartet werden. Hierfür steht im ``opengever.maintenance`` das Script ``activate_solr.py`` zur Verfügung.
Neben der Aktiverung, also dem Setzen des Feature Flags, wird auch ein Diff berechnet und neu indexiert. Zudem werden die nicht mehr benötigten Indexes aus dem ``Portal Catalog`` entfernt. Diese zusätzlichen Schritte können mittels separten Optionen (``--keep-indexes`` und ``--no-indexing``) übersprungen werden, standardmässig sollte dies aber nicht nötig sein::

  sudo -u zope bin/instance0 run src/opengever.maintenance/opengever/maintenance/scripts/activate_solr.py


Abschluss
---------
Sofern die Umstellung erfolgreich war und die Suche wie gewünscht funktioniert, muss noch die Dependency auf ``ftw.tika`` im ``setup.py`` der Policy, sowie das ``tika-standalone.cfg`` aus den Buildout extends entfernt werden.
