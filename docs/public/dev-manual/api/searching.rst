Suche
=====

Nach Inhalten in GEVER kann über den ``/@search`` Endpoint gesucht werden:

.. sourcecode:: http

  GET /plone/@search HTTP/1.1
  Accept: application/json

Eine Suche ist standardmässig **kontextabhängig**, das heisst, es wird nur
nach Inhalten innerhalb der Resource gesucht auf welcher ``@search``
aufgerufen wurde. Wird also ``@search`` z.B. auf einem Dossier aufgerufen,
wird nach Objekten gesucht werden, die sich (direkt oder indirekt) in diesem
Dossier befinden (inkl. dem Objekt selbst).

Wird ``/@search`` auf dem Root des GEVER-Mandanten aufgerufen, ist die Suche
global, da sich alle Objekte direkt oder indirekt unterhalb des Roots befinden.

Suchresultate werden im gleichen Format dargestellt wie Inhalte in
Ordner-artigen Objekten:

.. literalinclude:: examples/search.json
   :language: http

Die Standard-Darstellung eines Suchresultats ist eine kurze Zusammenfassung
der wichtigsten Eigenschaften des Objekts. Um weitere Attribute aus dem
Suchkatalog für die aufgelisteten Objekte zurückzugeben, kann der weiter unten
beschriebene ``metadata_fields`` Parameter verwendet werden.

.. note::
        Suchresultate werden **paginiert** wenn die Anzahl Resultate die
        voreingestellte Seitengrösse (default: 25) überschreitet. Siehe
        :doc:`batching` zu Details zum Umgang mit paginierten Resultaten.


Query-Format
------------

Suchabfragen (queries) und Suchoptionen werden als Query-String Parameter mit
dem ``/@search`` Request übergeben:

.. sourcecode:: http

  GET /plone/@search?SearchableText=lorem HTTP/1.1


``SearchableText`` bezieht sich hier auf den Namen eines sogenannten
**Indexes**. Ein Index ist eine Datenstruktur, welche Informationen über
Objekte in einer für Suchabfragen optimierten Form führt. Um nach einer
bestimmten Eigenschaft / einem Attribut eines Objekts suchen zu können, muss
daher ein entsprechender Index existieren.

Der ``SearchableText`` Index ist einer der am häufigsten verwendetet Indexe,
und ist bestimmt für die Volltext-Suche. Der Index enthält daher eine Liste
aller Begriffe mit welchen das Objekt via Volltext-Suche gefunden werden soll:

Titel und Beschreibung, wichtige GEVER-Metadaten wie Laufnummern und
Aktenzeichen, und für Dokumente mit Dateien den extrahierten Text der
jeweiligen Datei.

Weitere häufig verwendete Indexe:

================ =============================================================
Index            Beschreibung
================ =============================================================
``Title``        Titel
``Description``  Beschreibung
``path``         Pfad (z.b. ``/fd/ordnungssystem/allgemeines/dossier-27``)
``portal_type``  Typ des Objekts, siehe :ref:`Inhaltstypen <content-types>`
``reference``    Aktenzeichen (z.B. ``FD 0.0.0 / 1 / 39``)
``modified``     Zeitpunkt der letzten Änderung
================ =============================================================


Eine komplexe Suchabfrage kann aus der Kombination von Filtern auf mehrere
Indexe erstellt werden. Um zum Beispiel nur nach Dokumenten zu suchen, welche
den Begriff "beschluss" enthalten, kann folgende Suchabfrage verwendet werden:

.. sourcecode:: http

  GET /plone/@search?SearchableText=beschluss&portal_type=opengever.document.document HTTP/1.1


Zusätzliche Metadaten
---------------------
Standardmässig werden Suchresultate als eine kurze Zusammenfassung der
wichtigsten Eigenschaften des Objekts dargestellt.

Um weitere Metadaten des Objekts direkt in den Suchresultaten darzustellen,
können diese mittels der Option ``metadata_fields`` verlangt werden:

.. sourcecode:: http

  GET /plone/@search?SearchableText=lorem&metadata_fields=modified HTTP/1.1

Um *alle* im Suchkatalog verfügbaren Metadaten direkt in den Suchresultaten
darzustellen, kann ``metadata_fields=_all`` verwendet werden.

.. note::
    Die Verwendung des ``metadata_fields`` Parameters bedingt Kenntnis der
    internen Index-Namen, und sollte daher mit 4teamwork abgesprochen werden.
    Für :ref:`summarische Auflistungen bei GET requests <summaries>` gibt es
    einen separaten Mechanismus.

.. disqus::