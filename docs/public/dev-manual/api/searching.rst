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

   Zusätzlich stehen auch die Parameter ``preview_image_url`` und
   ``preview_pdf_url``, bei welchen es sich nicht um eigentliche Metadaten
   handelt, zur Verfügung.


Solr Suche
----------
Um direkt eine Suchabfrage an den Solr Service abzusetzen, steht der ``@solrsearch`` Endpoint zur Verfügung. Für die Abfrage kann SOLR API Syntax und dessen Parameter verwendet werden. Der Endpoint liefert ein Liste von Treffern zurück mit den im Parameter ``fl`` definierten Felder. Die folgende Parameter sind zurzeit vom Endpoint unterstützt:


Query
~~~~~
``q``: Suchbegriff

Beispiel für eine Suche nach "Kurz":

.. sourcecode:: http

  GET /plone/@solrsearch?q=Kurz HTTP/1.1

Der Suchbegriff kann mit dem Parameter ``q.raw`` auch in Solr Query Syntax angegeben werden.
Beispiel für eine Suche nach "Kurz" im Feld "Titel":

.. sourcecode:: http

  GET /plone/@solrsearch?q.raw=Title:Kurz HTTP/1.1


Filters
~~~~~~~
``fq``: Filtern nach einem bestimmten Wert eines Feldes.

Beispiel für ein Suchabfrage gefiltert nach portal_type nur für Dokumente und Dossiers

.. sourcecode:: http

  GET /plone/@solrsearch?fq=portal_type:(opengever.document.document%20OR%20opengever.dossier.businesscasedossier) HTTP/1.1


Fields
~~~~~~
``fl``: Liste der Felder, die zurückgegeben werden sollen. Standardmässig werden die Felder ``@id``, ``@type``, ``title``, ``description`` und ``review_state`` zurückgegeben.

Beispiel für ein Suchabfrage, mit UID, Title und Laufnummer als Resultat

.. sourcecode:: http

  GET /plone/@solrsearch?q=Kurz&fl=UID,Title,sequence_number HTTP/1.1


Weitere optionale Parameter:

- ``start``: Das erste zurückzugebende Element
- ``rows``: Die maximale Anzahl der zurückzugebenden Elemente
- ``sort``: Sortierung nach einem indexierten Feld


Facetten
~~~~~~~~
``facet``: Muss auf ``true`` gesetzt sein damit Solr die Facetten zurückgibt.
``facet.field``: Feld für welches Solr Facetten zurückgeben soll.

Beispiel für ein Suchabfrage mit Facetten für ``responsible`` und ``portal_type``:

  .. sourcecode:: http

    GET /plone/@solrsearch?facet=true&facet.field=portal_type&facet.field=responsible HTTP/1.1

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": "/plone/@solrsearch?facet=true&facet.field=portal_type&facet.field=responsible",
      "facet_counts": {
        "portal_type": {
          "opengever.document.document": {
            "count": 2
          }
        },
        "responsible": {
          "committee:161": {
            "count": 2,
            "label": "Kommission für Rechtsfragen"
          },
          "hugo.boss": {
            "count": 1,
            "label": "Hugo Boss"
          }
        }
      },
      "items": [
        {
          "@id": "/plone/ordnungssystem/fuehrung/dossier-23/document-59",
          "filesize": 12303,
          "modified": "2019-03-11T13:50:14+00:00",
          "title": "Ein Brief"
        },
        {
          "@id": "/plone/ordnungssystem/fuehrung/dossier-23/document-54",
          "filesize": 8574,
          "modified": "2019-03-11T12:32:24+00:00",
          "title": "Eine Mappe"
        }
      ],
      "items_total": 2,
      "rows": 25,
      "start": 0
    }

Pfadtiefe
~~~~~~~~~
``depth``: Limitierung der maximalen Pfadtiefe, relativ zum Kontext oder angegebener Pfad (mit ``fq=path:/path/to/container``)

.. sourcecode:: http

  GET /plone/@solrsearch?depth=1 HTTP/1.1

.. disqus::


Batching
~~~~~~~~
Der Endpoint stellt die Standard-Paginierung gem :ref:`Kapitel Paginierung <batching>` zur Verfügung.
