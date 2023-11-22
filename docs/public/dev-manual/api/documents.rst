Dokumente
=========

Für die Bearbeitung einer Dokumentdatei muss auch via REST API der Checkin/Checkout workflow beachtet und eingehaltet werden.

Folgende Abfolge ist dabei vorgesehen:

    1. :ref:`Checkout <label-api_checkout>`
    #. :ref:`Lock <label-api_lock>`
    #. :ref:`Download <label-api_download>`
    #. :ref:`Upload <label-api_upload>`
    #. :ref:`Unlock <label-api_unlock>`
    #. :ref:`Checkin <label-api_checkin>`

Dieser Workflow kann abgebrochen werden indem man den Checkout widerruft mit dem :ref:`@cancelcheckout <label-api_cancelcheckout>` Endpoint.

Dokumentversionen können mit dem :ref:`@history <label-api_history>` Endpoint aufgelistet werden.

.. _label-api_checkout:

Checkout - Dokument auschecken
------------------------------
Ein Dokument wird via ``@checkout`` Endpoint ausgecheckt.


  .. sourcecode:: http

    POST /ordnungssystem/dossier-23/document-123/@checkout HTTP/1.1
    Accept: application/json

  .. sourcecode:: http

    HTTP/1.1 204 No Content

Darf ein Dokument vom aktuellen Benutzer nicht ausgecheckt werden, so wird mit dem Status ``403 Forbidden`` geantwortet.

  .. sourcecode:: http

    POST /ordnungssystem/fuehrung/dossier-23/document-123/@checkout HTTP/1.1
    Accept: application/json

  .. sourcecode:: http

    HTTP/1.1 403 Forbidden
    Content-Type: application/json

    {
        "error": {
            "message": "Checkout is not allowed.",
            "type": "Forbidden"
        }
    }


Lock
----
Um das Dokument von Schreibzugriffen von anderen Benutzern zu schützen muss es mittels Lock gesperrt werden.

.. _label-api_lock:

Lock erstellen
~~~~~~~~~~~~~~

  .. sourcecode:: http

    POST /ordnungssystem/dossier-23/document-123/@lock HTTP/1.1
    Accept: application/json

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "creator": "peter.meier",
      "locked": true,
      "name": "plone.locking.stealable",
      "stealable": true,
      "time": 1477076400.0,
      "timeout": 600,
      "token": "0.684672730996-0.25195226375-00105A989226:1477076400.000"
    }


Standardmässig haben Locks ein Timeout von 600s Sekunden und müssen anschliessend erneuert werden.
Entweder sollten daher Locks periodisch erneuert werden oder man verwendet ein höheres Timeout:


Lock erneuern
~~~~~~~~~~~~~

  .. sourcecode:: http

    POST /ordnungssystem/dossier-23/document-123/@refresh-lock HTTP/1.1
    Accept: application/json

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "creator": "peter.meier",
      "locked": true,
      "name": "plone.locking.stealable",
      "stealable": true,
      "time": 1477076400.0,
      "timeout": 600,
      "token": "0.684672730996-0.25195226375-00105A989226:1477076400.000"
    }


Lock erstellen mit eigenem Timeout
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  .. sourcecode:: http

    POST /ordnungssystem/dossier-23/document-123/@lock HTTP/1.1
    Accept: application/json

    {
        "timeout": 86400
    }


  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "creator": "peter.meier",
      "locked": true,
      "name": "plone.locking.stealable",
      "stealable": true,
      "time": 1477076400.0,
      "timeout": 86400,
      "token": "0.684672730996-0.25195226375-00105A989226:1477076400.000"
    }


.. _label-api_unlock:

Lock entfernen
~~~~~~~~~~~~~~

Ein bestehendes Lock kann mittels ``@unlock`` Endpoint entfernt werden. Der ``lock_type`` Parameter erlaubt es, den Lock-Typ anzugegeben, der entfernt werden soll. Wenn ``lock_type`` nicht angegeben wird, wird ein Lock vom Typ ``plone.locking.stealable`` entfernt.


  .. sourcecode:: http

    POST /ordnungssystem/dossier-23/document-123/@unlock HTTP/1.1
    Accept: application/json

    {
        "lock_type": "document.copied_to_workspace.lock"
    }

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
        "locked": false,
        "stealable": true
    }


.. _label-api_upload:

Datei aktualisieren
-------------------
Für den Upload einer Datei unterstützt die REST API das sogenannte TUS Protocol. Eine detaillierte Dokumentation über die verschieden Möglichkeiten und Endpoints finden Sie in der `plone.restapi Dokumentation <https://plonerestapi.readthedocs.io/en/latest/tusupload.html>`_.

Folgend ein kurzes Beispiel wie eine Datei eines bestehenden Dokumentes aktualisiert werden kann.

Upload URL erstellen:

  .. sourcecode:: http

    POST /ordnungssystem/dossier-23/document-123/@tus-replace HTTP/1.1
    Accept: application/json
    Tus-Resumable: 1.0.0
    Upload-Length: 8
    Upload-Metadata: filename dGVzdC50eHQ=,content-type dGV4dC9wbGFpbg==


  .. sourcecode:: http

    HTTP/1.1 201 created
    Content-Type: application/json
    location: ordnungssystem/ressourcen-und-support/personal/personalrekrutierung/dossier-4/document-2/@tus-upload/6cdfc5ddd1844e8cbca32721c4b17b84


Datei uploaden:

  .. sourcecode:: http

      PATCH /ordnungssystem/dossier-23/document-123/@tus-upload/6cdfc5ddd1844e8cbca32721c4b17b84 HTTP/1.1
      Accept: application/json
      Tus-Resumable: 1.0.0
      Upload-Offset: 0
      Content-Type: application/offset+octet-stream

      test data

  .. sourcecode:: http

    HTTP/1.1 204 No content
    Content-Type: application/json

Wurde das Dokument zuvor mittels Lock gesperrt, muss das Lock Token über den
`Lock-Token` header mitgegeben werden.

Dateiupload mit Lock Token:

  .. sourcecode:: http

      PATCH /ordnungssystem/dossier-23/document-123/@tus-upload/6cdfc5ddd1844e8cbca32721c4b17b84 HTTP/1.1
      Accept: application/json
      Tus-Resumable: 1.0.0
      Upload-Offset: 0
      Content-Type: application/offset+octet-stream
      Lock-Token: 0.684672730996-0.25195226375-00105A989226:1477076400.000

      test data

  .. sourcecode:: http

    HTTP/1.1 204 No content
    Content-Type: application/json


.. _label-api_checkin:

Checkin - Dokument einchecken
-----------------------------
Ein Dokument wird via ``@checkin`` Endpoint eingecheckt, dabei wird automatisch eine neue Version erstellt.

  .. sourcecode:: http

    POST /ordnungssystem/dossier-23/document-123/@checkin HTTP/1.1
    Accept: application/json

    {
        "comment": "Kapitel 3 - 6 korrigiert."
    }

  .. sourcecode:: http

    HTTP/1.1 204 No content
    Content-Type: application/json


.. _label-api_cancelcheckout:

Cancel checkout - Checkout widerrufen
-------------------------------------

Der checkout von einem Dokument kann man mittels ``@cancelcheckout`` Endpoint widerrufen.

  .. sourcecode:: http

    POST /ordnungssystem/dossier-23/document-123/@cancelcheckout HTTP/1.1
    Accept: application/json

  .. sourcecode:: http

    HTTP/1.1 204 No Content


.. _label-api_history:

Versionen auflisten:
--------------------

  .. sourcecode:: http

    GET /ordnungssystem/dossier-23/document-123/@history HTTP/1.1
    Accept: application/json

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    [
        {
            "@id": "/ordnungssystem/dossier-23/document-123/@history/1",
            "action": "Bearbeitet",
            "actor": {
                "@id": "http://localhost:8080/fd/@users/peter.meier ",
                "fullname": "Peter Meier",
                "id": "peter.meier",
                "username": "peter.meier"
            },
            "comments": null,
            "may_revert": true,
            "time": "2019-03-27T10:50:59.196843",
            "transition_title": "Bearbeitet",
            "type": "versioning",
            "version": 1
        },
        {
            "@id": "/ordnungssystem/dossier-23/document-123/@history/0",
            "action": "Bearbeitet",
            "actor": {
                "@id": "http://localhost:8080/fd/@users/hugo.boss",
                "fullname": "Hugo Boss",
                "id": "hugo.boss",
                "username": "hugo.boss"
            },
            "comments": "Dokument erstellt (Initialversion)",
            "may_revert": true,
            "time": "2019-03-27T09:19:25",
            "transition_title": "Bearbeitet",
            "type": "versioning",
            "version": 0
        }
    ]

.. _save-document-as-pdf:

Dokument als PDF speichern
--------------------------

Mit dem ``@save-document-as-pdf`` kann ein Dokument oder eine Version eines Dokuments als PDF gespeichert werden. Als ``document_uid`` wird die UID des Dokuments erwartet. Wenn keine ``version_id`` mitgegeben wird, wird die aktuelle Version verwendet. Der Endpoint steht auf Stufe Dossier, Teamraum und Teamraum-Ordner zur Verfügung.

  .. sourcecode:: http

    POST /ordnungssystem/dossier-23/@save-document-as-pdf HTTP/1.1
    Accept: application/json

    {
      "document_uid": "f923b2321f174b408c3bd483db9bfa66",
      "version_id": 2
    }

  .. sourcecode:: http

    HTTP/1.1 201 Created
    Location: /ordnungssystem/dossier-4/document-1

Genehmigungen
-------------

Dokument Genehmigungen, welche via Aufgabe erteilt wurden, lassen sich als zusätzliche expansion ebenfalls mit einem GET Request auf ein Dokument abfragen.

  .. sourcecode:: http

    GET /ordnungssystem/dossier-23/document-21?expand=approvals HTTP/1.1
    Accept: application/json

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
        "@id": "/ordnungssystem/dossier-23/document-21",
        "@type": "opengever.document.document",
        "UID": "edc93b13e4bf4d72bcdc49838697ebe6",
        "@components": {
            "approvals": [
                {
                    "approved": "2021-08-02T00:00:00",
                    "approver": "peter.muster",
                    "task": {
                        "@id": "http://example.org/ordnungssystem/dossier-23/document-123",
                        "@type": "opengever.task.task",
                        "UID": "c99df05a4bbe473ead5e2356f5a4f8b4",
                        "description": "",
                        "is_leafnode": null,
                        "review_state": "task-state-in-progress",
                        "title": "Vertragsentwurf prüfen"},
                    "version_id": 1
                }
            ]
        }
    }


Bearbeiten des Öffentlichkeitsstatus
------------------------------------

Für die Bearbeitung des Öffentlichkeitsstatus eines Dokuments in einem abgeschlossen Geschäft, steht ein separater PATCH Endpoint ``@public-trial-status`` zur Verfügung. Dieser funktioniert identisch zum normalen Bearbeitung eines Dokuments, erlaubt aber ausschliesslich die Bearbeitung der Metadaten ``public_trial`` und ``public_trial_statement``.

  .. sourcecode:: http

    PATCH /ordnungssystem/dossier-23/document-11 HTTP/1.1
    Accept: application/json

    {
      "public_trial": "limited-public",
      "public_trial_statement": "Herr Muster, 03.02.2012, genehmigt."
    }

  .. sourcecode:: http

    HTTP/1.1 204 No Content

Dokument über einen XHR-Request als multipart/form-data erstellen
-----------------------------------------------------------------
Neben dem ``@tus-upload``-Endpoint gibt es auch die Mögilchkeit, Dokumente über einen normalen XHR-Request als multipart/form-data zu erstellen.

**Beispiel-Request**:

  .. sourcecode:: http

    POST http://example.com/ordnungssystem/dossier-1/@xhr-upload HTTP/1.1
    Authorization: [AUTH_DATA]
    Accept: application/json
    Content-Type: multipart/form-data; boundary=------------------------b3e801e2d0fb0cc9
    Content-Length: [NUMBER_OF_BYTES_IN_ENTIRE_REQUEST_BODY]

    --------------------------b3e801e2d0fb0cc9
    Content-Disposition: form-data; name="title"

    Hello Worlds
    --------------------------b3e801e2d0fb0cc9
    Content-Disposition: form-data; name="file"; filename="helloworld.pdf"
    Content-Type: application/octet-stream

    [FILE_DATA]


**Beispiel-Response**:

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": "http://example.com/ordnungssystem/dossier-1/document-1",
      "...": "..."
    }
