Debugging von Sablon-Vorlagen
-----------------------------

Einem Manager stehen die folgenden Plone-Views zum Debugging der Vorlagen zur
Verfügung:

- Inhaltstyp Sablon-Vorlage: ``fill_meeting_template`` füllt Beispieldaten einer
  Sitzung in die Sablon-Vorlage ein. Probleme mit der Syntax der
  Formatierungs-DSL werden so schnell ersichtlich.

- Inhaltstyp Sitzung: ``download_protocol_json`` ermöglicht es, das JSON File
  herunterzuladen, das zum Generieren des Dokuments aus der Sablon-Vorlage
  verwendet wird.

- Inhaltstyp Sitzung: ``download_generated_protocol`` ermöglicht es, ein
  Protokoll einer Sitzung zu generieren und herunterzuladen, ohne dass das
  bestehende Protokoll (das im GEVER abgelegte Dokument) verändert wird.

- Inhaltstyp Sitzung: ``debug_docxcompose`` ermöglicht es die ``docx`` Dateien,
  die zum Protokoll zusammengesetzt werden, separat in einem ``zip``
  herunterzuladen. Dies ermöglicht es Fehler im docxcompose einfacher zu
  analysieren.

.. disqus::
