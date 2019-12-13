.. globalindex:

Globalindex
===========

L'index des tâches couvrant l'ensemble des clients/départements peut être récupéré avec l'Endpoint ``@globalindex``.

  .. sourcecode:: http

    GET /@globalindex HTTP/1.1
    Accept: application/json

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "batching": null,
      "items": [
        {
          "title": "re: Requête directe",
          "task_type": "direct-execution",
          "task_id": 14,
          "containing_dossier": "Requêtes 2020",
          "created": "2016-08-31T18:27:33",
          "issuing_org_unit": "fa",
          "responsible": "inbox:fa",
          "responsible": "Boîte de réception Finances",
          "modified": "2016-08-31T18:27:33",
          "is_subtask": false,
          "deadline": "2021-01-01",
          "review_state": "task-state-in-progress",
          "assigned_org_unit": "fa",
          "is_private": true,
          "predecessor_id": null,
          "issuer": "robert.ziegler"
        }
      ]
    }


Pagination
~~~~~~~~~~

La pagination fonctionne de la même manière que pour les autres listings (voir :ref:`chapitre pagination <batching>`).


Filter
~~~~~~

**Exemple: Filtrer par tâches complétés et clôturées:**

  .. sourcecode:: http

    GET /@globalindex?filters.review_state:record:list=task-state-resolved&filters.review_state:record:list=task-state-tested-and-closed HTTP/1.1
    Accept: application/json

**Exemple: Filtrer par personne résponsable**

  .. sourcecode:: http

    GET /@globalindex?filters.responsible:record=peter.muser HTTP/1.1
    Accept: application/json
