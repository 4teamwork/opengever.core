Debugging von Sablon-Vorlagen
-----------------------------

Einem Manager stehen die folgenden Aktionen zum Debugging der Vorlagen zur
Verfügung:

- Inhaltstyp Sablon-Vorlage: Aktion ``Beispiels-Sitzungsdaten einfüllen``
  füllt Beispieldaten einer Sitzung in die Sablon-Vorlage ein.
  Probleme mit der Syntax der Formatierungs-DSL werden so schnell ersichtlich.
  Die entsprechende Plone-View ist ``fill_meeting_template``.

- Inhaltstyp Sitzung: Aktion ``JSON Sitzungsdaten herunterladen`` ermöglicht es,
  das JSON File herunterzuladen, das zum Generieren des Dokuments aus
  der Sablon-Vorlage verwendet wird.
  Die entsprechende Plone-View ist ``download_protocol_json``.

- Inhaltstyp Sitzung: Aktion ``Dateien für docxcompose herunterladen``
  ermöglicht es die ``docx`` Dateien, die zum Protokoll zusammengesetzt
  werden, separat in einem ``zip`` herunterzuladen.
  Dies ermöglicht es Fehler in docxcompose einfacher zu analysieren.
  Die entsprechende Plone-View ist ``debug_docxcompose``.

- Inhaltstyp Traktandum: Aktion ``Dateien für docxcompose herunterladen``
  (In den Aktionen des Traktandums) ermöglicht es die ``docx`` Dateien,
  die zum Protokollauszug zusammengesetzt werden, separat in
  einem ``zip`` herunterzuladen. Dies ermöglicht es Fehler in docxcompose
  einfacher zu analysieren. Die Entsprechende URL beinhaltet die id des
  Traktandums wie die sonstigen traktandumbasierten Aktionen, z.B.:
  ``meeting-X/agenda_items/YZ/debug_excerpt_docxcompose``.

.. disqus::
