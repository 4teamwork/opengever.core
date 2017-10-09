.. _scanin:

Scan-In
=======

Der ``/@scan-in`` Endpoint ermöglicht den Upload von Dokumenten in OneGov GEVER
von einem Scanner.

Im Unterschied zu einem herkömmlichen Upload, werden Dokumente nicht im Kontext
des authentisierten Benutzer erstellt, sondern im Kontext des über einen Parameter
angegebenen Benutzers. So kann ein Scanner mit einem unpersönlichen Service-Benutzer
angebunden werden, ohne dass der jeweilige Benutzer in OneGov GEVER authentifiziert
werden muss.

Dokumente können entweder in den Eingangskorb oder in die persönlichen Ablage
hochgeladen werden. In der persönlichen Ablage werden Dokumente in einem Dossier
mit dem Titel "Scaneingang" abgelegt. Falls dieses nicht existiert, wird ein
neues Dossier erstellt.

Die Daten werden als `multipart/form-data` mit einem POST Request übermittelt.

+-------------+------------------------------------------------------------------------------------------------------------------+
|  Parameter  |                                                   Beschreibung                                                   |
+=============+==================================================================================================================+
| userid      | Benutzername, unter welchem Dokumente abgelegt werden sollen.                                                    |
+-------------+------------------------------------------------------------------------------------------------------------------+
| destination | Ort an dem Dokumente abgelegt werden sollen. ``inbox`` für Eingangskorb oder ``private`` für persönliche Ablage. |
+-------------+------------------------------------------------------------------------------------------------------------------+
| org_unit    | Titel oder ID der Organisationseinheit. Nur bei mehreren Eingangskörben relevant.                                |
+-------------+------------------------------------------------------------------------------------------------------------------+


Beispiel: Upload eines Dokuments in die persönliche Ablage des Benutzers hugo.boss.

.. sourcecode:: http

  POST /gever/@scan-in HTTP/1.1
  Authorization: [AUTH_DATA]
  Accept: application/json
  Content-Type: multipart/form-data; boundary=------------------------b3e801e2d0fb0cc9
  Content-Length: [NUMBER_OF_BYTES_IN_ENTIRE_REQUEST_BODY]

  --------------------------b3e801e2d0fb0cc9
  Content-Disposition: form-data; name="userid"

  hugo.boss
  --------------------------b3e801e2d0fb0cc9
  Content-Disposition: form-data; name="destination"

  private
  --------------------------b3e801e2d0fb0cc9
  Content-Disposition: form-data; name="file"; filename="helloworld.pdf"
  Content-Type: application/octet-stream

  [FILE_DATA]
