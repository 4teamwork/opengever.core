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


Antworten
---------

ToDo Antworten sind ebenfalls via API ersichtlich bzw. können über diese erstellt und bearbeitet werden.

Die API Repräsentation eines ToDos, listet unter dem Attribut ``responses`` alle Antworten auf. Eine GET Request auf eine einzelnes ToDo ist ebenfalls möglich und antwortet mit der gleichen Repräsentation.

**Beispiel-Request**:

   .. sourcecode:: http

      GET workspaces/workspace-1/todo-1 HTTP/1.1
      Accept: application/json


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@id": "http://example.org/workspaces/workspace-1/todo-1",
        "@type": "opengever.workspace.todo",
        "responses": [
            {
              "@id": "http://example.org/workspaces/workspace-1/todo-1/@responses/1566374379118225",
              "created": "2019-08-21T09:59:39",
              "creator": {
                "title": "Meier Peter",
                "token": "peter.meier"
              },
              "text": "Ich werde die Anfrage prüfen."
            },
            {
              "@id": "http://example.org/workspaces/workspace-1/todo-1/@responses/1566374384493182",
              "created": "2019-08-21T09:59:44",
              "creator": {
                "title": "Meier Urs",
                "token": "urs.meier"
              },
              "text": "Ist aus meiner Sicht erledigt."
            },
        ]
        "...": "..."
      }


Erstellung und Bearbeitung
~~~~~~~~~~~~~~~~~~~~~~~~~~

Antworten können mit einem POST Request auf den ``@responses`` Endpoint hinzugefügt werden.

**Beispiel-Request**:

   .. sourcecode:: http

      POST workspaces/workspace-1/todo-1/@responses HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "text": "Bitte rasch anschauen. Danke.",
      }


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
        "@id": "http://example.org/workspaces/workspace-1/todo-1/@responses/1566382366854841",
        "created": "2019-08-21T12:12:46",
        "creator": {
          "title": "Meier Peter",
          "token": "peter.meier"
        },
        "text": "Bitte rasch anschauen. Danke."
      }


Die Bearbeitung einer Antwort geschieht mittels PATCH Request.

**Beispiel-Request**:

   .. sourcecode:: http

      PATCH workspaces/workspace-1/todo-1/@responses/1566382366854841 HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "text": "Bitte rasch anschauen. Danke.",
      }


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 Created
      Content-Type: application/json
