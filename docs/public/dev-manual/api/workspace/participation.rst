.. _participation:

Teamraum Beteiligungen
======================

Der ``@participations`` Endpoint behandelt Teamraum Beteiligungen.


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
          "participant_email": "max.muster@example.org",
          "participant_fullname": "Max Muster (max.muster)",
          "role": {
            "title": "Admin",
            "token": "WorkspaceAdmin"
          },
          "token": "max.muster"
        },
        {
          "@id": "http://localhost:8080/fd/workspaces/workspace-1/@participations/petra.frohlich",
          "@type": "virtual.participations.user",
          "is_editable": true,
          "participant_email": "petra.frohlich@example.org",
          "participant_fullname": "Petra Fröhlich (petra.frohlich)",
          "role": {
            "title": "Teammitglied",
            "token": "WorkspaceMember"
          },
          "token": "petra.frohlich"
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
      "participant_email": "max.muster@example.org",
      "participant_fullname": "Max Muster (max.muster)",
      "role": {
        "title": "Admin",
        "token": "WorkspaceAdmin"
      },
      "token": "max.muster"
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
         "token": "maria.meier",
         "role": "WorkspaceMember",
       }

**Beispiel-Response**:

   .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": "http://localhost:8080/fd/workspaces/workspace-1/@participations/max.muster",
      "@type": "virtual.participations.user",
      "is_editable": true,
      "participant_email": "max.muster@example.org",
      "participant_fullname": "Max Muster (max.muster)",
      "role": {
        "title": "Admin",
        "token": "WorkspaceMember"
      },
      "token": "max.muster"
    }


Beteiligungen bearbeiten:
-------------------------
Beteiligungen können über einen PATCH request auf die jeweilige Ressourece geändert werden.

**Beispiel-Request**:

  .. sourcecode:: http

    PATCH /workspaces/workspace-1/@participations/max.muster HTTP/1.1
    Accept: application/json

    {
      "role": { "token": "WorkspaceAdmin" }
    }

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content
