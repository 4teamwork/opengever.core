.. _vocabularies:

Vokabulare
==========

Die Grundlagen für den Umgang mit Vokabularen und Sourcen findet man in der
`plone.restapi Dokumentation Vocabularies and Sources <https://plonerestapi.readthedocs.io/en/latest/vocabularies.html>`_.

In ``plone.restapi`` wird jedoch nur das Editieren bestehender Inhalte
abgebildet. GEVER erweitert dies um eine weitere Aufruf-Syntax für ``@sources``,
`@querysources`` und ``@vocabularies``. Für diese drei Endpoints wird eine neue
Aufruf-Syntax eingeführt, welche die Add-Semantik wiederspiegelt.

.. sourcecode:: http

   GET (container)/@sources/(portal_type)/(field_name) HTTP/1.1


.. sourcecode:: http

   GET (container)/@querysources/(portal_type)/(field_name) HTTP/1.1


.. sourcecode:: http

   GET (container)/@vocabularies/(portal_type)/(field_name) HTTP/1.1


Die Endpoints wurden überschrieben und so umgebaut, dass sie entweder einenn
oder zwei Pfad-Parameter akzeptieren:

- 1 Parameter: Der parameter ist ``field_name``. Dies impliziert Edit intent.
- 2 Parameter: Die Parameter sind ``portal_type`` und ``field_name``, in dieser
  Reihenfolge. Dies impliziert Add intent.

Abhängig von der Aufruf-Syntax soll das Schema, von dem die Source, Querysource
oder Vocabulary geholt wird, unterschiedlich bestimmt werden:

- Edit - es soll der ``portal_type`` des context ausgelesen werden
- Add - es soll der ``portal_type`` Pfad-Parameter verwendet werden


Eine Query-Source nach token abfragen
-------------------------------------

Zusätzlich zum schon in ``plone.restapi`` zur Verfügung gestellten Paremeter
``query`` lässt sich eine ``@querysource`` in GEVER auch nach einem bereits
bekannten ``token`` abfragen. Dieses muss als Query-String Paremeter angegeben
werden. Es darf nur entweder ``token`` oder ``query`` verwendet werden, nicht
beides zugleich.

**Beispiel-Request**:

.. sourcecode:: http

   GET /dossier-15/@querysources/responsible?token=hans.muster HTTP/1.1
   Accept: application/json


**Beispiel-Response**:

.. sourcecode:: http

   HTTP/1.1 200 OK
   Content-Type: application/json

   {
     "@id": "/dossier-15/@querysources/responsible?token=hans.muster",
     "items": [
       {
         "title": "Hans Muster (hans.muster)",
         "token": "hans.muster"
       }
     ],
     "items_total": 1
   }

Dossier-Typen
-------------

Für die gängigen Anwendungsfälle können die Dossier-Typen über die oben beschriebenen Vokabular-Endpoints bezogen werden. Für gewisse Zwecke ist es aber nötig, die Dossier-Typen in einer "rohen" Form zu beziehen - dafür kann der ``@raw-dossier-types`` Endpoint verwendet werden.

Dieser Endpoint gibt die Dossier-Typen ungefiltert zurück (auch versteckte / deaktivierte Typen werden aufgeführt), und die Typen werden in der Reihenfolge zurückgegeben, in der sie erfasst wurden (statt alphabetisch sortiert wie bei normalen Vocabularies).