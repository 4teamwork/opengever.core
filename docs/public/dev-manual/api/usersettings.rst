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

Alternative Benachrichtigungsadresse
-----------------------------------

Wenn ``features.alternative_notification_email_enabled`` in ``@config`` aktiv ist,
liefern ``@user-settings`` und ``@config.user_settings`` zusätzlich
``notification_email`` (E-Mail-Adresse oder ``null``). Die Einstellung gehört
immer dem angemeldeten Benutzer; auch Administratoren können sie nicht für andere
Benutzer lesen oder ändern. Ein OGDS-Benutzerkonto ist erforderlich.

Ein PATCH wie ``{"notification_email": "privat@example.org"}`` setzt oder ersetzt
die Adresse. ``{"notification_email": null}`` oder eine leere Zeichenfolge löscht
sie. Ungültige Adressen, andere Datentypen und mehr als 255 Zeichen werden mit
HTTP 400 abgewiesen; dabei werden auch andere Felder desselben PATCH nicht geändert.
Wenn die Funktion deaktiviert ist, fehlt das Feld in Antworten und jeder PATCH
auf dieses Feld wird mit HTTP 400 abgewiesen. Bereits gespeicherte Werte bleiben
erhalten.

Die alternative Adresse ersetzt die primäre Empfängeradresse für einzelne
Benachrichtigungen, tägliche Zusammenfassungen und Mitteilungen beim Teilen von
Teamraum-Inhalten. Ohne alternative Adresse wird die primäre Adresse verwendet;
ohne zustellbare Adresse wird keine E-Mail versendet und eine Zusammenfassung
nicht als versendet markiert. Einladungen sowie Absender- und Reply-To-Adressen
bleiben unverändert. Beim Teilen bleiben To/Cc/Bcc erhalten: Adressen in To/Cc
sind für andere E-Mail-Empfänger sichtbar.

Die Einstellung wird nicht in Benutzerlisten, Profilen, Reports oder
Dokumenteigenschaften veröffentlicht und übersteht OGDS-Synchronisation und
Deaktivierung. Es gibt keine Bestätigungs-E-Mail, Doppelzustellung,
Teamraum-spezifische Benutzereinstellung oder Steuerung in der klassischen UI.
