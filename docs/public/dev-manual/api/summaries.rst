.. _summaries:

Summarische Auflistungen
------------------------

Einträge in summarischen Auflistungen von Containern ("Foldern") enthalten
standardmässig die Felder ``@id``, ``@type``, ``title``, ``description``
und ``review_state``.

Über den Parameter ``metadata_fields`` kann die gewünschte Liste der
Felder jedoch angegeben werden, um spezifische Metadaten in der summarischen
Auflistung zu erhalten.

Die zur Zeit unterstützten Felder für summarische Auflistungen sind die
folgenden:

- ``@type`` (Inhaltstyp)
- ``created`` (Erstellungsdatum)
- ``creator`` (Ersteller)
- ``description`` (Beschreibung)
- ``filename`` (Dateiname, falls Dokument)
- ``filesize`` (Dateigrösse, falls Dokument)
- ``mimetype`` (Datetyp, falls Dokument)
- ``modified`` (Modifikationsdatum)
- ``review_state`` (Workflow-Status ID)
- ``review_state_label`` (Workflow-Status Bezeichnung)
- ``title`` (Titel)


Der Query-String Parameter ``metadata_fields`` kann verwendet werden, um die in
summarische Auflistungen für ``GET`` requests zu steuern.

.. note::
    Die summarischen Auflistungen von Suchresultaten des ``@search`` endpoints
    verwenden den gleichen Mechanismus (``metdata_fields``).


Beispiel anhand eines ``GET`` requests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. http:get:: /(path)?metadata_fields=(fieldlist)

   Liefert die Attribute des Objekts unter `path` zurück, mit den in
   `fieldlist` angegebenen Feldern in der summarischen Auflistung
   der children (``items``).

   **Beispiel-Request**:

   .. sourcecode:: http

      GET /ordnungssystem/fuehrung/dossier-23?metadata_fields:list=filesize&metadata_fields:list=filename HTTP/1.1
      Accept: application/json

   **Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@context": "http://www.w3.org/ns/hydra/context.jsonld",
        "@id": "https://example.org/ordnungssystem/fuehrung/dossier-23",
        "@type": "opengever.dossier.businesscasedossier",
        "title": "Ein Geschäftsdossier",

        "...": "",

        "items": [
          {
            "@id": "https://example.org/ordnungssystem/fuehrung/dossier-23/document-259",
            "@type": "opengever.document.document"
            "review_state": "document_state_draft"
            "description": "..."
            "title": "..."
            "filesize": 42560,
            "filename": "vortrag.docx",


          },
          {
            "@id": "https://example.org/ordnungssystem/fuehrung/dossier-23/document-260",
            "@type": "opengever.document.document"
            "review_state": "document_state_draft"
            "description": "..."
            "title": "..."
            "filesize": 73536,
            "filename": "bewerbung.docx",
          }
        ],
        "parent": {
          "@id": "https://example.org/ordnungssystem/fuehrung",
          "@type": "opengever.document.document"
          "review_state": "document_state_draft"
          "description": "..."
          "title": "..."
          "filesize": null,
          "filename": null,
        },

        "...": ""

      }


.. container:: collapsible

    .. container:: header

       **Code-Beispiel (Python)**

    .. literalinclude:: examples/example_get_custom_summary.py
