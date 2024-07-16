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
        "root_item": {"...": "..."},
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
            "root_item": {"...": "..."},
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
            "root_item": {"...": "..."},
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


Dossier-Transfer-Inhalt abrufen
-------------------------------

Mit einem GET Request auf ``/@dossier-transfers/<id>?full_content=1`` kann
zusätzlich zu den Metadaten eines Dossier-Transfers eine Serialisierung des
Inhalts des Transfers abgerufen werden.

Dieser serialisierte Inhalt wird in einem zusätzlichen key ``content``
zurückgegeben:

**Beispiel-Request**:

   .. sourcecode:: http

       GET /@dossier-transfers/42?full_content=1 HTTP/1.1
       Accept: application/json


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
          "@id": "http://localhost:8080/fd/@dossier-transfers/4",
          "...": "...",
          "content": {
              "contacts": {
                  "person:39c2789d-a123-44ba-a3b1-4323d6e941c6": {
                      "id": "39c2789d-a123-44ba-a3b1-4323d6e941c6",
                      "firstName": "John",
                      "fullName": "John Doe",
                      "...": "..."
                  }
              },
              "documents": [
                  {
                      "@id": "http://localhost:8080/fd/dossier-20/dossier-21/document-44",
                      "@type": "opengever.document.document",
                      "UID": "a663689540a34538b6f408d4b41baee8",
                      "...": "..."
                  }
              ],
              "dossiers": [
                  {
                      "@id": "http://localhost:8080/fd/dossier-20",
                      "@type": "opengever.dossier.businesscasedossier",
                      "UID": "1b6d8dbf1f954bbb9510a1b65d51ede5",
                      "...": "...",
                      "participations": [
                          [
                              "person:39c2789d-a123-44ba-a3b1-4323d6e941c6",
                              ["final-drawing", "regard"]
                          ]
                      ]
                  },
                  {
                      "@id": "http://localhost:8080/fd/dossier-20/dossier-21",
                      "@type": "opengever.dossier.businesscasedossier",
                      "UID": "f510a6bb410f40258b53090bf2f0c545",
                      "...": "..."
                  }
              ]
          },
          "...": "..."
      }


Blobs von Dossier-Transfers herunterladen
-----------------------------------------

Mit einem GET Request auf ``/@dossier-transfers/<transfer-id>/blob/<document-uid>``
kann das Blob eines Dokuments heruntergeladen werden. Der Request muss dazu einem
gültigen Token für diesen Transfer authentisiert werden, und das Dokument muss
in diesem Transfer enthalten sein.


Dossier-Transfer durchführen
----------------------------

Mit dem ``/@perform-dossier-transfer`` Endpoint kann ein vorher erstellter
Dossier-Transfer durchgeführt werden. Dabei wird das entsprechende Dossier mit
seinen Subdossiers, Dokumenten und Beteiligungen auf dem Zielmandant
in der aufgerufenen Ordnungsposition erstellt.

Im Body muss die Id des Transfers mitgegeben werden.

**Beispiel-Request**:

   .. sourcecode:: http

       POST /ordnungssystem/fuehrung/@perform-dossier-transfer HTTP/1.1
       Accept: application/json
       Content-Type: application/json

       {
         "transfer_id": 42
       }

Als Antwort wird die Serialisierung des erstellten Dossiers zurückgegeben.

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
        "@id": "http://localhost:8080/fd/fuehrung/dossier-31",
        "@type": "opengever.dossier.businesscasedossier",
        "...": "..."
      }
