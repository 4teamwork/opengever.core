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
        "absent": false,
        "absent_from": null,
        "absent_to": null,
        "active": true,
        "address1": null,
        "...": "...",
        "groups": [
            {
                "@id": "http://example.org/fd/kontakte/@ogds-groups/afi_benutzer",
                "@type": "virtual.ogds.group",
                "active": true,
                "groupid": "afi_benutzer",
                "groupname": "afi_benutzer",
                "title": null
            },
            {"...": "..."}
        ],
        "last_login": "2020-05-03",
        "teams": [
            {
                "@id": "http://example.org/fd/@teams/90",
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

GET
---

Team-Daten werden mit dem ``@teams`` Endpoint abgefragt. Dieser Endpoint erwartet als Pfad-Argument die ID des Teams und wird auf Stufe PloneSite abgefragt. Die URL setzt sich somit folgendermassen zusammen:

``http://example.org/fd/@teams/90``

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
        "@id": "http://localhost:8080/fd/@teams/90",
        "@type": "virtual.ogds.team",
        "active": true,
        "groupid": "afi_benutzer",
        "group": {
            "@id": "http://localhost:8080/fd/@ogds-groups/afi_benutzer",
            "@type": "virtual.ogds.group",
            "active": true,
            "groupid": "afi_benutzer",
            "groupname": "afi_benutzer",
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


POST
----

Die Erstellung eines Teams erfolgt mit einem POST Request auf den ``@teams`` Endpoint.

**Beispiel-Request**:

   .. sourcecode:: http

      POST /@teams HTTP/1.1
      Accept: application/json

      {
        "active": true,
        "groupid": {"token": "projekt_a", "title": "Projekt A"},
        "org_unit_id": {"token": "fa", "title": "Finanzamt"},
        "title": "Team A"
      }

**Beispiel-Response**:


   .. sourcecode:: http

      HTTP/1.1 201 OK
      Content-Type: application/json

      {
        "@id": "http://localhost:8080/fd/@teams/90",
        "@type": "virtual.ogds.team",
        "active": true,
        "groupid": "projekt_a",
        "group": {
            "@id": "http://localhost:8080/fd/@ogds-groups/projekt_a",
            "@type": "virtual.ogds.group",
            "active": true,
            "groupid": "projekt_a",
            "groupname": "projekt_a",
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
        "org_unit_id": "fa",
        "org_unit_title": "Finanzamt",
        "team_id": 90,
        "title": "Projekt A"
      }


PATCH
-----

Auch die Bearbeitung eines Teams ist via API möglich. Hierfür muss ein PATCH Request auf den ``@teams`` Endpoint abgesetzt werden. Dabei wird, wie beim GET Endpoint, als Pfad-Argument die ID des Teams erwartet.

**Beispiel-Request**:

   .. sourcecode:: http

      PATCH /@teams/90 HTTP/1.1
      Accept: application/json

      {
        "active": false
      }

**Beispiel-Response**:


   .. sourcecode:: http

      HTTP/1.1 201 OK
      Content-Type: application/json

      {
        "@id": "http://localhost:8080/fd/@teams/90",
        "@type": "virtual.ogds.team",
        "active": false,
        "groupid": "projekt_a",
        "group": {
            "@id": "http://localhost:8080/fd/@ogds-groups/projekt_a",
            "@type": "virtual.ogds.group",
            "active": true,
            "groupid": "projekt_a",
            "groupname": "projekt_a",
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
        "org_unit_id": "fa",
        "org_unit_title": "Finanzamt",
        "team_id": 90,
        "title": "Projekt A"
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
        "groupname": "stv_benutzer",
        "groupurl": "http://example.org/@groups/stv_benutzer"
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

Plone-Gruppen
-------------
Falls mehr Informationen für eine Gruppe benötigt werden, kann ein Request auf die Plone-Gruppe über den ``@groups`` Endpoint gemacht werden. Dies ist weniger performant als ein Request auf den ``@ogds-groups`` Endpoint, bietet dafür mehr Informationen. Eine serialisierte OGDS-Gruppe enthält ein Attribut ``groupurl`` welches auf die Plone-Ressource zeigt.

Die generelle Verwendung des Endpoints ist in der `plone.restapi Dokumentation <https://plonerestapi.readthedocs.io/en/latest/groups.html>`_ beschrieben. Dieser Endpoint wurde für GEVER folgendermassen angepasst:

- Serialisierte Gruppendaten enthalten einen `@type`
- die Benutzer in den Gruppendaten werden als korrekte Ressource serialisiert

Die neue Antwort einer Gruppe sieht wie folgt aus:


**Beispiel-Request**:

   .. sourcecode:: http

      GET /@groups/stv_benutzer HTTP/1.1
      Accept: application/json


**Beispiel-Response**:


   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@id": "http://example.org/@groups/stv_benutzer",
        "@type": "virtual.plone.group",
        "description": "",
        "email": "",
        "groupname": "STV Benutzer",
        "id": "stv_benutzer",
        "roles": [
          "Authenticated"
        ],
        "title": "",
        "users": {
          "@id": "http://example.org/@groups/stv_benutzer",
          "items": [
            {
              "@id": "http://example.org/@users/muster.max",
              "@type": "virtual.plone.user",
              "title": "Max Muster (muster.max)",
              "token": "muster.max"
            },
            {"...": "..."}
          ],
          "items_total": 11
        }
      }


Gruppen erstellen, löschen und modifizieren
-------------------------------------------

Gruppen erstellen, modifizieren und löschen kann über den ``@groups`` Endpoint gemacht werden und ist in der `plone.restapi Dokumentation <https://plonerestapi.readthedocs.io/en/latest/groups.html>`_ beschrieben. Dieser Endpoint wurde für GEVER folgendermassen angepasst:

- Die Gruppen Daten werden korrekt im OGDS abgespiegelt.
- Er steht auch für Administratoren zur Verfügung.
- Er wurde eingeschränkt um nur die Administration von gewissen Rollen zu erlauben: ``workspace_guest``, ``workspace_member`` und ``workspace_admin``.
- Gruppennamen darf nicht länger als 255 Zeichen lang sein

.. _reactivate-local-group:

Lokale Gruppen reaktivieren
---------------------------

Mit dem ``@reactivate-local-group`` Endpoint kann eine lokale, inaktive Gruppe wieder aktiviert werden. Der Endpoint steht auf Stufe PloneSite zur Verfügung.

**Beispiel-Request**:

   .. sourcecode:: http

      POST /@reactivate-local-group HTTP/1.1
      Accept: application/json

      {
        "groupname": "test-group"
      }


**Beispiel-Response**:


   .. sourcecode:: http

      HTTP/1.1 204 No content
      Content-Type: application/json


KuB Kontakte
============

Mit dem ``@kub`` Endpoint können Kontakte aus dem KuB geholt werden. Der Endpoint steht nur auf Stufe PloneSiteRoot zur Verfügung und erwartet als Pfad Parameter die UID des Kontaktes:


**Beispiel-Request**:

   .. sourcecode:: http

      GET /@kub/person:1234abdc HTTP/1.1
      Accept: application/json

**Beispiel-Response**:


   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "addresses": [],
        "canton": null,
        "country": "",
        "countryIdISO2": "",
        "created": "2021-11-14T00:00:00+01:00",
        "dateOfBirth": null,
        "description": "",
        "emailAddresses": [],
        "firstName": "Julie",
        "fullName": "Dupont Julie",
        "id": "0e623708-2d0d-436a-82c6-c1a9c27b65dc",
        "languageOfCorrespondance": "fr",
        "maritalStatus": 2,
        "memberships": [],
        "modified": "2021-11-14T00:00:00+01:00",
        "officialName": "Dupont",
        "organizations": [],
        "originName": "Paris",
        "phoneNumbers": [],
        "primaryEmail": null,
        "primaryPhoneNumber": null,
        "salutation": "Frau",
        "sex": 2,
        "status": 1,
        "tags": [],
        "thirdPartyId": null,
        "title": "",
        "urls": []
      }
