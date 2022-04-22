.. _ui_actions:

UI-Actions
==========

Es gibt drei Kategorien von UI-Actions, ``context_actions``, ``listing_actions`` und ``webactions``. Mit dem ``categories`` Parameter kann bestimmt werden, welche Kategorien der Endpoint zurückgeben soll.


**Beispiel-Request**:

  .. sourcecode:: http

    GET /ordnungssystem/fuehrung/dossier-1/@ui-actions?categories:list=context_actions&categories:list=webactions HTTP/1.1
    Accept: application/json

**Beispiel-Response**:

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": "http://localhost:8080/fd/ordnungssystem/fuehrung/@ui-actions?categories:list=context_actions&categories:list=webactions",
      "context_actions": [
        {"id": "edit"},
        "..."
      ],
      "webactions": [
        {
          "action_id": 0,
          "title": "Open in ExternalApp",
          "target_url": "http://example.org/endpoint",
          "mode": "self",
          "display": "actions-menu"
        },
        "..."
      ]
    }

Für die ``listing_actions`` Kategorie gibts zusätzlich den Parameter ``listings``, mit dem festgelegt werden muss, für welches Listing die Actions zurückgeben werden sollen. Falls mehrere Listings angegeben werden, wird die Schnittmenge zurückgegeben.
Zur Verfügung stehen folgende Listings:

- documents
- dossiers
- dossiertempates
- proposals
- tasks
- trash
- workspace_folders

**Beispiel-Request**:

.. sourcecode:: http

    GET /ordnungssystem/fuehrung/dossier-1/@ui-actions?categories:list=listing_actions&listings:list=documents HTTP/1.1
    Accept: application/json

**Beispiel-Response**:

.. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": "http://localhost:8080/fd/ordnungssystem/fuehrung/@ui-actions?categories:list=listing_actions&listings:list=documents",
      "listing_actions": [
        {"id": "edit_items"},
        "..."
      ]
    }
