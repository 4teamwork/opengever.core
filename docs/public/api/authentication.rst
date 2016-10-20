.. _authentication:

Authentisierung
===============

Die REST API verwendet Plone PAS (Pluggable Authentication System) für die
Authentisierung.

Das bedeutet, dass jede Authentisierungsmethode, die von einem installierten
PAS Plugin unterstützt wird, grundsätzlich auch mit der REST API funktioniert.

  Die genauen Details zu den installierten Authentisierungs-Plugins und deren
  Konfiguration sind je nach Kunde und Bedürfnissen unterschiedlich. Bei
  Fragen oder Änderungswünschen zu Ihrer Konfiguration wenden Sie sich bitte
  an unseren Support.

Im folgenden sind die Authentisierungsmethoden beschrieben, welche
standardmässig vorhanden sind.


HTTP Basic Auth
---------------

Für HTTP Basic Auth muss ein ``Authorization`` Header im Request gesetzt werden:

.. sourcecode:: http

  GET /ordnungssystem HTTP/1.1
  Authorization: Basic Zm9vYmFyOmZvb2Jhcgo=
  Accept: application/json

Die HTTP Client Libraries der verwendeten Programmiersprache bieten
üblicherweise Hilfsfunktionen an, um diesen Header basierend auf Benutzername
und Passwort zu generieren.

**Code-Beispiel (Python)**: Session erzeugen und Headers setzen

.. literalinclude:: examples/example_session.py



JSON Web Tokens (JWT)
---------------------

Die REST API enthält ein Plugin, welches es erlaubt,
`JSON Web Tokens <https://en.wikipedia.org/wiki/JSON_Web_Token>`_ auszustellen.

Token-basierte Authentisierung ist besonders dazu geeignet, um andere
Applikationen an die API anzubinden, da vermieden werden kann, in der
Applikation die Zugangsdaten eines Benutzers hinterlegen zu müssen.

Ausstellen
^^^^^^^^^^

Ein Token kann ausgestellt werden durch einen ``POST`` Request auf den
``@login`` endpoint. Im Body des Requests müssen die Zugangsdaten des
Benutzers, für den das Token ausgestellt werden soll, enthalten sein:

.. sourcecode:: http

  POST /@login HTTP/1.1
  Accept: application/json
  Content-Type: application/json

  {
      "login": "admin",
      "password": "admin"
  }


Der Server antwortet mit einem JSON-Objekt welches das Token enthält:

.. literalinclude:: examples/login.json
   :language: http

Verwenden
^^^^^^^^^

Das Token kann jetzt für alle folgenden Requests zur Authentisierung verwendet
werden. Dazu muss ein ``Authorization`` Header mit der Authentisierungsmethode
``Bearer`` und dem Token gesetzt werden:

.. sourcecode:: http

  GET /Plone HTTP/1.1
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmdWxsbmFtZSI6IiIsInN1YiI6ImFkbWluIiwiZXhwIjoxNDY0MDQyMTAzfQ.aOyvMwdcIMV6pzC0GYQ3ZMdGaHR1_W7DxT0W0ok4FxI
  Accept: application/json

Erneuern
^^^^^^^^

Standardmässig läuft das Token nach 12 Stunden ab, und muss daher vor Ablauf
erneuert werden. Um das Token zu erneuern kann ein ``POST`` Request auf den
``@login-renew`` Endpoint gemacht werden:

.. sourcecode:: http

    POST /@login-renew HTTP/1.1
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmdWxsbmFtZSI6IiIsInN1YiI6ImFkbWluIiwiZXhwIjoxNDY0MDQyMTAzfQ.aOyvMwdcIMV6pzC0GYQ3ZMdGaHR1_W7DxT0W0ok4FxI
    Accept: application/json

Der Server antwortet mit einem JSON-Objekt welches das neue Token enthält:

.. literalinclude:: examples/login_renew.json
   :language: http


Invalidieren
^^^^^^^^^^^^

Der ``@logout`` endpoint kann verwendet werden, um ein Token zu invalidieren.
Dazu müssen die Tokens jedoch server-seitig persistiert werden.

In der Standardkonfiguration werden Tokens nicht persistiert, und können daher
nicht aktiv invalidiert werden. Wenn sie Bedarf danach haben, aktiv
invalidierbare Tokens auszustellen, können wir dies für Sie konfigurieren.

Der Logout-Request kann dann durchgeführt werden, indem das existierende Token
im ``Authorization`` Header angegeben wird:

.. sourcecode:: http

    POST /@logout HTTP/1.1
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmdWxsbmFtZSI6IiIsInN1YiI6ImFkbWluIiwiZXhwIjoxNDY0MDQyMTAzfQ.aOyvMwdcIMV6pzC0GYQ3ZMdGaHR1_W7DxT0W0ok4FxI
    Accept: application/json

Wenn die Invalidierung erfolgreich war, antwortet der Server mit einer leeren
``204`` Response:

.. literalinclude:: examples/logout.json
   :language: http

