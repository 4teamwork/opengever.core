Dokumente aus Vorlagen
======================

Gever unterstützt diverse Vorlagensysteme.

OneOffix
========

Das OneOffixx Vorlagensystem muss korrekt angebunden werden und das Feauture ``oneoffixx`` muss aktiviert sein.

Erstellen eines Dokuments von einer OneOffixx Vorlage
-----------------------------------------------------

Ein Dokument aus einer OneOffixx Vorlage wird in zwei Schritten erstellt. In einem ersten Schritt wird das Dokument mit allen Metadaten über ein ``POST`` auf den ``@document_from_oneoffixx`` Endpoint erstellt. Der Endpoint unterstützt alle Metadaten, die ein normales Dokument auch unterstützt.

**Beispiel-Request:**

  .. sourcecode:: http

    POST /ordnungssystem/dossier-23/@document_from_oneoffixx HTTP/1.1
    Accept: application/json

    {
    "document": {"title": "My OneOffixx Document"},
    }


Als Antwort erhält der Konsument eine Office-Connector URL welche im Browser aufgerufen werden kann. Der Office-Connector öffnet nun die vorher referenzierte Vorlage.

**Beispiel-Response:**

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@id": "http://nohost/plone/ordnungssystem/dossier-23/document-44",
        "url": "oc:token"
      }



