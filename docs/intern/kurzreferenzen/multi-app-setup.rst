Alternative Apps im neuen Frontend anzeigen
===========================================
Der ``@config``-Endpoint stellt im Attribut ``apps_url`` eine URL zum Abfragen von verfügbaren Applikationen zur Verfügung. Das Frontend führt einen GET request auf die URL aus und zeigt die zurückgegebenen Applikationen im App-Switcher an.

Die ``apps_url`` kann über eine Umgebungsvariable gesetzt werden:

``export APPS_ENDPOINT_URL=htt://example.com/portal/api/apps``
