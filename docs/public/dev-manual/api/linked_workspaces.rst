Verknüpfte Arbeitsräume
=======================

Arbeitsräume können direkt aus GEVER heraus erstellt und mit einem Dossier verknüpft werden.

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
