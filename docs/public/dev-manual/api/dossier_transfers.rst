.. _dossier_transfers:

Dossier-Transfers
=================

Über den ``@dossier-transfers`` Endpoint können Dossier-Transfers für den
Übertrag von einem Mandanten zu einem anderen erstellt werden.

Dies ist eine interne API, und sie kann nur von GEVER selbst verwendet werden.


Dossier-Transfer erstellen
--------------------------
Mittels eines POST Requests kann ein Dossier-Transfer erstellt werden:


**Beispiel-Request**:

   .. sourcecode:: http

       POST /@dossier-transfers HTTP/1.1
       Accept: application/json

       {
         "title": "Transfer Title",
         "message": "Transfer Message",
         "target": "recipient_admin_unit_id",
         "expires": "2024-02-23T15:45:00+00:00",
         "root": "dossier_uid",
         "documents": [
           "document1_uid",
           "document2_uid"
         ],
         "participations": [
           "participation1_id",
           "participation2_id"
         ],
         "all_documents": false,
         "all_participations": false
       }



**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json
      Location: /@dossier-transfers/1

      {
        "@id": "http://nohost/plone/@dossier-transfers/1",
        "@type": "virtual.ogds.dossiertransfer",
        "id": 1,
        "title": "Transfer Title",
        "message": "Transfer Message",
        "created": "2024-02-18T15:45:00+00:00",
        "expires": "2024-02-23T15:45:00+00:00",
        "state": "pending",
        "source": "plone",
        "target": "recipient",
        "source_user": "regular_user",
        "root": "createresolvabledossier000000001",
        "documents": [
           "document1_uid",
           "document2_uid"
        ],
        "participations": [
           "participation1_id",
           "participation2_id"
        ],
        "all_participations": false,
        "all_documents": false
      }

Dossier-Transfers auflisten
---------------------------
Mittels eines GET Requests können Dossier-Transfers aufgelistet werden:


**Beispiel-Request**:

   .. sourcecode:: http

       GET /@dossier-transfers HTTP/1.1
       Accept: application/json


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@id": "http://nohost/plone/@dossier-transfers",
        "items": [
          {
            "@id": "http://nohost/plone/@dossier-transfers/1",
            "@type": "virtual.ogds.dossiertransfer",
            "id": 1,
            "title": "Transfer Title",
            "message": "Transfer Message",
            "created": "2024-02-18T15:45:00+00:00",
            "expires": "2024-03-19T15:45:00+00:00",
            "state": "pending",
            "source": {
              "token": "plone",
              "title": "Hauptmandant"
            },
            "target": {
              "token": "recipient",
              "title": "Remote Recipient"
            },
            "source_user": "jurgen.konig",
            "root": "createresolvabledossier000000001",
            "documents": [
              "createresolvabledossier000000003"
            ],
            "participations": null,
            "all_documents": false,
            "all_participations": true
          },
          {
            "@id": "http://nohost/plone/@dossier-transfers/2",
            "@type": "virtual.ogds.dossiertransfer",
            "id": 2,
            "title": "Transfer 2",
            "message": "Transfer Message",
            "created": "2024-02-18T15:45:00+00:00",
            "expires": "2024-03-19T15:45:00+00:00",
            "state": "pending",
            "source": {
              "token": "plone",
              "title": "Hauptmandant"
            },
            "target": {
              "token": "recipient",
              "title": "Remote Recipient"
            },
            "source_user": "jurgen.konig",
            "root": "createresolvabledossier000000001",
            "documents": [
              "createresolvabledossier000000003"
            ],
            "participations": [
              "meeting_user"
            ],
            "all_documents": false,
            "all_participations": false
          }
        ]
      }

Über die Query-String Parameter ``direction`` und ``states`` können die
zurückgegebenen Transfers gefiltert werden nach Richtung
(``outgoing`` | ``incoming``) und/oder Zustand (``pending``, ``completed``):

   .. sourcecode:: http

       GET /@dossier-transfers?direction=outgoing HTTP/1.1
       Accept: application/json

   .. sourcecode:: http

       GET /@dossier-transfers?states:list=pending HTTP/1.1
       Accept: application/json


Mit einem GET Request auf ``/@dossier-transfers/<id>`` kann ein einzelner
Dossier-Transfer abgefragt werden.


Dossier-Transfers löschen
-------------------------
Mittels eines DELETE Requests können Dossier-Transfers gelöscht werden:


**Beispiel-Request**:

   .. sourcecode:: http

       DELETE /@dossier-transfers/1 HTTP/1.1
       Accept: application/json


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content
      Content-Type: application/json
