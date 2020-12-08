.. _inbox:

Eingangskorb
============

Weiterleitungen einem Dossier zuweisen
--------------------------------------

Eine Weiterleitung kann über eine Workflow-Transition einem Dossier zugewiesen werden.

Für das Zuweisen kann sowohl der ``@workflow`` Endpoint oder aber auch der ``@assign-to-dossier`` Endpoint verwendet werden.

Der Vorteil vom ``@assign-to-dossier`` gegenüber dem ``@worfklow`` Endpoint ist, dass dieser nach erfolgreichem Zuweisen den neu erstellten Task zurück gibt. Zudem werden Fehler im Payload besser behandelt als im generischen ``@worfklow`` Endpoint.

Die Verwendung des ``@workflow``-Endpoints kann im Kapitel :ref:`Workflow <workflow>` nachgeschaut werden. Die zu verwendende Transition ist ``forwarding-transition-assign-to-dossier``.

Beim Zuweisen einer Weiterleitung an ein Dossier wird eine neue Aufgabe im angegebenen Dossier erstellt und mit der Weiterleitung verknüpft. Die Weiterleitung wird erledigt und in den aktuellen Jahresordner der Inbox verschoben.

**Beispiel-Request**:

   .. sourcecode:: http

      POST /inbox/forwarding-1/@assign-to-dossier HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "target_uid": "123",
        "comment": "Bitte anschauen"
      }


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
        "@id": "http://example.org/ordnungssystem/dossier-1/task-1",
        "...": "..."
      }


Aufgabeneigenschaften ändern
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Standardmässig wird beim Zuweisen einer Weiterleitung an ein Dossier eine Aufgabe erstellt, welche den Titel und weitere Attribute von der Weiterleitung erben.

Die Aufgabe kann jedoch über den Endpoint komplett selber definiert werden. Dazu kann der Parameter ``task`` im Payload des Requests verwendet werden.

**Beispiel-Request**:

   .. sourcecode:: http

      POST /inbox/forwarding-1/@assign-to-dossier HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "target_uid": "123",
        "task": {
          "title": "Wichtige Aufgabe aus einer Weiterleitung",
          "task_type": "information",
          "deadline": "2016-11-01",
          "is_private": false,
          "responsible": "robert.ziegler",
          "responsible_client": "fa",
          "revoke_permissions": true,
          "issuer": "robert.ziegler"
        }
      }


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
        "@id": "http://example.org/ordnungssystem/dossier-1/task-1",
        "title": "Wichtige Aufgabe aus einer Weiterleitung",
        "...": "..."
      }
