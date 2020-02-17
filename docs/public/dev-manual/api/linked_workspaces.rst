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
