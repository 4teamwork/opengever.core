.. _usersettings:

Persönliche Einstellungen
=========================

Mittels ``/@user-settings`` Endpoint auf dem Root des Mandanten, können die persönlichen Einstellungen des Benutzer ausgelesen oder angepasst werden.


Auslesen (GET)
--------------

.. http:get:: /@user-settings

   Gibt die Einstellungen des aktuellen Benutzers zurück. Falls noch keine persönlichen Einstellungen vorgenommen wurden, so handelt es sich um die Default-Einstellungen des Mandanten.

   **Request**:

   .. sourcecode:: http

      GET /@user-settings HTTP/1.1
      Accept: application/json

   **Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "notify_inbox_actions": true,
        "notify_own_actions": true,
        "seen_tours": [
          "gever.introduction",
          "gever.release-2019.3"
        ]
      }


Ändern der Einstellungen (PATCH)
--------------------------------

.. http:patch:: /@user-settings

   Die Einstellungen für den aktuellen Benutzer können via PATCH Request geändert werden.

   **Request**:

   .. sourcecode:: http

      PATCH /@user-settings HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "notify_own_actions": true,
        "seen_tours": ["gever.introduction", "gever.release-2019.3"]
      }


   **Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content
      Content-Type: application/json


Gleich wie bei anderen PATCH Requests ist es auch hier möglich die Representation als Response zu erhalten, hierzu muss ein ``Prefer`` Header mit dem Wert ``return=representation`` gesetzt werden.
