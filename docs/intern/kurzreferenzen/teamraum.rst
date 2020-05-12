.. _teamraum-connect:

Teamraum einbinden
==================
Der Teamraum wird als eigenes Deployment betrieben und wird in GEVER integriert.

Da die Kommunikation immer nur von GEVER nach Teamraum (nie umgekehrt) stattfinden darf, wird GEVER dementsprechend als Client gegenüber Teamraum auftreten. Es wird der von `ftw.tokenauth <https://github.com/4teamwork/ftw.tokenauth>`__ unterstützte OAuth2 Flow verwendet, um Requests von GEVER an den Teamraum zu authentisieren.

Service-Benutzer erstellen
--------------------------
Erstellen Sie einen Benutzer auf der Teamraum Seite mit den Rollen ``ServiceKeyUser`` und ``Impersonator``.

Service-Schlüssel ausstellen
----------------------------
Erstellen Sie im Teamraum einen Service-Key für das GEVER gem. Dokumentation von `ftw.tokenauth <https://github.com/4teamwork/ftw.tokenauth#1-issue-service-key>`__

Service-Schlüssel im GEVER registrieren
---------------------------------------
Der von `ftw.tokenauth <https://github.com/4teamwork/ftw.tokenauth>`__ generierte Schlüssel welcher zum Download angeboten wird, muss nach dem Erstellen im GEVER zur Verfügung gestellt werden.

GEVER sucht im Ordner ``~/.opengever/ftw_tokenauth_keys`` nach entsprechenden Schlüsseln.

Erstellen Sie ein ``.json`` z.B. ``teamraum_dev.json`` mit dem gesamten Schlüssel als Inhalt. GEVER wird später anhand der ``token_uri`` im Schlüssel automatisch das korrekte Schlüssel-File für den Request auf den Teamraum verwenden.

Teamraum-URL definieren
-----------------------
Damit GEVER weiss, wo sich die Teamraum-Installation befindet, muss die URL in den Umgebungsvariablen konfiguriert werden:

``export TEAMRAUM_URL=http://example.com``

**Hinweis** Das ``development.cfg`` setzt die Umgebungsvariable bereits auf ``http://localhost:8080/fd``. Das GEVER und die Teamraum installation ist somit das gleiche Deployment.

Feature aktivieren
------------------
Nachdem die Verbindung konfiguriert ist, muss das Feature für den Teamraum-Client in der Plone-Registry unter dem Key: ``IWorkspaceClientSettings`` aktiviert werden.

**Achtung**: Die Verbindung funktioniert nicht mit dem zopemaster: https://github.com/4teamwork/ftw.tokenauth/blob/master/ftw/tokenauth/pas/plugin.py#L254

Berechtigung für Benutzer
-------------------------
Grundsätzlich steht nun die Verbindung von GEVER zum Teamraum.

Damit nun ein Benutzer die Verbindung auch verwenden darf, benötigt dieser die Rolle ``WorkspaceClientUser``.
