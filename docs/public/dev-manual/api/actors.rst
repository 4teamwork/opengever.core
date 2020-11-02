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
        "actor_type": "user",
        "identifier": "peter.mueller",
        "label": "Mueller Peter",
        "portrait_url": "http://example.org/defaultUser.png"
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
            "actor_type": "user",
            "identifier": "peter.mueller",
            "label": "Mueller Peter",
            "portrait_url": "http://example.org/defaultUser.png"
          },
          {
            "@id": "http://example.org/@actors/inbox:fa",
            "actor_type": "inbox",
            "identifier": "inbox:afi",
            "label": "Eingangskorb",
            "portrait_url": null
          },
          { "...": "..." }
        ]
      }
