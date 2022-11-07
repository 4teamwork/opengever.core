.. _linked-workspaces:

Verknüpfte Arbeitsräume
=======================

Arbeitsräume können direkt aus GEVER heraus erstellt und mit einem Dossier verknüpft werden.

.. _get-linked-workspaces:

Verknüpfte Teamräume abrufen
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ein GET-Request auf den Endpoint `@linked-workspaces` auf einem Dossier gibt die verknüpften Teamräume für ein Dossier zurück:


  .. sourcecode:: http

    GET /ordnungssystem/dossier-23/@linked-workspaces HTTP/1.1
    Accept: application/json

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": "/ordnungssystem/dossier-23/@linked-workspaces",
      "items": [
        {
          "@id": "http://example.ch/workspaces/workspace-5",
          "@type": "opengever.workspace.workspace",
          "...": "..."
        },
        {
          "@id": "http://example.ch/workspaces/workspace-3",
          "@type": "opengever.workspace.workspace",
          "...": "..."
        }
      ],
      "items_total": 2,
      "workspaces_without_view_permission": false
    }

Das Feld `workspaces_without_view_permission` gibt an, ob noch weitere Teamräume existieren, für die der Benutzer keine Leserechte hat.


Dossier mit Teamraum verknüpfen
-------------------------------

Ein Dosser kann über den Endpoint `@create-linked-workspace` mit einem neuen Teamraum verknüpft werden.
Als Antwort erhalten Sie eine Representation des erstellten Teamraums

**Beispiel-Request**:

  .. sourcecode:: http

    POST /ordnungssystem/dossier-23/@create-linked-workspace HTTP/1.1
    Accept: application/json
    Content-Type: application/json

    {
      "title": "Externe Zusammenarbeit"
    }


**Beispiel-Response**:

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": ".../workspaces/workspace-1",
      "@type": "opengever.workspace.workspace",
      "title": "Externe Zusammenarbeit",
       "...": "..."
    }


Dossier mit bestehendem Teamraum verknüpfen
-------------------------------------------

Ein Dosser kann über den Endpoint ``@link-to-workspace`` mit einem bestehenden Teamraum verknüpft werden.

**Beispiel-Request**:

  .. sourcecode:: http

    POST /ordnungssystem/dossier-23/@link-to-workspace HTTP/1.1
    Accept: application/json
    Content-Type: application/json

    {
      "workspace_uid": "c11627f492b6447fb61617bb06b9a21a"
    }

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content

.. _unlink-workspace:

Teamraum Verknüpfung entfernen
------------------------------

Eine bestehende Verknüpfung eines Teamraums kann mit dem ``@unlink-workspace`` Endpoint entfernt werden. Dabei werden auch bestehende Locks auf verlinkten Dokumenten aufgehoben. Der Teamraum bleibt aber bestehen. Mit dem Parameter ``deactivate_workspace`` kann der Teamraum zusätzlich deaktiviert werden.

**Beispiel-Request**:

  .. sourcecode:: http

    POST /ordnungssystem/dossier-23/@unlink-workspace HTTP/1.1
    Accept: application/json
    Content-Type: application/json

    {
      "workspace_uid": "c11627f492b6447fb61617bb06b9a21a",
      "deactivate_workspace": true
    }

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content


Teilnehmer in einem verknüpften Teamraum setzen
-----------------------------------------------

Mit dem ``@linked-workspace-participations`` Endpoint können Teilnehmer auf einem verknüpften Teamraum hinzugefügt werden.

**Beispiel-Request**:

  .. sourcecode:: http

    POST /ordnungssystem/dossier-23/@linked-workspace-participations HTTP/1.1
    Accept: application/json
    Content-Type: application/json

    {
      "workspace_uid": "c11627f492b6447fb61617bb06b9a21a"
      "participants": [
        {"participant": "max.muster", "role": "WorkspaceAdmin"},
        {"participant": "maria.meier", "role": "WorkspaceGuest"}
      ]
    }

**Beispiel-Response**:

   .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": "/ordnungssystem/dossier-23/@linked-workspace-participations",
      "items": [
          {
            "@id": "http://localhost:8080/fd/workspaces/workspace-1/@participations/max.muster",
            "@type": "virtual.participations.user",
            "is_editable": true,
            "role": {
              "title": "Admin",
              "token": "WorkspaceAdmin"
            },
            "participant_actor": {
              "@id": "http://localhost:8081/fd/@actors/max.muster",
              "identifier": "max.muster",
            },
            "participant": {
              "@id": "http://localhost:8081/fd/@ogds-users/max.muster",
              "@type": "virtual.ogds.user",
              "active": true,
              "email": "max.muster@example.com",
              "title": "Max Muster (max.muster)",
              "id": "max.muster",
              "is_local": null
            },
          },
          {
            "@id": "http://localhost:8080/fd/workspaces/workspace-1/@participations/maria.meier",
            "...": "..."
          },
      ]
    }


Teilnehmer in einen verknüpften Teamraum einladen
-------------------------------------------------

Mit dem ``@linked-workspace-invitations`` Endpoint können Teilnehmer auf einem verknüpften Teamraum eingeladen werden.

**Beispiel-Request**:

  .. sourcecode:: http

    POST /ordnungssystem/dossier-23/@linked-workspace-invitations HTTP/1.1
    Accept: application/json
    Content-Type: application/json

    {
      "workspace_uid": "c11627f492b6447fb61617bb06b9a21a"
      "recipient_email": "max.muster@example.com",
      "role": {"token": "WorkspaceGuest"},
    }

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content


Ein GEVER-Dokument in einen verknüpften Teamraum kopieren
---------------------------------------------------------

Über den Endpoint `@copy-document-to-workspace` kann eine Kopie eines GEVER-Dokuments in einen bestehenden Teamraum hochgeladen werden. Dabei ist zu beachten, dass der Teamraum mit dem Haupt-Dossier verknüpft sein muss und dass sich das Dokument innerhalb des aktuellen Hauptdossier oder in einem seiner Subdossiers befindet.

Wird eine `folder_uid` angegeben, wird das Dokument in den enstprechenden Folder im Teamraum kopiert, ansonsten in das root des angegebenen Teamraums.

Die Kopie wird mit dem originalen Dokument verknüpft. Diese Verknüpfung wird auf beiden Objekten eingetragen (dem ursprünglichen GEVER-Dokument, und der Kopie im Teamraum), und ist in einem GET Request auf das entsprechende Dokument im Property ``teamraum_connnect_links`` sichtbar.

Ein automatisches Zurückführen oder Synchronisieren mit dem Originaldokument ist zur Zeit allerdings noch nicht möglich.

Das GEVER-Dokument kann beim Kopieren gesperrt werden, wenn der optionale ``lock`` Parameter auf ``True`` gesetzt wird. Dies verhindert, dass das Dokument im Gever überarbeitet wird.

**Beispiel-Request**:

  .. sourcecode:: http

    POST /ordnungssystem/dossier-23/@copy-document-to-workspace HTTP/1.1
    Accept: application/json
    Content-Type: application/json

    {
      "workspace_uid": "c11627f492b6447fb61617bb06b9a21a"
      "document_uid": "c2ae40cf41c84493ac4b7618d75ee7f7"
      "folder_uid": "dd0d865477204f11b8aa2108cd3940bd"
      "lock": "True"
    }


**Beispiel-Response**:

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": ".../workspaces/workspace-1/document-1",
      "@type": "opengever.document.document",
      "title": "Ein Dokument",
       "...": "..."
    }


Ein GEVER-Dossier in einen verknüpften Teamraum kopieren
--------------------------------------------------------

Ein Dossier, inkl. Subdossiers, kann in mehreren Schritten in den mit dem Hauptdossier verküpften Teamraum kopiert werden:

Zuerst kann über den ``@prepare-copy-dossier-to-workspace`` Endpoint die Ordnerstruktur des Dossiers in den Teamraum gespiegelt werden. Der Endpoint erstellt im Teamraum die entsprechende Ordnerstruktur, und liefert eine Liste von zu kopierenden Dokumenten zurück, und welchem Ordner diese zugeordnet werden. Danach können diese Dokumente über den ``@copy-document-to-workspace`` Endpoint in die jeweiligen Ordner kopiert werden.


Der ``@prepare-copy-dossier-to-workspace`` wird auf dem zu kopierenden Dossier aufgerufen, und hat zwei Modi: Validierung, und Erstellung der Struktur.

In beiden Fällen muss die ``workspace_uid`` des Teamraums angegeben werden, in welchen das Dossier kopiert werden soll.

Wenn der Parameter ``validate_only`` auf true gesetzt ist, prüft der Endpoint nur die entsprechenden Vorbedingungen (Hautpdossier mit Teamraum verküpft, keine ausgecheckten Dokumente), und liefert ggf. die Fehler zurück.

Wenn ``validate_only`` auf false gesetzt ist, erstellt der Endpoint im angegebenen Workspace eine leere Ordnerstruktur, welche der Dossierstruktur entspricht. In der Response gibt der Endpoint dann eine Liste von Dokumenten zurück, und die Angabe, in welchen Ordner sie kopiert werden sollen:



**Beispiel-Request**:

  .. sourcecode:: http

    POST /ordnungssystem/dossier-23/@prepare-copy-dossier-to-workspace HTTP/1.1
    Accept: application/json
    Content-Type: application/json

    {
      "workspace_uid": "c11627f492b6447fb61617bb06b9a21a",
      "validate_only": false
    }


**Beispiel-Response**:

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
        "docs_to_upload": [
            {
                "source_document_uid": "24c8742581a046f9b645f24c9a9cd874",
                "target_folder_uid": "d95b653a1fc642c18851616d79b6e5d5",
                "title": "Some document"
            },
            {
                "source_document_uid": "189f2688fb334c1ea7c7ba60411baf78",
                "target_folder_uid": "b529713f1f28421da968550f3aef7cdb",
                "title": "Document in Subdossier"
            }
        ]
    }


Dokumente in einem verknüpften Teamraum auflisten
-------------------------------------------------

Über den Endpoint ``@list-documents-in-linked-workspace`` werden die Dokumente in einem verlinktem Teamraum aufgelistet. Der Endpoint benötigt als zusätzlichen Pfad Parameter die UID des Teamraums, z.B. ``@list-documents-in-linked-workspace/workspace_uid``. Dieser Endpoint unterstützt Batching.

**Beispiel-Request**:

  .. sourcecode:: http

    GET /ordnungssystem/dossier-23/@list-documents-in-linked-workspace/42bd0fa3b90548fda53105081886a21c HTTP/1.1
    Accept: application/json

**Beispiel-Response**:

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": "http://localhost:8080/fd/dossier-23/@list-documents-in-linked-workspace/42bd0fa3b90548fda53105081886a21c",
      "batching": null,
      "items": [
          {
              "@id": "http://localhost:8080/fd/workspaces/workspace-5/document-126",
              "@type": "opengever.document.document",
              "UID": "39e29affb6f94a7d905f587fce3244f8",
              "checked_out": "",
              "description": "",
              "file_extension": ".jpg",
              "filename": "rand_image.jpg",
              "review_state": "document-state-draft",
              "title": "rand_image"
          },
          {
              "@id": "http://localhost:8080/fd/workspaces/workspace-5/document-127",
              "@type": "ftw.mail.mail",
              "UID": "ebb87ebde84a4f9cae5fb91d04c89de8",
              "checked_out": "",
              "description": "",
              "file_extension": ".eml",
              "filename": "Test email.eml",
              "review_state": "mail-state-active",
              "title": "Test email"
          }
        ],
      "items_total": 2
    }




Ein GEVER-Dokument von einem verknüpften Teamraum zurückführen
--------------------------------------------------------------

Über den Endpoint ``@copy-document-from-workspace`` kann ein Dokument aus einem verknüpften Teamraum in GEVER zurückgeführt werden.

Abhängig vom Boolean-Parameter ``as_new_version`` kann bestimmt werden, ob das Dokument als neue Version des Ursprungsdokuments zurückgeführt werden soll (falls möglich), oder als Kopie (als neues GEVER-Dokument).

In gewissen Fällen ist es nicht möglich, ein Dokument als neue Version zurückzuführen. Z.B. wenn das Teamraum-Dokument nicht mit einem GEVER-Dokument verlinkt ist, das Dokument keine Datei hat, oder es sich um ein E-Mail handelt.

Wenn mit ``"as_new_version": true`` in solchen Fällen trotzdem eine neue Version gewünscht wird, erstellt das Backend automatisch eine Kopie statt einer Version. Die Entscheidung, welchen Rückführungsmechanismus das Backend schlussendlich gewählt und durchgeführt hat, wird in der Response im Attribut ``teamraum_connect_retrieval_mode`` zurückgegeben: Entweder ``copy`` oder ``version``.


**Beispiel-Request**:

  .. sourcecode:: http

    POST /ordnungssystem/dossier-23/@copy-document-from-workspace HTTP/1.1
    Accept: application/json
    Content-Type: application/json

    {
      "workspace_uid": "c11627f492b6447fb61617bb06b9a21a",
      "document_uid": "c2ae40cf41c84493ac4b7618d75ee7f7",
      "as_new_version": true
    }


**Beispiel-Response**:

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": ".../dossier-23/document-1",
      "@type": "opengever.document.document",
      "title": "Ein Dokument",
      "teamraum_connect_retrieval_mode": "version",
       "...": "..."
    }
