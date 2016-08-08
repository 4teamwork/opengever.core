.. _authentication:

Authentisierung
---------------

Die Authentisierung an der API erfolgt mittels HTTP Basic Auth, unter
Verwendung eines normalen Benutzers welcher die nötigen Berechtigungen für
die gewünschte Operation hat.

Für HTTP Basic Auth muss ein `Authorization` Header im Request gesetzt werden:

.. sourcecode:: http

  GET /ordnungssystem HTTP/1.1
  Authorization: Basic Zm9vYmFyOmZvb2Jhcgo=
  Accept: application/json

Die HTTP Client Libraries bieten üblicherweise Hilfsfunktionen an, um diesen
Header basierend auf Benutzername und Passwort zu generieren.

**Code-Beispiel (Python)**: Session erzeugen und Headers setzen

.. literalinclude:: examples/example_session.py