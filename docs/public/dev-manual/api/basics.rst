Grundlagen
==========

Die OneGov GEVER API ist eine RESTful_ HTTP API.

Dies bedeutet, dass Operationen über die API via HTTP Requests durchgeführt
werden, welche von einem HTTP Client abgesetzt werden.

  HTTP_ ist ein Protokoll für die Kommunikation zwischen einem Client und einem
  Server, und basiert auf dem Austausch von Anfragen des Clients (**Request**)
  und Antworten des Servers (**Response**).

Die Verwendung der API funktioniert so, dass Requests auf die URL des
entsprechenden Inhaltsobjekts gemacht werden, aber ein spezieller
HTTP-Header verwendet wird welchen den Request als API-Request auszeichnet
(um ihn von einem Request eines normales Browsers abzugrenzen).

Für die meisten Requests ist es notwendig, dass sich der Benutzer zuerst an der
API authentisiert, siehe dazu das Kapitel zur
:ref:`Authentisierung <authentication>`.

Änderungen an der API werden im :ref:`API Changelog <api-changelog>` dokumentiert.

------


Request
-------

Requests an die API setzen sich zusammen aus einem **HTTP Verb**, einer
**URL**, **Request-Headern**, und für gewisse Typen von Requests, einem
**Request-Body** im JSON Format.

HTTP Verb
^^^^^^^^^

Im Kapitel :ref:`operations` ist beschrieben, auf welche HTTP Verben die
verfügbaren Operationen gemappt sind.

URL
^^^

Die URL eines Requests ist bestimmt durch das Objekt, für welches eine
Operation durchgeführt werden soll. Diese URL ist in der Regel für das
entsprechende Objekt in der Adresszeile des Browsers sichtbar.

.. _basics-headers:

Headers
^^^^^^^

Die API verwendet JSON für die Serialisierung von Daten (für die
Eingabe wie auch die Ausgabe).

Dementsprechend muss bei der Anfrage (Request) der HTTP-Header
``Accept: application/json`` gesetzt werden, damit ein Request an die API
weitergeleitet wird.

**Beispiel-Request**:

.. sourcecode:: http

  GET /ordnungssystem HTTP/1.1
  Accept: application/json

Dieser Header muss bei *jedem* Request auf die API gesetzt werden, und wird in
den folgenden Beispielen daher nicht mehr immer explizit erwähnt.

Body
^^^^

Bestimmte Request-Typen (``POST`` und ``PATCH``) brauchen weitere
Informationen, welche in Form eines Request-Bodies im JSON Format mitgegeben
werden. Wie der Inhalt dieses Bodies genau beschaffen sein muss, ist im
Kapitel :ref:`operations` beschrieben.


------


Response
--------

Wenn eine Response einen Body hat, ist dies immer ein JSON-Dokument:

**Beispiel-Response**:

.. sourcecode:: http

   HTTP/1.1 200 OK
   Content-Type: application/json

   {
      "@context": "http://www.w3.org/ns/hydra/context.jsonld",
      "@id": "https://example.org/ordnungssystem/fuehrung/dossier-23",
      "@type": "opengever.dossier.businesscasedossier",
      "oguid": "fd:12345",
      "title": "Titel des Objekts",
      "review_state": "dossier-state-active",
       "...": "..."
   }

`(Gekürzt - vollständige Beispiele von konkreten Responses sind in späteren
Abschnitten zu finden)`

Die mit einem ``@`` Zeichen präfixten Keys haben eine spezielle Beduetung, und
entsprechen nicht einem Feld auf dem Inhaltstyp, sondern sind JSON-LD_
(Linked Data) Metadaten:

============= ================= ===============================================
Key           Bedeutung               Beschreibung
============= ================= ===============================================
``@context``  Kontext           Wird immer denselben Wert haben, eine URI zum
                                Hydra Kontext - dieser Key hat für die OneGov
                                GEVER API im Moment keine Relevanz.

``@id``       Eindeutige URL    Die eindeutige URL zu einem Objekt.

``@type``     Typ eines Objekts Der Typ eines Objekts. Dieser Typ entspricht
                                einem der unter :ref:`content-types`
                                angegebenen Typen, und lässt den Client so
                                wissen, welche Felder mit welchen Datentypen
                                in einer Antwort zu erwarten sind.
============= ================= ===============================================


Zusätzlich zu den oben aufgeführten JSON-LD Attributen gibt es für Objekttypen,
welche einen Workflow haben, ein allgemeines Property ``review_state``, welches
den aktuellen Workflow-State enthält:

================= ================= ===============================================
Key               Bedeutung               Beschreibung
================= ================= ===============================================
``review_state``  Workflow-State    Falls das Objekt einen Workflow hat, enthält
                                    dieses Property den aktuellen Worflow-State.
================= ================= ===============================================

Siehe :ref:`Workflow <workflow>` für Details bezüglich Workflows.


.. _RESTful: https://de.wikipedia.org/wiki/Representational_State_Transfer
.. _HTTP: https://de.wikipedia.org/wiki/Hypertext_Transfer_Protocol
.. _JSON-LD: http://json-ld.org/
