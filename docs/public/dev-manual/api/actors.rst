.. _actors:

Actors
======

Ein actor ist eine generische Repräsentation von Benutzer, Gruppen, Teams, Kontakte, Eingangskörbe und Gremien. Actors werden in verschiedenen Endpoints und für gewisse Felder (zum Beispiel Dossier Federführung) verwendet.

Die Daten eines actor können mit dem ``@actors`` Endpoint abgefragt werden. Dieser Endpoint erwartet als Pfad-Argument die actor ID und steht auf Stufe PloneSite zur Verfügung. Die URL setzt sich somit folgendermassen zusammen:

``http://example.org/fd/@actors/peter.mueller``

Ein actor ist kein Plone Inhaltstyp, deshalb beinhaltet die Response weniger Informationen als für andere Inhaltstypen.

**Beispiel-Request**:

   .. sourcecode:: http

      GET /@actors/peter.mueller HTTP/1.1
      Accept: application/json

**Beispiel-Response**:


   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@id": "http://example.org/@actors/peter.mueller",
        "@type": "virtual.ogds.actor",
        "active": true,
        "actor_type": "user",
        "identifier": "peter.mueller",
        "is_absent": true,
        "label": "Mueller Peter",
        "login_name": "peter.mueller",
        "portrait_url": "http://example.org/portraits/peter.mueller.png"
        "representatives": [
           {
               "@id": "http://example.org/@actors/peter.mueller",
               "identifier": "peter.mueller"
           },
        ],
        "represents": {
            "@id": "http://example.org/@actors/peter.mueller"
        }
      }

Mit dem Parameter ``full_representation`` werden im represents-Feld nicht nur eine URL, sondern alle Details des Aktors zurückgegeben.

**Beispiel-Request**:

   .. sourcecode:: http

      GET /@actors?full_representation=true HTTP/1.1
      Accept: application/json


**Beispiel-Response**:


   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@id": "http://example.org/@actors/peter.mueller",
        "...": "",
        "represents": {
            "@id": "http://example.org/@ogds-users/peter.mueller"
            "@type": "virtual.ogds.user",
             "absent": false,
             "active": true,
             "city": "Thun",
             "country": "Schweiz",
             "department": "Finanzdirektion",
             "department_abbr": "fd",
             "email": "peter.mueller@4teamwork.ch",
             "firstname": "Peter",
             "...":"..."
        }
      }


Via POST können die Daten von mehreren actors mit einem Request abgefragt werden. Im Request-body wird die Liste von actor ID angegeben:

**Beispiel-Request**:

   .. sourcecode:: http

      POST /@actors HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "actor_ids": [
          "peter.mueller",
          "inbox:fa",
          "team:90",
          "group:stv_benutzer",
           "..."
        ]
      }

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@id": "http://example.org/@actors",
        "items": [
          {
            "@id": "http://example.org/@actors/peter.mueller",
            "@type": "virtual.ogds.actor",
            "active": true,
            "actor_type": "user",
            "identifier": "peter.mueller",
            "is_absent": false,
            "label": "Mueller Peter",
            "login_name": "peter.mueller",
            "portrait_url": "http://example.org/portraits/peter.mueller.png",
            "representatives": [
               {
                 "@id": "http://example.org/@actors/peter.mueller",
                 "identifier": "peter.mueller"
               },
            ],
            "represents": {
               "@id": "http://example.org/@actors/peter.mueller"
            }
          },
          {
            "@id": "http://example.org/@actors/inbox:fa",
            "@type": "virtual.ogds.actor",
            "active": true,
            "actor_type": "inbox",
            "identifier": "inbox:afi",
            "is_absent": false,
            "label": "Eingangskorb",
            "login_name": "afi_inbox",
            "portrait_url": null,
            "representatives": [
               {
                 "@id": "http://example.org/@actors/peter.mueller",
                 "identifier": "peter.mueller"
               },
            ],
            "represents": {
               "@id": "http://example.org/eingangskorb/eingangskorb_fa"
            }
          },
          { "...": "..." }
        ]
      }
