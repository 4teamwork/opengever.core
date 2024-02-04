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
