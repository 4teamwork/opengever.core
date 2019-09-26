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

Ein bestehendes Lock kann mittels ``@unlock`` Endpoint entfernt werden.


  .. sourcecode:: http

    POST /ordnungssystem/dossier-23/document-123/@unlock HTTP/1.1
    Accept: application/json

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
