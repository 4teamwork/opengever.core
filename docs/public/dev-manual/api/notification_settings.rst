.. _notification_settings:

Benachrichtigungseinstellungen
==============================

Mit dem ``@notification-settings`` Endpoint können die Benachrichtigungseinstellungen des aktuellen Benutzers ausgelesen und angepasst werden. Der Endpoint steht nur auf Stufe PloneSite zur Verfügung.


Auslesen (GET)
--------------

Gibt die Benachrichtigungseinstellungen des aktuellen Benutzers zurück.

 **Request**:

 .. sourcecode:: http

    GET /@notification-settings HTTP/1.1
    Accept: application/json

 **Response**:

 .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": "http://localhost:8080/fd/@notification-settings",
      "activities": {
        "@id": "http://localhost:8080/fd/@notification-settings/activities",
        "items": [
          {
            "@id": "http://localhost:8080/fd/@notification-settings/activities/task-added-or-reassigned",
            "badge": {
              "regular_watcher": true,
              "task_issuer": true,
              "task_responsible": true
            },
            "digest": {
              "regular_watcher": false,
              "task_issuer": false,
              "task_responsible": false
            },
            "group": "task",
            "id": "task-added-or-reassigned",
            "kind": "task-added-or-reassigned",
            "mail": {
              "regular_watcher": true,
              "task_issuer": false,
              "task_responsible": true
            },
            "personal": false,
            "title": "Aufgabe erstellt / neu zugewiesen"
          },
          { "...": "..." },
        ]
      },
      "general": {
        "@id": "http://localhost:8080/fd/@notification-settings/general",
        "items": [
          {
            "@id": "http://localhost:8080/fd/@notification-settings/general/notify_own_actions",
            "group": "general",
            "help_text": "Standardmässig werden für selbst ausgeführte Aktionen keine Benachrichtigungen ausgelöst. Mit dieser Option kann dieses Verhalten verändert werden. Persönlich vorgenommene Benachrichtigungseinstellungen pro Aktionstyp gelten dabei nach wie vor.",
            "id": "notify_own_actions",
            "personal": false,
            "title": "Benachrichtigung für eigene Aktionen aktivieren",
            "value": false
          },
          { "...": "..." },
        ]
      },
      "translations": [
        {
          "id": "task_responsible",
          "title": "Auftragnehmer"
        },
        {
          "id": "task_issuer",
          "title": "Auftraggeber"
        },
        { "...": "..." },
      ]
    }


Ändern einer Benachrichtigungseinstellung (PATCH)
-------------------------------------------------

Die Einstellungen für den aktuellen Benutzer können via PATCH Request geändert werden.
Dabei wird zwischen generellen Benachrichtigungseinstellungen und Einstellungen für Aktivitätsbenachrichtigungen unterschieden.


 **Beispiel-Request fürs Ändern einer generellen Benachrichtigungseinstellung**:

 .. sourcecode:: http

    PATCH /@notification-settings/general/notify_own_actions HTTP/1.1
    Accept: application/json
    Content-Type: application/json

    {
      "value": true,
    }


 **Response**:

 .. sourcecode:: http

    HTTP/1.1 204 No Content
    Content-Type: application/json


Bei den Einstellungen für Aktivitätsbenachrichtigungen kann gewählt werden, in welcher Rolle man per GEVER-Benachrichtigung (``badge``) , E-Mail (``mail``) und Tageszusammenfassung (``digest``) benachrichtigt werden will. Dabei müssen pro Benachrichtigungstyp alle Rollen mitgegeben werden, in denen man benachrichtigt werden will:

 **Beispiel-Request fürs Ändern einer Einstellung für Aktivitätsbenachrichtigungen**:

 .. sourcecode:: http

    PATCH /@notification-settings/activity/task-added-or-reassigned HTTP/1.1
    Accept: application/json
    Content-Type: application/json

    {
      "mail": {
        "task_issuer": true,
        "regular_watcher": true
      },
      "digest": {
        "regular_watcher": true
      }
    }


 **Response**:

 .. sourcecode:: http

    HTTP/1.1 204 No Content
    Content-Type: application/json

Gleich wie bei anderen PATCH Requests ist es auch hier möglich, die Repräsentation als Response zu erhalten, hierzu muss ein ``Prefer`` Header mit dem Wert ``return=representation`` gesetzt werden.

Zurücksetzen einer Benachrichtigungseinstellung (PATCH)
-------------------------------------------------------

Die Einstellungen für den aktuellen Benutzer können via PATCH Request auf den Standard zurückgesetzt werden.

 **Request**:

 .. sourcecode:: http

    PATCH /@notification-settings/activity/task-added-or-reassigned HTTP/1.1
    Accept: application/json
    Content-Type: application/json

    {
      "reset": true
    }


 **Response**:

 .. sourcecode:: http

    HTTP/1.1 204 No Content
    Content-Type: application/json

