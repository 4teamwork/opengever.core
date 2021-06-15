.. _trash:

Papierkorb
==========

Objekte in den Papierkorb legen
-------------------------------

Dokumente und Teamraum Ordner können über den ``/@trash`` Endpoint in den Papierkorb gelegt werden.

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


Objekte wiederherstellen
------------------------

Objekte, die sich im Papierkorb befinden, können über den ``/@untrash``
Endpoint wiederhergestellt werden. Ein Objekt kann nur wiederhergestellt werden, wenn
das übergeordnete Objekt sich nicht im Papierkorb befindet.

**Beispiel-Request**:

   .. sourcecode:: http

       POST /ordnungssystem/fuehrung/dossier-23/document-8/@untrash HTTP/1.1
       Accept: application/json

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content

      null
