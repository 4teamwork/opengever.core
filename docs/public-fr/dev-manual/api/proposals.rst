Requêtes
========

Les requêtes peuvent également être desservies  par l'API REST. La création d'une requête se déroule comme pour les autres contenus (voir chapitre :ref:`operations`), par l'intermédiaire d'une Request POST. Il faut toutefois s'assurer d'avoir défini soit ``proposal_template`` ou ``proposal_document`` et ``"proposal_document_type": "existing"``  (``proposal_template`` et ``proposal_document`` en tant qu' ``UUID``):


**Exemple de Request avec `proposal_template`**:

   .. sourcecode:: http

      POST /(container) HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "@type": "opengever.meeting.proposal",
        "title": "Requête pour la construction d'un giratoire",
        "committee_oguid": "fd:1722088772",
        "issuer": "john.doe",
        "proposal_template": "c6df8eb485a448ef861caf97198e1dae"
      }


**Exemple de Request avec `proposal_document`**:

   .. sourcecode:: http

      POST /(container) HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "@type": "opengever.meeting.proposal",
        "title": "Requête pour la construction d'un giratoire",
        "committee_oguid": "fd:1722088772",
        "issuer": "john.doe",
        "proposal_document":"a7f51d19d31141ac84bd368d44d17f05",
        "proposal_document_type": "existing"
      }

**Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Accept: application/json

      {
        "@id": "http://example.org/ordnungssystem/direction/dossier-1/proposal-5",
        "@type": "opengever.meeting.proposal",
        "committee_oguid": {
          "title": "Commission juridique",
          "token": "fd:1722088772"
        },
        "issuer": {
          "title": "Boss Hugo (hugo.boss)",
          "token": "hugo.boss"
        },
        "...": "..."
      }


Déroulement d'une requête
-------------------------
Le déroulement d'une requête est contenu dans sa représentation GET, sous l'attribut ``responses``.


**Exemple de Respones sur une Request GET**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Accept: application/json

      {
        "@id": "http://example.org/ordnungssystem/direction/dossier-1/proposal-5",
        "@type": "opengever.meeting.proposal",
        "UID": "3a551f6e3b62421da029dfceb71656e6",
        "items": [],
        "responses": [
          {
            "@id": "http://example.org/ordnungssystem/direction/dossier-1/proposal-5/@responses/1569394746972113",
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
            "@id": "http://example.org/ordnungssystem/direction/dossier-1/proposal-5/@responses/1573486804000000",
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

