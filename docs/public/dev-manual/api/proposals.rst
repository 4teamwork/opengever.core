Anträge
=======

Auch Anträge können via REST API bedient werden. Die Erstellung eines Antrags erfolgt wie bei anderen Inhalten (siehe Kapitel :ref:`operations`) via POST request:


**Beispiel-Request**:

   .. sourcecode:: http

      POST /(container) HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "@type": "opengever.meeting.proposal",
        "title": "Antrag für Kreiselbau",
        "committee_oguid": "fd:1722088772",
        "issuer": "john.doe",
        "proposal_template": "fd/vorlagen/proposal-template-1"
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
          "title": "Johner Niklaus (niklaus.johner)",
          "token": "niklaus.johner"
        },
        "...": "..."
      }
