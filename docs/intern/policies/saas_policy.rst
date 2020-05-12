.. _saas-policy:

Erstellen einer SaaS Policy
===========================

*Für das Erstellen der Policy gibt es im Jira ein* `Issue-Template <https://4teamwork.atlassian.net/browse/TEMP-7>`_.

Vorbereitung
------------
Zum Erstellen einer neuen Policy benötigen wir diverse Informationen vom Kunden. Diese Informationen müssen vom PO organisiert werden. Folgende Dokumente müssen uns ausgefüllt zur Verfügung stehen:

- `Vorlage Checkliste <https://gever.4teamwork.ch/vorlagen/opengever-dossier-templatefolder/document-22875>`_
- `Ordnungssystem <https://github.com/4teamwork/opengever.core/blob/master/opengever/examplecontent/profiles/repository_minimal/opengever_repositories/ordnungssystem.xlsx?raw=true>`_

Anhand der Checkliste müssen folgende Konfigurations-Attribute definiert werden:

- Domain: [name].onegovgever.ch *z.B.: 4teamwork.onegovgever.ch*
- Repo-Link: https://github.com/4teamwork/opengever.[name]
- Server: [name] *z.B.: ipet*
- Server-Pfad:
- Deployment: [number] *z.B.: 09*
- Plone-Site id: [id] *z.B.: 4tw*
- postgres-db: ogds_[name] *z.B.: ogds_4teamwork*
- LDAP Ast `ou=[name],ou=OneGovGEVER,dc=4teamwork,dc=ch` einrichten
- bumblebee secret: gever_[name]

Policy generieren
-----------------
Wir erstellen die Policy mit dem Policy-Generator gemäss `GEVER Readme <https://github.com/4teamwork/opengever.core#creating-policies>`_.

.. code-block:: bash

    $ bin/create-policy

Die Antworten dazu sind der Excel Checkliste und dem Jira-Issue zu entnehmen.

Policy konfigurieren
--------------------
Nachdem die Policy erstellt wurde, müssen diverse manuelle Schritte wie folgt durchgeführt werden:

- aktuellen Release im ``versions.cfg`` eintragen
- initiale Templates hinzufügen, falls vorhanden. Diese müssen in der Datei ``opengever.[name]/opengever/[name]/profiles/default_content/opengever_content/02-templates.json`` eingetragen werden, die entsprechenden blobs kommen in ``/opengever.[name]/opengever/[name]/profiles/default_content/opengever_content/templates``
- Ordnungssystem gemäss :ref:`policies-repository` testen und hinzufügen
- `bin/buildout` mit ``development.cfg``
- Plone-Site erstellen
- Theme übers `@@teamraumtheme-controlpanel` anpassen, Logo und u.U. `Höhe des Kopfbereiches`
- Theme exportieren und als ``opengever.[name]/opengever/[name]/profiles/default/customstyles.json` hinterlegen[name]/opengever/[name]/profiles/default/customstyles.json`` hinterlegen
- finaler lokaler Test, Plone-Site löschen und neu erstellen
- privates Repo ``http://github.com/4teamwork/opengever.[name]`` einrichten und Policy pushen
- initiale Gruppen: e.g.: [name]_admins, [name]_users, [name]_inbox im LDAP erstellen (https://ldaptain.4teamwork.ch/)

Policy auf Server installieren
------------------------------
Betrieb
^^^^^^^
Folgende Punkte müssen vom Betrieb erledigt werden:

- IANUS Portal einrichten
- DNS, Haproxy etc. konfigurieren
- Bumblebee einrichten

Entwickler
^^^^^^^^^^
Folgende Punkte müssen vom Entwickler erledigt werden:

- SQL-DB erstellen mit ``createdb [ogds-name]``
- Policy auf Server Klonen mit ``git clone [repo-url]``
    - Namenskonventionen für Deployments auf dem Server beachten
- Policy auf dem Server mit ``[python-pfad] bootstrap.py`` und ``bin/buildout`` installieren
    - korrekter Python Pfad für Bootstrapping verwenden. Der korrekte Pfad kann in einem bestehenden Deployment im File ``bin/buildout`` nachgeschaut werden
- Instanzen über den Supervisor Deamon starten mit ``bin/supervisord``
- GEVER kann über einen SSH Tunnel auf eine Instanz installieret werden
- Solr gemäss `Dokumentation <https://github.com/4teamwork/opengever.core#installing-and-activating-solr>`_ aktivieren
- cas_auth plugin URL anpassen: ``acl_users/cas_auth/manage_config`` => von ``/portal`` zu ``/portal/cas``


Weiterführende Links
--------------------

.. toctree::
   :maxdepth: 1

   repository
