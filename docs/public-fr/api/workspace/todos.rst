.. _todos:

ToDos
=====

Les ToDos (tâches teamraum) sont desservies via la REST-API comme suit:

Créer un ToDo
-------------

**Exemple de Request**:

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


**Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Accept: application/json

      {
        "@id": "http://example.org/workspaces/workspace-1/todo-1",
        "@type": "opengever.workspace.todo",
        "...": "..."
      }


Marquer un ToDo comme accompli
------------------------------

**Exemple de Request**:

   .. sourcecode:: http

      PATCH workspaces/workspace-1/todo-1 HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "completed": true
      }


**Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content



Réassigner un ToDo
---------------------

**Exemple de Request**:

   .. sourcecode:: http

      PATCH workspaces/workspace-1/todo-1 HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "responsible": "jack.johnson",
      }

**Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content



Effacer un ToDo
----------------

**Exemple de Request**:

   .. sourcecode:: http

      DELETE workspaces/workspace-1/todo-1 HTTP/1.1
      Accept: application/json


**Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content


Réponses
--------

Il est aussi possible de consulter les réponses de ToDos via l'API, en l'l'occurrence les créer et modifier. 

La représentation API d'un ToDo liste toutes les réponses sous l'attribut ``responses``. Une Request GET sur un ToDo spécifique est également possible et répond avec la même représentation. 

**Exemple de Request**:

   .. sourcecode:: http

      GET workspaces/workspace-1/todo-1 HTTP/1.1
      Accept: application/json


**Exemple de Response**:

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
              "text": "Vais vérifer la requête."
            },
            {
              "@id": "http://example.org/workspaces/workspace-1/todo-1/@responses/1566374384493182",
              "created": "2019-08-21T09:59:44",
              "creator": {
                "title": "Meier Urs",
                "token": "urs.meier"
              },
              "text": "Est en ordre selon moi."
            },
        ]
        "...": "..."
      }


Création et modification
~~~~~~~~~~~~~~~~~~~~~~~~

Des réponses peuvent être ajoutées à l'aide d'une Request POST sur l'Endpoint ``@responses``.

**Exemple de Request**:

   .. sourcecode:: http

      POST workspaces/workspace-1/todo-1/@responses HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "text": "Prière de voir rapidement. Merci.",
      }


**Exemple de Response**:

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
        "text": "Prière de voir rapidement. Merci."
      }


La modification d'une réponse passe par une Request PATCH.

**Exemple de Request**:

   .. sourcecode:: http

      PATCH workspaces/workspace-1/todo-1/@responses/1566382366854841 HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "text": "Prière de voir rapidement. Merci.",
      }


**Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 204 Created
      Content-Type: application/json
