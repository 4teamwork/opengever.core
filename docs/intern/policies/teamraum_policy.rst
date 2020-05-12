.. teamraum-policy:

Erstellen einer Teamraum Policy
===============================

*Für das Erstellen der Policy gibt es im Jira ein* `Issue-Template <https://4teamwork.atlassian.net/browse/TEMP-8>`_.

Vorbereitung
------------
Zum Erstellen einer neuen Policy benötigen wir diverse Informationen vom Kunden. Diese Informationen müssen vom PO organisiert werden. Folgende Dokumente müssen uns ausgefüllt zur Verfügung stehen:

- `Vorlage Checkliste <https://gever.4teamwork.ch/vorlagen/opengever-dossier-templatefolder/document-33846>`_

Anhand der Checkliste müssen die Konfigurations-Attribute im Jira-Teamplate definiert werden können.

Policy generieren/erweitern
---------------------------
Wenn ein Kunde bereits eine eigene GEVER-Policy besitzt, können wir die bestehende Policy mit einem Teamraum-Profil manuell erweitern.

Falls der Kunde noch keine Policy hat, erstellen wir die Policy mit dem Policy-Generator gemäss `GEVER Readme <https://github.com/4teamwork/opengever.core#creating-policies>`_.

.. code-block:: bash

    $ bin/create-policy

Die Antworten dazu sind der Excel Checkliste und dem Jira-Issue zu entnehmen.

Policy konfigurieren
--------------------
Nachdem die Policy erstellt wurde, müssen diverse manuelle Schritte wie folgt durchgeführt werden:

- aktuellen Release im ``versions.cfg`` eintragen
- BUMBLEBEE_SECRET und WORKSPACE_SECRET im `prod-buildout.cfg` hinterlegen
- `bin/buildout` mit ``development.cfg`` lokal ausführen
- Plone-Site erstellen
- finaler lokaler Test, Plone-Site löschen und neu erstellen
- privates Repo ``http://github.com/4teamwork/opengever.[name]`` einrichten und Policy pushen

Policy auf Server installieren
------------------------------
Betrieb
^^^^^^^
Folgende Punkte müssen vom Betrieb erledigt werden:

Wir haben praktisch nie Schreibberechtigung auf das LDAP vom Kunden. Damit externe Personen eingeladen werden können müssen wir jedoch neue Benutzer im LDAP erstellen können. Dazu setzen wir i.d.R. ein eigenes LDAP auf. Benutzer aus dem Kunden-LDAP werden in unseres synchronisiert.

- LDAP aufsetzen und konfigurieren
- LDAP Synchronisation mit `LDAPSync <https://github.com/4teamwork/ldapsync>`_ einrichten
    - LDAP Ast gem. Konfiguration erstellen
    - LDAP-Gruppen erstellen
        - All Users (Enthält Internal und External Users)
        - External Users (externe Benutzer werden in dieser Gruppe erstellt)
        - Internal Users (interne Benutzer werden in diese Gruppe synchronisiert)
        - Admin Users
- IANUS Portal einrichten
    - Registrierung von externen Benutzern ermöglichen
    - Neu registrierte Benutzer müssen Mitglied der Gruppe "External Users" werden
    - ``IANUS_INVITATION_SIGNATURE_SECRET_KEY`` gem. ``WORKSPACE_SECRET`` vom Jira-Ticket setzen
- DNS, Haproxy, u.U. Postgres etc. konfigurieren
- Bumblebee einrichten
- Bumblebee secret im Jira-Ticket hinterlegen
- Neues UI installieren und konfigurieren
    - ``git clone git@github.com:4teamwork/gever-ui.git 99-[name]``
    - ``yarn install --ignore-optional``
    - ``yarn build``
    - Rewrite-Rules konfigurieren

Entwickler
^^^^^^^^^^
Folgende Punkte müssen vom Entwickler erledigt werden:

- SQL-DB erstellen mit ``createdb [ogds-name]``
- Policy auf Server klonen mit ``git clone [repo-url]``
    - Namenskonventionen für Deployments auf dem Server beachten
- Policy auf dem Server mit ``[python-pfad] bootstrap.py`` und ``bin/buildout`` installieren
    - korrekter Python Pfad für Bootstrapping verwenden. Der korrekte Pfad kann in einem bestehenden Deployment im File ``bin/buildout`` nachgeschaut werden
- Instanzen über den Supervisor Deamon starten mit ``bin/supervisord``
- über einen SSH Tunnel auf eine Instanz navigieren und ``zauth`` ausführen, damit der Zope-Benutzer korrekt initialisiert wird
- Teamraum über einen SSH Tunnel auf eine Instanz installieren
- Solr gemäss `Dokumentation <https://github.com/4teamwork/opengever.core#installing-and-activating-solr>`_ aktivieren
- cas_auth plugin URL anpassen: ``acl_users/cas_auth/manage_config`` => von ``/portal`` zu ``/portal/cas``
- Teamraum-App im Ianus für den App-Switcher erstellen
- GEVER mit Teamraum gem. :ref:`teamraum-connect` verbinden
    - Teamraum-App im Ianus des GEVERs für den App-Switcher erstellen
