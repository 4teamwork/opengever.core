Anträge
=======

Auch Anträge können via REST API bedient werden. Die Erstellung eines Antrags erfolgt wie bei anderen Inhalten (siehe Kapitel :ref:`operations`) via POST request. Man muss entweder ``proposal_template`` oder ``proposal_document`` und ``"proposal_document_type": "existing"`` spezifizieren (``proposal_template`` und ``proposal_document`` als ``UUID``):


**Beispiel-Request mit `proposal_template`**:

   .. sourcecode:: http

      POST /(container) HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "@type": "opengever.meeting.proposal",
        "title": "Antrag für Kreiselbau",
        "committee_oguid": "fd:1722088772",
        "issuer": "john.doe",
        "proposal_template": "c6df8eb485a448ef861caf97198e1dae"
      }


**Beispiel-Request mit `proposal_document`**:

   .. sourcecode:: http

      POST /(container) HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "@type": "opengever.meeting.proposal",
        "title": "Antrag für Kreiselbau",
        "committee_oguid": "fd:1722088772",
        "issuer": "john.doe",
        "proposal_document":"a7f51d19d31141ac84bd368d44d17f05",
        "proposal_document_type": "existing"
      }

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Accept: application/json

      {
        "@id": "http://example.org/ordnungssystem/fuehrung/dossier-1/proposal-5",
        "@type": "opengever.meeting.proposal",
        "committee_oguid": {
          "title": "Kommission für Rechtsfragen",
          "token": "fd:1722088772"
        },
        "committee": {
          "@id": "http://example.org/sitzungen/committee-1",
          "title": "Kommission für Rechtsfragen"
        },
        "issuer": {
          "title": "Boss Hugo (hugo.boss)",
          "token": "hugo.boss"
        },
        "...": "..."
      }


Antragverlauf
-------------
Der Verlauf eines Antrags ist in der GET Repräsentation eines Antrags unter dem Attribut ``responses`` enthalten.


**Beispiel-Respones auf ein GET Request**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Accept: application/json

      {
        "@id": "http://example.org/ordnungssystem/fuehrung/dossier-1/proposal-5",
        "@type": "opengever.meeting.proposal",
        "UID": "3a551f6e3b62421da029dfceb71656e6",
        "oguid": "fd:12345",
        "items": [],
        "responses": [
          {
            "@id": "http://example.org/ordnungssystem/fuehrung/dossier-1/proposal-5/@responses/1569394746972113",
            "response_id": 1569394746972113,
            "response_type": "successor_created",
            "additional_data": {
                "successor_oguid": "fd:593382572"
            },
            "changes": [],
            "creator": {
                "title": "hugo.boss",
                "token": "hugo.boss"
            },
            "created": "2019-05-21T13:57:42",
            "modified": null,
            "modifier": null,
            "text": "",
          },
          {
            "@id": "http://example.org/ordnungssystem/fuehrung/dossier-1/proposal-5/@responses/1573486804000000",
            "response_id": 1573486804000000
            "response_type": "commented"
            "additional_data": [],
            "changes": [],
            "creator": {
                "title": "hugo.boss",
                "token": "hugo.boss"
            },
            "created": "2019-11-11T16:40:04",
            "modified": "2020-05-21T13:57:42",
            "modifier": "kathi.barfuss",
            "text": "Suspendisse faucibus, nunc et pellentesque egestas.",
          },
        ]
        "review_state": "proposal-state-submitted",
        "...": "...",
      }

.. _submit-additional-documents:

Zusätzliche Beilagen einreichen
-------------------------------

Nach dem einreichen eines Antrags können mit dem ``@submit-additional-documents`` zusätzliche Beilagen oder eine neue Version von einer existierender Beilage eingereicht werden. Als Body wird eine Liste von Dokumente (UID) im Attribut ``documents`` erwartet.

**Beispiel-Request**:

   .. sourcecode:: http

       POST dossier-1/proposal-1/@submit-additional-documents HTTP/1.1
       Accept: application/json

       {
        "documents": ["00040acaba70487a98d15b832cc1f99a", "001dbd36feec4df1a106047d3fa884b4"]
       }

Die Response ist eine Liste die für jede Beilage die folgenden Informationen zurückliefert:
``source``: URL der Beilage
``action``: "copied" wenn es sich um eine neu Beilage die in den eingereichten Antrag kopiert wurde, "udapted" wenn eine neue Version der Beilage erstellt wurde oder "null" wenn diese Beilage bereits in dieser Version eingereicht wurde.

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
          {
              "action": "copied",
              "source": "dossier-1/proposal-1/document-75"
          },
          {
              "action": null,
              "source": "dossier-1/proposal-1/document-76"
          }
      ]


Protokollauszug im Antragsdossier ablegen
=========================================

Mit dem ``@ris-return-excerpt`` Endpoint können Protokollauszüge aus der SPV
ins Antragsdossier eingereicht werden. Der Endpoint erwartet als Pfad Parameter:

- Mandant ID
- relative Dossierpfad


**Beispiel-Request**:

   .. sourcecode:: http

      POST ordnungssystem/dossier-1/document-1/@ris-return-excerpt HTTP/1.1
      Accept: application/json

      {
        "target_admin_unit_id": "fd",
        "target_dossier_relative_path": "ordnungssystem/dossier-1"
      }

**Beispiel-Response**:


   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "path": "ordnungssystem/dossier-2/document-2",
        "intid": 3,
        "url": "http://gever.onegovgever.ch/fd/ordnungssystem/dossier-2/document-2",
        "current_version_id": 1,
      }


Protokollauszug im Antragsdossier aktualisieren
===============================================

Mit dem ``@ris-update-excerpt`` Endpoint können Protokollauszüge aus der SPV
im Antragsdossier aktualisiert werden. Der Endpoint erwartet als Pfad Parameter:

- Mandant ID
- relative Dokumentpfad vom Protokollauszug


**Beispiel-Request**:

   .. sourcecode:: http

      POST ordnungssystem/dossier-1/document-1/@ris-update-excerpt HTTP/1.1
      Accept: application/json

      {
        "target_admin_unit_id": "fd",
        "target_document_relative_path": "ordnungssystem/dossier-1/document-1"
      }

**Beispiel-Response**:


   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "path": "ordnungssystem/dossier-2/document-2",
        "intid": 3,
        "url": "http://gever.onegovgever.ch/fd/ordnungssystem/dossier-2/document-2",
        "current_version_id": 1,
      }
