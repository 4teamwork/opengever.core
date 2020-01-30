Tâches
======

Les tâches peuvent également être contrôlées via REST API. La création d'une tâche se faite comme pour les autres contenus via une Request POST (Voir chapitre :ref:`operations`):


**Exemple de Request**:

   .. sourcecode:: http

      POST /(container) HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "@type": "opengever.task.task",
        "title": "Prière de contrôler le document",
        "responsible": "john.doe",
        "issuer": "john.doe",
        "responsible_client": "afi",
        "task_type": "direct-execution"
      }


**Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Accept: application/json

      {
        "@id": "http://example.org/ordnungssystem/direction/dossier-1/task-5",
        "@type": "opengever.task.task",
        "...": "..."
      }


Modifications/Changements d'état
--------------------------------


La modification d'une tâche via Patch Request n'est possible que de manière limitée, c'est-à-dire lorsque la tâche est dans un état `ouvert`. Dans le déroulement subséquent de la tâche, les changements sont uniquement traités via des changements d'état. Ceci se fait par l'Endpoint ``@workflow`` avec la Transition ID comme paramètre additionnel. 

Une requête GET sur l'endpoint @workflow endpoint Liste les transitions possibles:

**Exemple de Request**:

   .. sourcecode:: http

      GET /(path)/@workflow HTTP/1.1
      Accept: application/json


**Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Accept: application/json

      {
        "@id": "http://example.org/ordnungssystem/direction/dossier-1/task-5/@workflow",
        "history": [],
        "transitions": [
          {
          "@id": "http://example.org/ordnungssystem/direction/dossier-1/task-5/@workflow/task-transition-modify-deadline",
          "title": "Modifier délai"
          },
          {
          "@id": "http://example.org/ordnungssystem/direction/dossier-1/task-5/@workflow/task-transition-open-in-progress",
          "title": "Accepter"
          },
          {
          "@id": "http://example.org/ordnungssystem/direction/dossier-1/task-5/@workflow/task-transition-reassign",
          "title": "Réassigner"
          }
        ]
      }


Une transition est exécutée de la manière suivante:

**Exemple de Request**:

   .. sourcecode:: http

      POST /(path)/@workflow/task-transition-open-in-progress HTTP/1.1
      Accept: application/json

      {
        "text": "Ok, je m'en occupe!"
      }


**Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Accept: application/json

      {
        "action": "task-transition-open-in-progress",
        "actor": "philippe.gross",
        "comments": "",
        "review_state": "task-state-in-progress",
        "time": "2019-01-24T16:12:12+00:00",
        "title": "En traitement"
      }



Les changements d'état sont documentés comme suit:


Accepter
~~~~~~~~

Transition IDs:
 - ``task-transition-open-in-progress``

Métadonnées additionnelles:

   .. py:attribute:: text

       :Type: ``Text``


Modifier délai
~~~~~~~~~~~~~~

Transition IDs:
 - ``task-transition-modify-deadline``

Métadonnées additionnelles:

   .. py:attribute:: new_deadline

       :Type: ``Date``
       :Obligatoire: Oui :required:`(*)`

   .. py:attribute:: text

       :Type: ``Text``


Réassigner
~~~~~~~~~~

Transition IDs:
 - ``task-transition-reassign``

Métadonnées additionnelles:

   .. py:attribute:: text

       :Type: ``Text``

   .. py:attribute:: responsible

       :Type: ``Choice``
       :Obligatoire: Oui :required:`(*)`


   .. py:attribute:: responsible_client

       :Type: ``Choice``
       :Obligatoire: Oui :required:`(*)`


Compléter
~~~~~~~~~

Transition IDs:
 - ``task-transition-in-progress-resolved``
 - ``task-transition-open-resolved``

Métadonnées additionnelles:

   .. py:attribute:: text

       :Type: ``Text``


Réviser
~~~~~~~

Transition IDs:
 - `task-transition-resolved-in-progress`

Métadonnées additionnelles:

   .. py:attribute:: text

       :Type: ``Text``


Fermer
~~~~~~

Transition IDs:
 - ``task-transition-resolved-tested-and-closed``
 - ``task-transition-in-progress-tested-and-closed``
 - ``task-transition-open-tested-and-closed``


Métadonnées additionnelles:

   .. py:attribute:: text

       :Type: ``Text``


Annuler
~~~~~~~

Transition IDs:
 - ``task-transition-open-cancelled``
 - ``task-transition-in-progress-cancelled``


Métadonnées additionnelles:

   .. py:attribute:: text

       :Type: ``Text``


Refuser
~~~~~~~

Transition IDs:
 - ``task-transition-open-rejected``
 - ``task-transition-in-progress-cancelled``


Métadonnées additionnelles:

   .. py:attribute:: text

       :Type: ``Text``


Rouvrir
~~~~~~~

Transition IDs:
 - ``task-transition-cancelled-open``
 - ``task-transition-rejected-open``


Métadonnées additionnelles:

   .. py:attribute:: text

       :Type: ``Text``


Déléguer
~~~~~~~~

Transition IDs:
 - ``task-transition-delegate``


Métadonnées additionnelles:

   .. py:attribute:: text

       :Type: ``Text``

Additionnellément, les changements d'état suivants sont disponibles pour les tâches séquentielles:


Sauter
~~~~~~

Transition IDs:
 - ``task-transition-planned-skipped``
 - ``task-transition-rejected-skipped``


Métadonnées additionnelles:

   .. py:attribute:: text

       :Type: ``Text``


Ouvrir
~~~~~~

Transition IDs:
 - ``task-transition-planned-open``


Métadonnées additionnelles:

   .. py:attribute:: text

       :Type: ``Text``


Commenter une tâche
-------------------

Il est possible de commenter une tâche via l'Endpoint `@responses`:


Ajouter un commentaire
~~~~~~~~~~~~~~~~~~~~~~

Une requête POST sur l'Endpoint `@responses` créé un commentaire avec l'utilisateur courant

**Exemple de Request**:

   .. sourcecode:: http

      POST http://example.org/ordnungssystem/direction/dossier-1/task-5/@responses HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "text": "Prière de vérifier rapidement! Merci.",
      }


**Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
        "@id": "http://example.org/ordnungssystem/direction/dossier-1/task-5/@responses/1569875801956269",
        "added_objects": [],
        "changes": [],
        "created": "2019-05-21T13:57:42+00:00",
        "creator": {
          "title": "Meier Peter",
          "token": "peter.meier"
        },
        "mimetype": "",
        "related_items": [],
        "rendered_text": "",
        "response_id": 1569875801956269,
        "response_type": "comment",
        "successor_oguid": "",
        "text": "Prière de vérifier rpaidement! Merci.",
        "transition": "task-commented"
      }


Modifier un commentaire
~~~~~~~~~~~~~~~~~~~~~~~

Une Request PATCH sur une ressource de type commentaire modifie le commentaire.

**Exemple de Request**:

   .. sourcecode:: http

      PATCH http://example.org/ordnungssystem/direction/dossier-1/task-5/@responses/1569875801956269 HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "text": "Ca s'est réglé tout seul.",
      }


**Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 204 Created
      Content-Type: application/json


Déroulement d'une tâche
-----------------------

Le déroulement d'une tâche est contenu dans une représentation GET de celle-ci, sous l'attribut ``responses``.

**Exemple de Response sur une request GET**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Accept: application/json

      {
        "@id": "http://example.org/ordnungssystem/direction/dossier-1/task-5",
        "@type": "opengever.task.task",
        "UID": "3a551f6e3b62421da029dfceb71656e6",
        "items": [],
        "responses": [
          {
            "response_id": 1
            "response_type": "default"
            "added_objects": [],
            "changes": [],
            "creator": "zopemaster",
            "created": "2019-05-21T13:57:42+00:00",
            "date_of_completion": null,
            "related_items": [],
            "reminder_option": null,
            "text": "Lorem ipsum.",
            "transition": "task-commented"
          },
          {
            "response_id": 2
            "response_type": "default"
            "added_objects": [],
            "changes": [],
            "creator": "zopemaster",
            "created": "2019-05-21T14:02:01+00:00",
            "date_of_completion": null,
            "related_items": [],
            "text": "Suspendisse faucibus, nunc et pellentesque egestas.",
            "transition": "task-transition-open-in-progress"
          },
        ]
        "responsible": "david.erni",
        "...": "...",
      }
