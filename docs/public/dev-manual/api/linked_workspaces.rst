Verknüpfte Arbeitsräume
=======================

Arbeitsräume können direkt aus GEVER heraus erstellt und mit einem Dossier verknüpft werden.

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
      "items_total": 2
    }


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


Ein GEVER-Dokument in einen verknüpften Teamraum kopieren
---------------------------------------------------------

Über den Endpoint `@copy-document-to-workspace` kann eine Kopie eines GEVER-Dokuments in einen bestehenden Teamraum hochgeladen werden. Dabei ist zu beachten, dass der Teamraum mit dem Haupt-Dossier verknüpft sein muss und dass sich das Dokument innerhalb des aktuellen Hauptdossier oder in einem seiner Subdossiers befindet.

Achtung: Die Kopie wird nicht mit dem originalen Dokument verknüpft. Es handelt sich um ein komplett unabhängiges Objekt. Ein automatisches zurückführen oder synchronisieren mit dem Originaldokument ist nicht möglich.

**Beispiel-Request**:

  .. sourcecode:: http

    POST /ordnungssystem/dossier-23/@copy-document-to-workspace HTTP/1.1
    Accept: application/json
    Content-Type: application/json

    {
      "workspace_uid": "c11627f492b6447fb61617bb06b9a21a"
      "document_uid": "c2ae40cf41c84493ac4b7618d75ee7f7"
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
              "description": "",
              "filename": "rand_image.jpg",
              "review_state": "document-state-draft",
              "title": "rand_image"
          },
          {
              "@id": "http://localhost:8080/fd/workspaces/workspace-5/document-127",
              "@type": "ftw.mail.mail",
              "UID": "ebb87ebde84a4f9cae5fb91d04c89de8",
              "description": "",
              "filename": "Test email.eml",
              "review_state": "mail-state-active",
              "title": "Test email"
          }
        ],
      "items_total": 2
    }


Ein GEVER-Dokument von einem verknüpften Teamraum zurückführen
--------------------------------------------------------------

Über den Endpoint ``@copy-document-from-workspace`` kann eine Kopie eines Dokuments aus einem verknüpften Teamraum in GEVER zurückgeführt werden.

Achtung: Auch wenn das Dokument ursprünglich von GEVER in den Teamraum kopiert wurde, wird beim Zurückführen ein neues, komplett unabhängiges Dokument in GEVER erstellt.

**Beispiel-Request**:

  .. sourcecode:: http

    POST /ordnungssystem/dossier-23/@copy-document-from-workspace HTTP/1.1
    Accept: application/json
    Content-Type: application/json

    {
      "workspace_uid": "c11627f492b6447fb61617bb06b9a21a"
      "document_uid": "c2ae40cf41c84493ac4b7618d75ee7f7"
    }


**Beispiel-Response**:

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": ".../dossier-23/document-1",
      "@type": "opengever.document.document",
      "title": "Ein Dokument",
       "...": "..."
    }
