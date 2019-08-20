Server-Konfiguration
====================

Informationen zur Konfiguration von Linux-Server, auf welchen GEVER deployed
werden soll.


Settings im ``~/.opengever/`` Verzeichnis
-----------------------------------------

In diesem Verzeichnis sind gewisse Server-seitige Settings hinterlegt.


``~/.opengever/ldap/{hostname}.json``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

(required)

In diesem Verzeichnis sind (pro LDAP-Server) die Credentials für den
entsprechenden Server hinterlegt.

Da diese auch für die lokale Entwicklung benötigt werden, sind sie im
`README von opengever.core <https://github.com/4teamwork/opengever.core/#ldap-credentials>`_
dokumentiert.


``~/.opengever/bundle_ingestion/settings.json``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

(optional)

In dieser Datei sind Settings für den Import von OGGBundles auf diesem
Server hinterlegt.

Diese Datei ist optional - sie wird benötigt, falls aus Bundles Dateien von
UNC shares referenziert werden, oder wenn IDs von Principals
(Benutzer oder Gruppen) in den lokalen Rollen von Bundle-Items umgeschrieben
werden müssen (weil sie in GEVER anders lauten sollen als im Bundle angegeben).

Für diese beiden Fälle können in dieser Datei entsprechende Settings
hinterlegt werden:

.. code:: json

    {
        "unc_mounts": {
            "\\\\fileserver.example.org\\sharename": "/mnt/sharename",
            "\\\\fileserver.example.org\\other": "/mnt/other"
        },
    
        "principal_mapping": {
            "username.in.bundle": "username.in.gever"
        }
    }
    

``~/.opengever/oneoffixx/oneoffixx.json``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

(optional)

In dieser Datei können Credentials zu einem OneOffix backend hinterlegt werden.
Diese Datei ist optional - sie wird nur benötigt, wenn OneOffix angebunden
werden soll.

Siehe OneOffix :ref:`OneOffixCredentials` für weitere Details.


``~/.opengever/ftps_transport/profile.json``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

(optional)

Falls das Aussonderungsmodul aktiviert ist, und SIP Pakete mittels dem
FTPSTransport auf einen FTPS-Server hochgeladen werden sollen, müssen in dieser
Datei die Verbindungsdaten für den FTPS-Server hinterlegt werden.

Beispiel:

.. code:: json

    {
      "host": "ftp.example.org",
      "port": 990,
      "username": "john.doe",
      "password": "secret"
    }


