Serialisierung
==============

In der REST API muss an verschiedenen Stellen Inhalt von und nach JSON
serialisiert und deserialisiert werden.

Grundsätzlich ist das Format für die Serialisierung (Lesen von der API)
dasselbe wie für die Deserialisierung (Schreiben via API).

Primitive Typen
---------------

Primitive Datentypen, welche eine entsprechende Repräsentation in JSON haben,
wie z.B. Integers oder Strings, werden direkt zwischen Python und JSON
übersetzt. Ein Python string aus GEVER wird also als JSON-String ausgegeben,
und umkekehrt.

Datum / Zeit
--------------

Da JSON keinen nativen Support für datetimes bietet, werden Python/Zope
datetimes zu `ISO 8601 <https://de.wikipedia.org/wiki/ISO_8601>`_ Strings
serialisiert. Als Zeitzone wird bei der Serialisierung immer UTC verwendet,
nicht Lokalzeit.

============================================================================== ======================================
Python                                                                         JSON
============================================================================== ======================================
``time(19, 45, 55)``                                                           ``'19:45:55'``
``date(2015, 11, 23)``                                                         ``'2015-11-23'``
``datetime(2015, 11, 23, 19, 45, 55, tzinfo=pytz.timezone('Europe/Zurich'))``  ``'2015-11-23T18:45:55+00:00'``
``DateTime('2018/08/09 13:43:27.261730 GMT+2')``                               ``'2018-08-09T11:43:58+00:00'``
============================================================================== ======================================





Dateien
-------

.. _label-api_download:

Download (Serialisierung)
^^^^^^^^^^^^^^^^^^^^^^^^^

Für den Download von Dateien wird ein File-Field zu einem Mapping serialisiert
welches die wichtigsten Metadaten zur Datei (nicht zum Dokument), und einen
Download-Link für das Herunterladen enthält:

.. code:: json

      {
        "@id": "http://example.org/dossier/mydoc",
        "@type": "opengever.document.document",
        "title": "My document",
        "...": "",
        "file": {
          "content-type": "application/pdf",
          "download": "http://example.org/dossier/mydoc/@@download/file",
          "filename": "file.pdf",
          "size": 74429
        }
      }


Die URL im ``download`` Property zeigt auf die reguläre Download-View von
Plone. Dies bedeutet, dass der Client einen ``GET`` request auf diese URL
durchführen kann, um die Datei herunterzuladen. Jedoch darf hier als
``Accept`` Header nicht mehr ``application/json`` gesetzt werden (wie sonst
für API-Requests üblich), sondern der MIME-Type der zu herunterladenden
Datei (gemäss dem ``content-type`` Property).


Upload (Deserialisierung)
^^^^^^^^^^^^^^^^^^^^^^^^^

Für Datei-Felder muss der Client die Datei und deren Metadaten als ein Mapping
senden, ähnlich dem Mapping für den Download. Das Mapping muss die Daten der
Datei base64 codiert im ``data`` Property enthalten, und weitere Metadaten in
den übrigen Properties:

- ``data`` - der Inhalt der Datei, base64 codiert
- ``encoding`` - das Encoding das verwendet wurde, also ``base64``
- ``content-type`` - der MIME-Type der Datei
- ``filename`` - der Dateiname, inkl. Dateiendung

.. code:: json

      {
        "@type": "opengever.document.document",
        "title": "My file",
        "...": "",
        "file": {
            "data": "TG9yZW0gSXBzdW0uCg==",
            "encoding": "base64",
            "filename": "lorem.txt",
            "content-type": "text/plain"}
      }


Verweise
--------

Serialisierung
^^^^^^^^^^^^^^

Verweise werden zu einer summarischen Repräsentation des referenzierten
Objekts serialisiert:

.. code:: json

    {
      "...": "",
      "relatedItems": [
        {
          "@id": "http://example.org/dossier/doc1",
          "@type": "opengever.document.document",
          "title": "Document 1",
          "description": "Description"
        }
      ]
    }

Die Liste von Verweisen wird zu einer einfachen JSON-Liste serialisiert.

Deserialisierung
^^^^^^^^^^^^^^^^

Um beim Erstellen oder Updaten von Objekten einen Verweis zu setzen, können
verschiedene Methoden verwendet werden um das Verweisziel anzugeben. Es kann
einer der hier aufgeführten Bezeichner verwendet werden, um das Verweisziel
eindeutig zu identifizieren:

======================================= ======================================
Typ                                     Beispiel
======================================= ======================================
UID                                     ``'9b6a4eadb9074dde97d86171bb332ae9'``
IntId                                   ``123456``
Pfad                                    ``'/dossier/doc1'``
URL                                     ``'http://example.org/dossier/doc1'``
======================================= ======================================

.. disqus::
