.. resolve_oguid:

Resolve Oguid
=============

Mit dem ``@resolve-oguid`` kann die serialisierte Repräsentation eines Inhalts
im Mandatenverbund abgefragt werden. Der Endpoint leitet den Request an eine
andere Admin-Unit weiter, sollte sich der Inhalt nicht auf der aktuellen
Admin-Unit befinden.

Parameter
---------

Die Oguid muss als Query-String Parameter mitgegeben werden.

================ ===========================================================
Parameter        Beschreibung
================ ===========================================================
``oguid``        Die Oguid des zu serialisierenden Inhalts. Diese setzt sich
                 aus <admin_unit_id>:<int_id> zusammen.
================ ===========================================================

Des weiteren sind alle Query-String Parameter erlaubt, die bei einem GET Request
auf einen einzelnen Inhalt möglich sind.

  .. sourcecode:: http

    GET /@resolve-oguid?oguid=fd:123456789 HTTP/1.1
    Accept: application/json

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": "http://localhost:8080/rk/ordnungssystem/uebergeordnete-erlasse/dossier-1/task-1",
      "@type": "opengever.task.task",
      "UID": "1546308893054eb8b3c21fc8be129607",
      "changed": "2020-07-27T12:28:47+00:00",
       "...": "..."
    }


Remote Requests
---------------

Wurde der Request intern an eine andere Admin-Unit weitergeleitet so ist dies
über den Header ``X-GEVER-RemoteRequest`` ersichtlich.
