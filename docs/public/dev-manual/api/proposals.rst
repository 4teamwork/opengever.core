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
            "text": "Suspendisse faucibus, nunc et pellentesque egestas.",
          },
        ]
        "review_state": "proposal-state-submitted",
        "...": "...",
      }

