.. _users:

Benutzer
========

Benutzer-Daten werden mit dem ``@ogds-users`` Endpoint abgefragt. Dieser Endpoint unterstützt nur das GET und erwartet als Pfad-Argument die ID des Benutzers und wird auf dem Kontaktordner abgefragt. Die URL setzt sich somit folgendermassen zusammen:

``http://example.org/fd/kontakte/@ogds-users/peter.mueller``

Ein Benutzer wird lediglich durch einen Eintrag in der SQL Datenbank repräsentiert und ist kein Plone Inhaltstyp. Deshalb beinhaltet die Response weniger Informationen als für andere Inhaltstypen.

**Beispiel-Request**:

   .. sourcecode:: http

      GET /@ogds-users/peter.mueller HTTP/1.1
      Accept: application/json

**Beispiel-Response**:


   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@id": "http://example.org/fd/kontakte/@ogds-users/peter.mueller",
        "@type": "virtual.ogds.user",
        "active": true,
        "address1": null,
        "...": "...",
        "groups": [
            {
                "@id": "http://example.org/fd/kontakte/@ogds-groups/afi_benutzer",
                "@type": "virtual.ogds.group",
                "active": true,
                "groupid": "afi_benutzer",
                "title": null
            },
            {"...": "..."}
        ],
        "last_login": "2020-05-03",
        "teams": [
            {
                "@id": "http://example.org/fd/kontakte/@teams/90",
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

Das Attribut `last_login` ist nur für Administratoren und Manager sichtbar.


Teams
=====

Team-Daten werden mit dem ``@teams`` Endpoint abgefragt. Dieser Endpoint unterstützt nur das GET und erwartet als Pfad-Argument die ID des Teams und wird auf dem Kontaktordner abgefragt. Die URL setzt sich somit folgendermassen zusammen:

``http://example.org/fd/kontakte/@teams/90``

Ein Team wird lediglich durch einen Eintrag in der SQL Datenbank repräsentiert und ist kein Plone Inhaltstyp. Deshalb beinhaltet die Response weniger Information als für andere Inhaltstypen. Dieser Endpoint unterstützt Batching. Die Teammitglieder werden nach Nachnamen
sortiert zurückgegeben.

**Beispiel-Request**:

   .. sourcecode:: http

      GET /@teams/a-team HTTP/1.1
      Accept: application/json

**Beispiel-Response**:


   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@id": "http://localhost:8080/fd/kontakte/@teams/90",
        "@type": "virtual.ogds.team",
        "active": true,
        "groupid": "afi_benutzer",
        "group": {
            "@id": "http://localhost:8080/fd/kontakte/@ogds-groups/admin-group",
            "@type": "virtual.ogds.group",
            "active": true,
            "groupid": "admin-group",
            "title": null
        },
        "items": [
            {
                "@id": "http://localhost:8080/fd/kontakte/@ogds-users/peter.mueller",
                "@type": "virtual.ogds.user",
                "active": true,
                "...": "..."
            },
            {"...": "..."}
        ],
        "items_total": 14,
        "org_unit_id": "fd",
        "org_unit_title": "Finanzdepartement",
        "team_id": 90,
        "title": "afi_benutzer"
      }


Gruppen
=======

Gruppendetails
--------------

Details über Gruppen können mit dem ``@ogds-groups`` Endpoint abgefragt werden. Der Endpoint steht nur auf Stufe Kontaktordner zur Verfügung und erwartet eine Einschränkung auf eine Gruppe via Gruppen-ID. Die URL setzt sich somit folgendermassen zusammen:

``http://example.org/kontakte/@ogds-groups/stv_benutzer``

Dieser Endpoint unterstützt Batching. Die Gruppenmitglieder werden nach
Nachnamen sortiert zurückgegeben.


**Beispiel-Request**:

   .. sourcecode:: http

      GET /@ogds-groups/stv_benutzer HTTP/1.1
      Accept: application/json


**Beispiel-Response**:


   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@id": "http://example.org/kontakte/@ogds-groups/stv_benutzer",
        "@type": "virtual.ogds.group",
        "active": true,
        "groupid": "stv_benutzer",
        "title": "stv_benutzer",
        "items": [
            {
                "@id": "http://localhost:8080/fd/kontakte/@ogds-user/peter.mueller",
                "@type": "virtual.ogds.user",
                "active": true,
                "...": "..."
            },
            {"...": "..."}
        ],
        "items_total": 11
      }

Gruppen erstellen, löschen und modifizieren
-------------------------------------------

Gruppen erstellen, modifizieren und löschen kann über den ``@groups`` Endpoint gemacht werden und ist in der `plone.restapi Dokumentation <https://plonerestapi.readthedocs.io/en/latest/groups.html>`_ beschrieben. Dieser Endpoint wurde für GEVER folgendermassen angepasst:

- Die Gruppen Daten werden korrekt im OGDS abgespiegelt.
- Er steht auch für Administratoren zur Verfügung.
- Er wurde eingeschränkt um nur die Administration von gewissen Rollen zu erlauben: ``workspace_guest``, ``workspace_member`` und ``workspace_admin``.
- Gruppennamen darf nicht länger als 255 Zeichen lang sein
