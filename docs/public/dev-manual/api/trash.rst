.. _trash:

Papierkorb
==========

Dokumente in den Papierkorb legen
---------------------------------

Dokumente können über den ``/@trash`` Endpoint in den Papierkorb gelegt werden.

**Beispiel-Request**:

   .. sourcecode:: http

       POST /ordnungssystem/fuehrung/dossier-23/document-8/@trash HTTP/1.1
       Accept: application/json

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content

      null

Ausgecheckte Dokumente und Dokumente in abgeschlossenen Dossiers können nicht
in den Papierkorb gelegt werden.


Dokumente wiederherstellen
--------------------------

Dokumente, die sich im Papierkorb befinden, können über den ``/@untrash``
Endpoint wiederhergestellt werden.

**Beispiel-Request**:

   .. sourcecode:: http

       POST /ordnungssystem/fuehrung/dossier-23/document-8/@untrash HTTP/1.1
       Accept: application/json

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content

      null
