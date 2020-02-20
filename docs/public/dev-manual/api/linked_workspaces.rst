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
