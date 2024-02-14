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
        "deadline": "2018-10-16",
        "responsible": "john.doe",
        "external_reference": "www.example.com"
      }


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Accept: application/json

      {
        "@id": "http://example.org/workspaces/workspace-1/todo-1",
        "@type": "opengever.workspace.todo",
        "UID": "dc295c19ee404aafa7b9331b3eb353f2",
        "...": "..."
      }


Ein ToDo als erledigt markieren
--------------------------------

**Beispiel-Request**:

   .. sourcecode:: http

       POST workspaces/workspace-1/todo-1/@workflow/opengever_workspace_todo--TRANSITION--complete--active_completed HTTP/1.1
       Accept: application/json


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
          "action": "opengever_workspace_todo--TRANSITION--complete--active_completed",
          "title": "Completed",
          "...": "..."
      }

Ein erledigtes ToDo wieder öffnen
---------------------------------

**Beispiel-Request**:

   .. sourcecode:: http

       POST workspaces/workspace-1/todo-1/@workflow/opengever_workspace_todo--TRANSITION--open--completed_active HTTP/1.1
       Accept: application/json


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
          "action": "opengever_workspace_todo--TRANSITION--open--completed_active",
          "title": "Active",
          "...": "..."
      }

Ein ToDo-Status togglen (öffnen/abschliessen)
---------------------------------------------
Der Status eines Todos kann mit dem ``@toggle``-Endpoint umgedreht werden.

**Beispiel-Request**:

   .. sourcecode:: http

       POST workspaces/workspace-1/todo-1/@toggle HTTP/1.1
       Accept: application/json
       Prefer: return=representation


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
         "@id": "workspaces/workspace-1/todo-1/@toggle",
          "review_state": "opengever_workspace_todo--TRANSITION--open--completed_active",
          "is_completed": true,
          "...": "..."
      }


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

ToDo Antworten sind ebenfalls via API ersichtlich bzw. können über diese erstellt, bearbeitet und gelöscht werden.

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


Erstellung, Bearbeitung und Löschen
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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


Die Bearbeitung einer Antwort geschieht mittels PATCH Request. Nur Antworten vom Typ "Kommentar" können bearbeitet werden.

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


Ein DELETE Request auf eine Antwort vom Typ Kommentar löscht den Kommentar.

**Beispiel-Request**:

   .. sourcecode:: http

      DELETE workspaces/workspace-1/todo-1/@responses/1569875801956269 HTTP/1.1
      Accept: application/json
      Content-Type: application/json

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content
