Inhalte teilen
==============
Mit dem ``@share-content`` Endpoint können Teamräume und Inhalte von Teamräumen mit anderen Mitgliedern geteilt werden. Die ausgewählten Mitglieder erhalten eine E-Mail mit einem Hinweis zum geteilten Inhalt. Es können auch Gruppen ausgewählt werden.

**Beispiel-Request**:

  .. sourcecode:: http

    POST /workspaces/workspace-1/todo-1/@share-content HTTP/1.1
    Accept: application/json

    {
      "actors_to": [
        {
          "title": "Baerfuss Kaethi (kathi.barfuss)",
          "token": "kathi.barfuss"
        },
        {
          "title": "Kohler Nicole (nicole.kohler)",
          "token": "nicole.kohler"
        },
      ],
      "actors_cc": [
        {
          "title": "Gruppe A",
          "token": "gruppe-a"
        }
      ],
      "comment": "Have you seen this ToDo yet?"
    }

**Beispiel-Response**:

  .. sourcecode:: http

    HTTP/1.1 204 No Content
