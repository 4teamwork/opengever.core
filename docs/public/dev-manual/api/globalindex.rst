.. globalindex:

Globalindex
===========

Der globale, also über den ganzen Mandantenverbund verteilte, Aufgabenindex kann mit dem ``@globalindex`` Endpoint abgefragt werden.

Die Felder ``issuer_fullname`` und ``responsible_fullname`` sind überholt und durch ``issuer_actor`` und ``responsible_actor`` ersetzt.

  .. sourcecode:: http

    GET /@globalindex HTTP/1.1
    Accept: application/json

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "batching": null,
      "facets": {},
      "items": [
        { "@id": "http://localhost:8080/ordnungssystem/dossier-23/document-123/task-1",
          "@type": "opengever.task.task",
          "assigned_org_unit": "fa",
          "containing_dossier": "Anfragen 2019",
          "created": "2016-08-31T18:27:33",
          "deadline": "2020-01-01",
          "is_private": true,
          "is_subtask": false,
          "issuer": "robert.ziegler",
          "issuer_fullname": "Ziegler Robert",
          "issuer_actor": {
            "@id": "http://localhost:8080/@actors/robert.ziegler"
            "identifier": "robert.ziegler"
          }
          "issuing_org_unit": "fa",
          "modified": "2016-08-31T18:27:33",
          "oguid": "plone:1016273300",
          "predecessor_id": null,
          "responsible": "Eingangskorb Finanzamt",
          "responsible": "inbox:fa",
          "responsible_actor": {
            "@id": "http://localhost:8080/@actors/inbox:fa"
            "identifier": "inbox:fa"
          }
          "review_state": "task-state-in-progress",
          "task_id": 14,
          "task_type": "For direct execution",
          "title": "re: Direkte Anfrage"
        }
      ]
    }


Optionale Parameter:
--------------------

Paginierung
~~~~~~~~~~~
Die Paginierung funktioniert gleich wie bei anderen Auflistungen auch (siehe :ref:`Kapitel Paginierung <batching>`).

- ``b_start``: Das erste zurückzugebende Element
- ``b_size``: Die maximale Anzahl der zurückzugebenden Elemente

Sortierung
~~~~~~~~~~

- ``sort_on``: Sortierung nach einem indexierten Feld
- ``sort_order``: Sortierreihenfolge: ``ascending`` (aufsteigend) oder ``descending`` (absteigend)

Filter und Suche
~~~~~~~~~~~~~~~~

- ``search``: Filterung nach einem beliebigen Suchbegriff
- ``filters``: Einschränkung nach einem bestimmten Wert eines Feldes

Facetten
~~~~~~~~
- ``facets``: Liste von Feldern für die Facetten Wertebereiche zurückgegeben werden sollen.


**Beispiel: Filtern nach erledigten und abgeschlossenen Aufgaben:**

  .. sourcecode:: http

    GET /@globalindex?filters.review_state:record:list=task-state-resolved&filters.review_state:record:list=task-state-tested-and-closed HTTP/1.1
    Accept: application/json

**Beispiel: Filtern nach Responsible**

  .. sourcecode:: http

    GET /@globalindex?filters.responsible:record=peter.muser HTTP/1.1
    Accept: application/json

**Beispiel: Suche**

  .. sourcecode:: http

    GET /@globalindex?search=vertrag HTTP/1.1
    Accept: application/json

**Beispiel: Wertebereiche des Auftragnehmers und des Aufgabenstatus liefern**

  .. sourcecode:: http

    GET /@globalindex?facets:list=review_state&facets:list=responsible HTTP/1.1
    Accept: application/json
