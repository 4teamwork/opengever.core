Teamraum-Mitglieder
===================

Der ``@actual-workspace-members`` Endpoint liefert ein Vokabular aller Mitglieder eines Teamraums.

**Beispiel-Request**:

   .. sourcecode:: http

       GET /workspace-1/@actual-workspace-members?b_size=3 HTTP/1.1
       Accept: application/json

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
          "@id": "http://localhost:8080/fd/workspaces/workspace-1/@actual-workspace-members",
          "batching": {
            "@id": "http://localhost:8080/fd/workspaces/workspace-1/@actual-workspace-members?b_size=3",
            "first": "http://localhost:8080/fd/workspaces/workspace-1/@actual-workspace-members?b_start=0&b_size=3",
            "last": "http://localhost:8080/fd/workspaces/workspace-1/@actual-workspace-members?b_start=9&b_size=3",
            "next": "http://localhost:8080/fd/workspaces/workspace-1/@actual-workspace-members?b_start=3&b_size=3"
          },
          "items": [
            {
              "title": "Baerfuss Kaethi (kathi.barfuss)",
              "token": "kathi.barfuss"
            },
            {
              "title": "Kohler Nicole (nicole.kohler)",
              "token": "nicole.kohler"
            },
            {
              "title": "Ziegler Robert (robert.ziegler)",
              "token": "robert.ziegler"
            }
          ],
          "items_total": 12
        }

