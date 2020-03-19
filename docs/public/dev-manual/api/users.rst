.. _users:

Benutzer
========

Benutzer Daten werden mit dem ``@ogds-user`` Endpoint abgefragt. Dieser Endpoint unterstützt nur das GET und erwartet als Pfad-Argument die ID des Benutzers und wird auf dem Kontakt Folder abgefragt. Die URL setzt sich somit folgendermassen zusammen:

``http://example.org/fd/kontakte/@ogds-user/peter.mueller``

Ein Benutzer wird lediglich durch einen Eintrag in der SQL Datenbank repräsentiert und ist kein Plone Inhaltstyp. Deshalb beinhaltet die Response weniger Information als für andere Inhaltstypen.

**Beispiel-Request**:

   .. sourcecode:: http

      GET /@ogds-user/peter.mueller HTTP/1.1
      Accept: application/json

**Beispiel-Response**:


   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@id": "http://example.org/fd/kontakte/@ogds-user/peter.mueller",
        "@type": "virtual.ogds.user",
        "active": true,
        "address1": null,
        "...": "...",
        "groups": [
            {
                "@id": "http://example.org/fd/kontakte/@group/afi_benutzer",
                "@type": "virtual.ogds.group",
                "active": true,
                "groupid": "afi_benutzer",
                "title": null
            },
            {"...": "..."}
        ],
        "teams": [
            {
                "@id": "http://example.org/fd/kontakte/@team/90",
                "@type": "virtual.ogds.team",
                "active": true,
                "groupid": "afi_benutzer",
                "org_unit_id": "fd",
                "org_unit_title": "Steuerverwaltung",
                "team_id": 90,
                "title": "afi_benutzer"
            },
            {"...": "..."}
        ],
        "userid": "peter.mueller",
        "zip_code": null
      }


Teams
=====

Team Daten werden mit dem ``@team`` Endpoint abgefragt. Dieser Endpoint unterstützt nur das GET und erwartet als Pfad-Argument die ID des Teams und wird auf dem Kontakt Folder abgefragt. Die URL setzt sich somit folgendermassen zusammen:

``http://example.org/fd/kontakte/@team/90``

Ein Team wird lediglich durch einen Eintrag in der SQL Datenbank repräsentiert und ist kein Plone Inhaltstyp. Deshalb beinhaltet die Response weniger Information als für andere Inhaltstypen.

**Beispiel-Request**:

   .. sourcecode:: http

      GET /@team/a-team HTTP/1.1
      Accept: application/json

**Beispiel-Response**:


   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@id": "http://localhost:8080/fd/kontakte/@team/90",
        "@type": "virtual.ogds.team",
        "active": true,
        "groupid": "afi_benutzer",
        "org_unit_id": "fd",
        "team_id": 90,
        "title": "afi_benutzer",
        "users": [
            {
                "@id": "http://localhost:8080/fd/kontakte/@ogds-user/peter.mueller",
                "@type": "virtual.ogds.user",
                "active": true,
                "...": "..."
            },
            {"...": "..."}
        ]
      }
