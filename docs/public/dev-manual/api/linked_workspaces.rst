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


Ein GEVER-Dokument in einen verknüpften Teamraum kopieren
---------------------------------------------------------

Über den Endpoint `@copy-document-to-workspace` kann eine Kopie eines GEVER-Dokuments in einen bestehenden Teamraum hochgeladen werden. Dabei ist zu beachten, dass der Teamraum mit dem Haupt-Dossier verknüpft sein muss und dass sich das Dokument innerhalb des aktuellen Hauptdossier oder in einem seiner Subdossiers befindet.

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
