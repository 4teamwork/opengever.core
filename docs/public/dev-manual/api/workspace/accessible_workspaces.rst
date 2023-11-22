.. _accessible-workspaces:

Zugängliche Teamräume
=====================

Der ``@accessible-workspaces`` Endpoint liefert alle Teamräume, für die ein Benutzer eine Ansichtsberechtigung hat. Der Endpoint steht nur für Administratoren auf Stufe PloneSite zur Verfügung.

**Beispiel-Request**:

   .. sourcecode:: http

       GET /fd/@accessible-workspaces/kathi.barfuss HTTP/1.1
       Accept: application/json

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
          "@id": "http://example.org/@accessible-workspaces/kathi.barfuss",
          "items": [
            {
              "@id": "http://example.org/workspace-4",
              "@type": "opengever.workspace.workspace",
              "UID": "a3c9f8a47655463ea7a4a43bf1fdf40c",
              "review_state": "opengever_workspace--STATUS--active",
              "title": "Anlageberatung",
            },
            {
              "@id": "http://example.org/workspace-12",
              "@type": "opengever.workspace.workspace",
              "UID": "b3c9f8a47655463ea7a4a43bf1fdf40c",
              "review_state": "opengever_workspace--STATUS--active",
              "title": "Gemeindeversammlung",
            },
            {
              "@id": "http://example.org/workspace-1",
              "@type": "opengever.workspace.workspace",
              "UID": "c3c9f8a47655463ea7a4a43bf1fdf40c",
              "review_state": "opengever_workspace--STATUS--active",
              "title": "Neuimplementierung GUI",
            },
          ],
        }
