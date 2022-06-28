.. _dispositions:

Aussonderungsangebote
=====================

Auch Aussonderungsangebote können via API gelesen, erstellt und bearbeitet werden. Die API verhält sich dabei gleich wie bei allen anderen Objekten und wie im Kapitel :ref:`operations` beschrieben.

Einzig die Response eines GET Requests bietet unter dem Key ``dossier_details`` eine zusätzliche Zusammenfassung der angehängten Dossiers gruppiert nach Ordnungsposition. Dabei wird auch der Bewertungsentscheid der jeweiligen Dossiers zurück gegeben.


**Auszug ``dossier_details``**:


.. code:: json

    {
       "dossier_details": {
           "active_dossiers": [
               {
                   "@id": "http://example.org/fd/ordnungssystem/bildung",
                   "@type": "opengever.repository.repositoryfolder",
                   "archival_value": {
                       "title": "Nicht geprüft",
                       "token": "unchecked"
                   },
                   "description": "",
                   "dossiers": [
                   {
                       "appraisal": false,
                       "archival_value": {
                           "title": "Nicht geprüft",
                           "token": "unchecked"
                        },
                        "archival_value_annotation": null,
                        "end": "2021-11-23",
                        "former_state": "dossier-state-resolved",
                        "intid": 2053980678,
                        "public_trial": {
                            "title": "Nicht geprüft",
                            "token": "unchecked"
                        },
                        "reference_number": "FD 2 / 1",
                        "start": "2021-11-23",
                        "title": "TEST",
                        "uid": "9604019b72bb4f5096c2efe07d114dcf",
                        "url": "http://example.org/fd/ordnungssystem/bildung/dossier-21"
                    }
                ],
                "is_leafnode": true,
                "review_state": "repositoryfolder-state-active",
                "title": "2. Bildung"
            }
        ],
        "inactive_dossiers": []
    }

Statusänderungen können wie bei anderen Objekten und im Kapitel :ref:`workflow` mittels ``@workflow`` Endpoint durchgeführt werden.


Bewertungsentscheid ändern
--------------------------

Der Bewertungsentscheid lässt sich mit einem PATCH request auf den ``@appraisal`` Endpoint ändern. Es wird ein Mapping ``UID:Bewertungsentscheid`` erwartet. Somit lässt sich der Bewertungsentscheide von einzelnen oder mehreren Dossiers verändern:

**Request**:

 .. sourcecode:: http

    PATCH http://example.org/fd/ordnungssystem/disposition-234/@appraisal HTTP/1.1
    Accept: application/json
    Content-Type: application/json

    {
      "9823u409823094": true,
      "9823u409823021": false,
    }


 **Response**:

 .. sourcecode:: http

    HTTP/1.1 204 No Content
    Content-Type: application/json


Ablieferungsnummer bearbeiten
-----------------------------

Die Ablieferungsnummer lässt sich mit einem PATCH request auf den ``@transfer-number`` Endpoint ändern. ``transfer-number`` wird im Body erwartet":

**Request**:

 .. sourcecode:: http

    PATCH http://example.org/fd/ordnungssystem/disposition-234/@transfer-number HTTP/1.1
    Accept: application/json
    Content-Type: application/json

    {
      "transfer-number": "Angebot 31.8.2016",
    }


 **Response**:

 .. sourcecode:: http

    HTTP/1.1 204 No Content
    Content-Type: application/json
