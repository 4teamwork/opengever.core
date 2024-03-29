.. _todolists:

ToDo Listen
===========

ToDo Listen dienen als Gruppierungsmöglichkeiten für ToDos. Sie können via REST Operationen :ref:`operations` erstellt, gelesen, bearbeitet und gelöscht werden. Beim Löschen gilt es zu beachten, dass nur leere Listen gelöscht werden können.

Reihenfolge
-----------
Die Reihenfolge der ``items`` bei eienm GET Request eines Teamraums, entspricht der aktuellen Sortierung der Inhalte.

**Beispiel-Request**:


   .. sourcecode:: http

      GET workspaces/workspace-1 HTTP/1.1
      Accept: application/json
      Content-Type: application/json


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@type": "opengever.workspace.workspace",
        "UID": "ac295c19ee404aafa7b9331b3eb353f2",
        "title": "Projekt XY",
        "id": "workspace-1"
        "responsible": "john.doe",
        "items": [
            {
              "@id": "workspaces/workspace-1/todolist-6",
              "@type": "opengever.workspace.todolist",
              "UID": "bc295c19ee404aafa7b9331b3eb353f2",
              "description": "",
              "review_state": "opengever_workspace_todolist--STATUS--active",
              "title": "Allgemeine Projektinformationen"
            },
            {
              "@id": "workspaces/workspace-1/todolist-10",
              "@type": "opengever.workspace.todolist",
              "UID": "cc295c19ee404aafa7b9331b3eb353f2",
              "description": "",
              "review_state": "opengever_workspace_todolist--STATUS--active",
              "title": "Konzept Phase"
            },
            {
              "@id": "workspaces/workspace-1/todolist-2",
              "@type": "opengever.workspace.todolist",
              "UID": "dc295c19ee404aafa7b9331b3eb353f2",
              "description": "",
              "review_state": "opengever_workspace_todolist--STATUS--active",
              "title": "Externe Abklärungen"
            }
        ]
      }


Reihenfolge anpassen
~~~~~~~~~~~~~~~~~~~~
Die Sortierung von ToDo Listen auf Stufe Teamraum kann mit der Verwendung des Parameters ``ordering`` bei einem PATCH Requests verändert werden. Verwenden Sie den Key ``obj_id``, um anzugeben, welche Liste verschoben werden soll. Der key ``delta`` unterstützt die Werte ``top``, ``bottom`` oder eine negative oder positive ganze Zahl für das Auf- oder Abbewegen einer Liste.

Es wird empfohlen den key ``subset_ids`` zu verwenden um nur die Reihenfolgen eines Subsets von Ressourcen zu verändern, beispielsweise nur alle ToDo Listen. Zudem wird bei der Verwendung von ``subset_ids`` ein korrektes Fehlerverhalten bei quasi gleichzeitiger Bearbeitung unterstützt. Weiterführende Informationen zur Anordnung von Objekten finden sie in der `plone.restapi Dokumentation <https://plonerestapi.readthedocs.io/en/latest/content.html?highlight=position#reordering-sub-resources>`_.

**Beispiel-Request**:

   .. sourcecode:: http

      GET workspaces/workspace-1 HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "ordering": {
          "obj_id": "todolist-1",
          "delta": "2",
          "subset_ids": ["todolist-1", "todolist-2", "todolist-3", "todolist-4"]
        }

      }



**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No content


ToDos in Liste verschieben
--------------------------
Um einzelne ToDos zu verschieben, senden sie eine POST Request an den ``@move`` Endpoint des Zielobjekts. Im Request-Body muss unter dem Key ``source`` das zu verschiebende Objekt definiert sein, dieses kann via URL, Pfad, UID oder intid angegeben werden.

**Beispiel-Request**:


   .. sourcecode:: http

      POST workspaces/workspace-1/todolist-4/@move HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "source": "http://nohost/plone/workspaces/workspace-3/todo-1323"
      }



**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
