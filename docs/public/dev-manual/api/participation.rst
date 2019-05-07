.. _participation:

Teamraum Beteiligungen
======================

Der ``@participations`` Endpoint behandelt Teamraum Beteiligungen.


Beteiligungen abrufen:
----------------------
Ein GET Request gibt die Beteiligungen sowie die aktiven Einladungen eines Inhalts zurück.

Zusätzlich werden alle verfügbaren Rollen im Attribut "roles" zurückgegeben. Dies erleichtert die Darstellung und Verwaltung von Rollen.

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
          "@id": "http://localhost:8080/fd/workspaces/workspace-1/@participations/users/max.muster",
          "@type": "virtual.participations.user",
          "inviter_fullname": null,
          "is_editable": false,
          "participant_fullname": "Max Muster (max.muster)",
          "readable_role": "Federführung",
          "role": "WorkspaceOwner",
          "token": "max.muster",
          "participation_type": "user",
          "readable_participation_type": "User",
        },
        {
          "@id": "http://localhost:8080/fd/workspaces/workspace-1/@participations/invitations/3a8bfcb1b6294edfb60e2a43717fc300",
          "@type": "virtual.participations.invitation",
          "inviter_fullname": "Max Muster (max.muster)",
          "is_editable": true,
          "participant_fullname": "Petra Fröhlich (petra.frohlich)",
          "readable_role": "Gast",
          "role": "WorkspaceGuest",
          "token": "3a8bfcb1b6294edfb60e2a43717fc300",
          "participation_type": "invitation",
          "readable_participation_type": "Invitation",
        }
      ],
      "roles": [
        {
          "id": "WorkspaceOwner",
          "managed": false,
          "title": "Federführung"
        },
        {
          "id": "WorkspaceAdmin",
          "managed": true,
          "title": "Admin"
        },
        {
          "id": "WorkspaceMember",
          "managed": true,
          "title": "Teammitglied"
        },
        {
          "id": "WorkspaceGuest",
          "managed": true,
          "title": "Gast"
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
      "@id": "http://localhost:8080/fd/workspaces/workspace-1/@participations/users/max.muster",
      "@type": "virtual.participations.user",
      "inviter_fullname": null,
      "is_editable": false,
      "participant_fullname": "Max Muster (max.muster)",
      "readable_role": "Federführung",
      "role": "WorkspaceOwner",
      "token": "max.muster",
      "participation_type": "user",
      "readable_participation_type": "User",
    }


Beteiligungen löschen:
----------------------
Ein DELETE Request auf die `@id` einer Beteiligung löscht die entsprechnede Beteilungung oder Einladung.

Die URL setzt sich dabei folgendermassen zusammen:
``gever-url/workspaces/workspace/@participations/{participation_type}/{token}``

**Beispiel-Request**:

   .. sourcecode:: http

       DELETE /workspace-1/@participations/invitations/3a8bfcb1b6294edfb60e2a43717fc300 HTTP/1.1
       Accept: application/json


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content


Beteiligungen hinzufügen (Benutzer einladen):
---------------------------------------------
Eine Beteiligung kann nur über eine Einladung hinzugefügt werden. Der eingeladene Benutzer muss seine Beteiligung erste bestätigen, bevor der Benutzer effektiv berechtigt wird.

Eine Einladung wird durch einen POST request auf den `@participation/invitations` Endpoint erstellt.


**Parameter:**

Pflicht:

``userid``: ``String``
   ID des Benutzers, welcher eingeladen werden soll

``role``: ``String``
   Eine Arbeitsraum-Rolle

**Beispiel-Request**:

   .. sourcecode:: http

       POST /workspaces/workspace-1/@participations/invitations/ HTTP/1.1
       Accept: application/json

       {
         "userid": "maria.meier",
         "role": "WorkspaceMember",
       }

**Beispiel-Response**:

   .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
          "@id": "http://localhost:8080/fd/workspaces/workspace-1/@participations/invitations/3a8bfcb1b6294edfb60e2a43717fc301",
          "@type": "virtual.participations.invitation",
          "inviter_fullname": "Max Muster (max.muster)",
          "is_editable": true,
          "participant_fullname": "Maria Meier (maria.meier)",
          "readable_role": "Teammitglied",
          "role": "WorkspaceMember",
          "token": "3a8bfcb1b6294edfb60e2a43717fc301",
          "participation_type": "invitation",
          "readable_participation_type": "Invitation",
    }


Beteiligungen bearbeiten:
-------------------------
Sowohl Beteiligungen wie auch Einladungen können über einen PATCH request auf die jeweilige Ressourece geändert werden.

**Parameter:**

Pflicht:

``role``: ``String``
   Eine Arbeitsraum-Rolle

**Beispiel-Request**:

   .. sourcecode:: http

       POST /workspaces/workspace-1/@participations/invitations/3a8bfcb1b6294edfb60e2a43717fc301 HTTP/1.1
       Accept: application/json

       {
         "role": "WorkspaceAdmin",
       }

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content
