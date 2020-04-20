.. _label-policy:

Erstellen einer policy
======================

Policies können mittels Skript erstellt werden, siehe auch `<https://github.com/4teamwork/opengever.core#creating-policies>`_:

.. code-block:: bash

    $ bin/create-policy


Da viele Fragen während der Erstellung auftauchen, ist es gut die Antworten vorzubereiten.
Die Antworten dazu sind der Excel Checkliste, der Auftragsbestätigung aus dem GEVER Dossier oder dem Deployment-Server resp. dem Betrieb zu entnehmen.

Als Input zur Erstellung einer Policy brauchen wir:

- Ausgefüllte Checkliste gemäss Vorlage unter `<https://gever.4teamwork.ch/vorlagen/opengever-dossier-templatefolder/document-22875>`_
- Ordnungssystem gemäss Vorlage unter `<https://github.com/4teamwork/opengever.core/blob/master/opengever/examplecontent/profiles/repository_minimal/opengever_repositories/ordnungssystem.xlsx?raw=true>`_
- Operative Abklärungen gemäss :ref:`policies-deployment`

Die Fragen können aus folgender Datei entnommen werden: https://github.com/4teamwork/opengever.core/blob/master/opengever/policytemplates/policy_template/.mrbob.ini

Mit diesen Angaben kann die Policy generiert werden. Danach sind folgende manuelle
Schritte nötig:

- Aktuellen Release im `versions.cfg` eintragen
- Initiale Templates hinzufügen, falls vorhanden. Diese müssen in der Datei `opengever.[name]/opengever/[name]/profiles/default_content/opengever_content/02-templates.json` eingetragen werden, die entsprechenden blobs kommen in `/opengever.[name]/opengever/[name]/profiles/default_content/opengever_content/templates`

- Ordnungssystem gemäss :ref:`policies-repository` hinzufügen
- `bin/buildout` mit `development.cfg`
- Plone-Site erstellen
- Theme übers `@@teamraumtheme-controlpanel` anpassen, Logo und u.U. `Höhe des Kopfbereiches`
- Theme exportieren und als `opengever.[name]/opengever/[name]/profiles/default/customstyles.json` hinterlegen
- Finaler lokaler Test, Plone-Site löschen und neu erstellen
- Repo `http://github.com/4teamwork/opengever.[name]` einrichten und Policy pushen
