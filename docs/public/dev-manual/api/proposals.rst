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
