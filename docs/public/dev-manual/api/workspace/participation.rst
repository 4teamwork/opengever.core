.. _participation:

Teamraum Beteiligungen
======================

Der ``@participations`` Endpoint behandelt Teamraum Beteiligungen.

Eine Beteiligung an einem Teamraum bedeutet, dass ein bestimmter Benutzer oder
eine bestimmte Gruppe zugriff auf einen Teaumraum hat. Je nach Beteiligung hat der Benutzer andere Berechtigungen.

Es gibt folgende Beteiligungsrollen:

- WorkspaceAdmin
- WorkspaceMember
- WorkspaceGuest

Diese Endpoints liefern zur Zeit sowohl ``participant`` als auch ``participant_actor`` zurück. ``participant`` wird in einer späteren Version jedoch nicht mehr unterstützt werden, und wird durch ``participant_actor`` abgelöst.


Beteiligungen abrufen:
----------------------
Ein GET Request gibt die Beteiligungen sowie die aktiven Einladungen eines Inhalts zurück.

**Beispiel-Request**:

   .. sourcecode:: http

       GET /workspace-1/@participations HTTP/1.1
       Accept: application/json

**Beispiel-Response**:


   .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "items": [
        {
          "@id": "http://localhost:8080/fd/workspaces/workspace-1/@participations/max.muster",
          "@type": "virtual.participations.user",
          "is_editable": true,
          "role": {
            "title": "Admin",
            "token": "WorkspaceAdmin"
          },
          "participant_actor": {
            "@id": "http://localhost:8081/fd/@actors/max.muster",
            "identifier": "max.muster",
          },
          "participant": {
            "@id": "http://localhost:8081/fd/@ogds-users/max.muster",
            "@type": "virtual.ogds.user",
            "active": true,
            "email": "max.muster@example.com",
            "title": "Max Muster (max.muster)",
            "id": "max.muster",
            "is_local": null
          },
        },
        {
          "@id": "http://localhost:8081/fd/workspaces/workspace-41/@participations/afi_benutzer",
          "@type": "virtual.participations.group",
          "is_editable": true,
          "participant_actor": {
            "@id": "http://localhost:8081/fd/@actors/afi_benutzer",
            "identifier": "afi_benutzer",
          },
          "participant": {
            "@id": "http://localhost:8081/fd/@ogds-groups/afi_benutzer",
            "@type": "virtual.ogds.group",
            "active": true,
            "id": "afi_benutzer",
            "is_local": true,
            "title": "AFI Benutzer",
            "email": null
          },
          "role": {
            "title": "Admin",
            "token": "WorkspaceAdmin"
          }
        }
      ]
    }


Eine einzelne Beteiligung abrufen:
----------------------------------
Ein GET Request auf die jeweilige Resource gibt die Beteiligungen oder die Einladungen eines Inhalts zurück.

**Beispiel-Request**:

   .. sourcecode:: http

       GET /workspaces/workspace-1/@participations/users/max.muster HTTP/1.1
       Accept: application/json

**Beispiel-Response**:


   .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": "http://localhost:8080/fd/workspaces/workspace-1/@participations/max.muster",
      "@type": "virtual.participations.user",
      "is_editable": true,
      "role": {
        "title": "Admin",
        "token": "WorkspaceAdmin"
      },
      "participant_actor": {
        "@id": "http://localhost:8081/fd/@actors/max.muster",
        "identifier": "max.muster",
      },
      "participant": {
        "@id": "http://localhost:8081/fd/@ogds-users/max.muster",
        "@type": "virtual.ogds.user",
        "active": true,
        "email": "max.muster@example.com",
        "title": "Max Muster (max.muster)",
        "id": "max.muster",
        "is_local": null
    }


Beteiligungen löschen:
----------------------
Ein DELETE Request auf die `@id` einer Beteiligung löscht die entsprechnede Beteilungung.

**Beispiel-Request**:

   .. sourcecode:: http

       DELETE /workspace-1/@participations/max.muster HTTP/1.1
       Accept: application/json


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content


Beteiligungen hinzufügen:
-------------------------
In einem selbst verwalteten Teamraum-Ordner (Vererbung wurde unterbrochen) können beteiligungen über einen POST request auf den @participations Endpoint hinzugefügt werden.

**Achtung**: Eine Beteiligung in einem Arbeitsraum kann nur über eine Einladung hinzugefügt werden. Der eingeladene Benutzer muss seine Beteiligung erste bestätigen, bevor der Benutzer effektiv berechtigt wird.

**Beispiel-Request**:

   .. sourcecode:: http

       POST /workspaces/workspace-1/folder-1/@participations HTTP/1.1
       Accept: application/json

       {
         "participant": "maria.meier",
         "role": "WorkspaceAdmin"
       }

**Beispiel-Response**:

   .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": "http://localhost:8080/fd/workspaces/workspace-1/@participations/max.muster",
      "@type": "virtual.participations.user",
      "is_editable": true,
      "role": {
        "title": "Admin",
        "token": "WorkspaceAdmin"
      },
      "participant_actor": {
        "@id": "http://localhost:8081/fd/@actors/maria.meier",
        "identifier": "maria.meier",
      },
      "participant": {
        "@id": "http://localhost:8081/fd/@ogds-users/maria.meier",
        "@type": "virtual.ogds.user",
        "active": true,
        "email": "maria.meier@example.com",
        "title": "Maria Meier (maria.meier)",
        "id": "maria.meier",
        "is_local": null
    }


Beteiligungen bearbeiten:
-------------------------
Beteiligungen können über einen PATCH request auf die jeweilige Ressourece geändert werden.

**Beispiel-Request**:

  .. sourcecode:: http

    PATCH /workspaces/workspace-1/@participations/max.muster HTTP/1.1
    Accept: application/json

    {
      "role": "WorkspaceAdmin"
    }

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content
