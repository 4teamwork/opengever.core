.. _batching:

Paginierung
===========

Paginierung (auch *Batching* gennannt) bezeichnet das Aufteilen von Resultaten
auf mehrere "Seiten", um den Server nicht unnötig zu belasten und die Grösse
von Responses kontrollierbar zu halten.

Repräsentationen von Collection-artigen Resourcen werden in der API paginiert
wenn die Anzahl Resultate die Batch-Grösse (standardmässig 25) überschreitet.

.. code:: json

    {
      "@id": "http://example.org/dossier/@search",
      "batching": {
        "@id": "http://example.org/dossier/@search?b_size=10&b_start=20",
        "first": "http://example.org/dossier/@search?b_size=10&b_start=0",
        "last": "http://example.org/dossier/@search?b_size=10&b_start=170",
        "prev": "http://example.org/dossier/@search?b_size=10&b_start=10",
        "next": "http://example.org/dossier/@search?b_size=10&b_start=30"
      },
      "items": [
        "..."
      ],
      "items_total": 175,
    }

Die Batch-Grösse kann pro Request über den Query-String Parameter ``b_size``
gesteuert werden.

Wenn Resultate über mehrere Seiten verteilt werden mussten, sind im Top-Level
Property ``batching`` Hypermedia-Links zur Navigation der Batches enthalten.

Falls hingegen alle Resultate auf einer Seite Platz haben, wird das Top-Level
Property ``batching`` weggelassen.


Top-level Properties
--------------------

================ ===========================================================
Property         Description
================ ===========================================================
``@id``          Kanonische basis-URL für die entsprechende Resource, ohne
                 irgendwelche Batching-Parameter
``items``        Batch mit den Resultaten der aktuellen Seite
``items_total``  Anzahl Resultate insgesamt
``batching``     Hypermedia-Links zur Navigation der Batches
================ ===========================================================


Batching links
--------------

Falls die Resultate über mehrere Seiten verteilt werden mussten, enthält der
Response-Body auf der obersten Ebene ein Property ``batching``, welches
Links zur Navigation der Batches enthält. Diese Links können von einem Client
verwendet werden, um die Seiten einer paginierten Resultatliste zu
navigieren:

================ ===========================================================
Attribute        Description
================ ===========================================================
``@id``          Link zur aktuellen Seite
``first``        Link zur ersten Seite
``prev``         Link zur vorherigen Seite (*falls vorhanden*)
``next``         Link zur nächsten Seite (*falls vorhanden*)
``last``         Link zur letzten Seite
================ ===========================================================



Parameter
---------

Die Paginierung kann mittels zwei Query-String Parametern kontrolliert werden.
Um eine bestimmte Seite zu addressieren, kann der Parameter ``b_start``
verwendet werden. Mit dem Parameter ``b_size`` kann gesteuert werden, wieviele
Resultate eine Seite (maximal) enthalten soll.

================ ===========================================================
Parameter        Beschreibung
================ ===========================================================
``b_size``       Anzahl Resultate pro Seite (default ist 25)
``b_start``      Erstes Resultat ab welchem die Batch-Seite beginnen soll
================ ===========================================================


Komplettes Beispiel einer paginierten Response:

.. sourcecode:: http

    GET /dossier/@search?b_size=5&sort_on=path HTTP/1.1
    Accept: application/json


.. literalinclude:: examples/batching.json
   :language: http

.. disqus::