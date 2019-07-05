.. _todos:

ToDo Listen
===========

Ein ToDo kann in Listen organisiert werden.
Die Verwaltung der ToDo-Listen wird über den ``@todolist`` Endpoint behandelt.

Eine Liste erstellen:
---------------------
Ein POST Request auf den Endpoint erstellt eine neue ToDo-Liste

**Beispiel-Request**:

   .. sourcecode:: http

       POST /workspace-1/@todolist HTTP/1.1
       Accept: application/json

       {
         "title": "01 - Allgemein",
       }

**Beispiel-Response**:

   .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": "http://localhost:8080/fd/workspaces/workspace-1/@todolist/00b4fa3790a8412ca02a0aa6f33bdf48",
      "@type": "virtual.workspace.todolist",
      "UID": "00b4fa3790a8412ca02a0aa6f33bdf48",
      "title": "01 - Allgemein",
      "todos": []
    }

Ein ToDo an das Ende einer Liste hinzufügen:
--------------------------------------------
Führen Sie einen entsprechenden POST-Request auf den Endpoint der Liste aus.

Die URL setzt sich dabei folgendermassen zusammen:
``gever-url/workspaces/{workspace_id}/@todolist/{todo_list_id}``

Als Antwort erhalten Sie die neue serialisierte Liste.

**Beispiel-Request**:

   .. sourcecode:: http

       POST http://localhost:8080/fd/workspaces/workspace-1/@todolist/00b4fa3790a8412ca02a0aa6f33bdf48 HTTP/1.1
       Accept: application/json

       {
           todo_uid: "todo-1"
       }


**Beispiel-Response**:

   .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": "http://localhost:8080/fd/workspaces/workspace-1/@todolist/00b4fa3790a8412ca02a0aa6f33bdf48",
      "@type": "virtual.workspace.todolist",
      "UID": "00b4fa3790a8412ca02a0aa6f33bdf48",
      "title": "01 - Allgemein",
      "todos": ["todo-1"]
    }
