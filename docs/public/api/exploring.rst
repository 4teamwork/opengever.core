Die API entdecken mit Postman
=============================

Um die API interaktiv zu entdecken, ist die Chrome-Extension Postman_ sehr gut geeignet.


Konfiguration
-------------

Damit Links, welche die API zurückgibt, einfach gefolgt werden kann, sollte die Option **"Retain headers on clicking on links"** in den Einstellungen von Postman aktiviert werden:

|postman-retain-headers|


Diese Option stellt sicher, dass einmal konfigurierte HTTP-Header bei Folge-Requests mitgeschickt werden, wenn diese durch das Klicken auf Links in der Response ausgelöst werden. Dies erleichtert so das Navigieren der Struktur mittels der API.

Die Option **"Send anonymous usage data to Postman"** sollte deaktiviert werden.

Verwendung
----------

Als erstes muss das zu verwendende **HTTP Verb** für den Request bestimmt werden. Dieses kann über das entsprechende Drop-Down Menü ausgewählt werden. Als nächstes muss im Feld rechts vom ausgewählten HTTP Verb die **URL des Objekts** eingetragen werden, auf welches ein Request gemacht werden soll:

|postman-request|


Anschliessend müssen die notwendigen HTTP Header gesetzt werden. Zum einen ist dies der ``Authorization`` Header für die Authentisierung mit dem richtigen Benutzer, und zum anderen der ``Accept`` Header welcher bewirkt, dass der Request von der API behandelt wird.

----------

Für das Setzen des ``Authorization`` Headers gibt es eine eigenes Tab, welches den endültigen Header aus den gewählten Authentisierungsmethode und Benutzernamen + Passwort generiert.

Als Authentisierungsmethode muss **"Basic Auth"** gewählt werden, und als Benutzer ein existierender und entsprechend berechtigter Benutzer. Nachdem diese Parameter angegeben wurde, kann mittels Klick auf **"Update Request"** der entsprechende ``Authorization`` Header erzeugt und in den vorbereiteten Request übernommen werden.

|postman-basic-auth|

----------

Im **"Headers"** Tab muss nun noch der ``Accept: application/json`` Header hinzugefügt werden:

|postman-headers|


Der Request ist nun vorbereitet und kann durch einen Klick auf **"Send"** abgeschickt werden.

Die Antwort des Servers (Response) erscheint nun unter dem Request. Den Links in den ``@id`` Attributen kann nun durch einen Klick gefolgt werden, und Postman bereitet für den angeklickten Link einen weiteren Request mit den den gleichen Headern vor, welcher durch einen Klick auf **"Send"** wieder abgesendet werden kann.

So lässt sich die Struktur des GEVER-Mandandanten über die API mittels ``GET`` Requests sehr einfach navigieren.



.. _Postman: http://www.getpostman.com/

.. |postman-retain-headers| image:: ../_static/img/postman_retain_headers.png
.. |postman-request| image:: ../_static/img/postman_request.png
.. |postman-basic-auth| image:: ../_static/img/postman_basic_auth.png
.. |postman-headers| image:: ../_static/img/postman_headers.png
