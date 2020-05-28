
Anhänge speichern
=================

E-Mail-Anhänge können in OneGov GEVER als separate Dokumente gespeichert werden (nur einmal pro Anhang). Dies wird in der REST API mit einem ``POST`` Request auf den ``@extract-attachments`` Endpoint ermöglicht. Der ``positions`` Parameter erlaubt auszuwählen, welche Anhänge extrahiert werden sollen und entspricht der ``position``, die in der Response eines ``GET`` Request auf eine E-Mail für jeden Anhang enthalten ist. Wenn ``positions`` nicht angegeben wird, dann werden alle Anhänge extrahiert, welche noch nicht gespeichert wurden. Die Dokumente werden im selben Gefäss erstellt, in welchem sich die E-Mail befindet.

**Beispiel-Request**:

   .. sourcecode:: http

       POST http://localhost:8080/fd/ordnungssystem/bildung/dossier-25/document-78/@extract-attachments HTTP/1.1
       Accept: application/json

       {
        "positions": [4, 5]
       }


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
          {
              "extracted_document_title": "Ein Dokument",
              "extracted_document_url": "http://localhost:8080/fd/ordnungssystem/bildung/dossier-25/document-79",
              "position": 4
          },
          {
              "extracted_document_title": "Ein weiteres Dokument",
              "extracted_document_url": "http://localhost:8080/fd/ordnungssystem/bildung/dossier-25/document-80",
              "position": 5
          }
      ]
