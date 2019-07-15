.. _todos:

ToDos
======

ToDos (Teamraum Aufgaben) werden wie folgt über die REST-API bedient:

Ein ToDo erstellen
-------------------

**Beispiel-Request**:

   .. sourcecode:: http

      POST workspaces/workspace-1 HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "@type": "opengever.workspace.todo",
        "title": "Bitte Dokument reviewen",
        "text": "Das wichtige Dokument muss angeschaut werden.",
        "deadline": "2018-10-16"
        "responsible": "john.doe",
        "completed": false
      }


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Accept: application/json

      {
        "@id": "http://example.org/workspaces/workspace-1/todo-1",
        "@type": "opengever.workspace.todo",
        "...": "..."
      }


Ein ToDo als erledigt markieren
--------------------------------

**Beispiel-Request**:

   .. sourcecode:: http

      PATCH workspaces/workspace-1/todo-1 HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "completed": true
      }


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content



Ein ToDo neu zuweisen
---------------------

**Beispiel-Request**:

   .. sourcecode:: http

      PATCH workspaces/workspace-1/todo-1 HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "responsible": "jack.johnson",
      }

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content



Ein ToDo löschen
----------------

**Beispiel-Request**:

   .. sourcecode:: http

      DELETE workspaces/workspace-1/todo-1 HTTP/1.1
      Accept: application/json


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content
