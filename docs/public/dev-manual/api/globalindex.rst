.. globalindex:

Globalindex
===========

Der globale, also über den ganzen Mandantenverbund verteilte, Aufgabenindex kann mit dem ``@globalindex`` Endpoint abgefragt werden.

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
          "title": "re: Direkte Anfrage",
          "task_type": "direct-execution",
          "task_id": 14,
          "created": "2016-08-31T18:27:33",
          "issuing_org_unit": "fa",
          "responsible": "inbox:fa",
          "modified": "2016-08-31T18:27:33",
          "is_subtask": false,
          "deadline": "2020-01-01",
          "review_state": "task-state-in-progress",
          "assigned_org_unit": "fa",
          "is_private": true,
          "predecessor_id": null,
          "issuer": "robert.ziegler"
        }
      ]
    }


Paginierung
~~~~~~~~~~~
Die Paginierung funktioniert gleich wie bei anderen Auflistungen auch (siehe :ref:`Kapitel Paginierung <batching>`).


Filter
~~~~~~

**Beispiel: Filtern nach erledigten und abgeschlossenen Aufgaben:**

  .. sourcecode:: http

    GET /@globalindex?filters.review_state:record:list=task-state-resolved&filters.review_state:record:list=task-state-tested-and-closed HTTP/1.1
    Accept: application/json

**Beispiel: Filtern nach Responsible**

  .. sourcecode:: http

    GET /@globalindex?filters.responsible:record=peter.muser HTTP/1.1
    Accept: application/json
