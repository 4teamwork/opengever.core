Teamraum einbinden
==================
Der Teamraum wird als eigenes Deployment betrieben und wird in GEVER integriert.

Da die Kommunikation immer nur von GEVER nach Teamraum (nie umgekehrt) stattfinden darf, wird GEVER dementsprechend als Client gegenüber Teamraum auftreten. Es wird der von `ftw.tokenauth <https://github.com/4teamwork/ftw.tokenauth>`__ unterstützte OAuth2 Flow verwendet, um Requests von GEVER an den Teamraum zu authentisieren.

Service-Benutzer erstellen
--------------------------
Erstellen Sie einen Benutzer sowohl auf GEVER wie auch auf Teamraum Seite mit den Rollen ``ServiceKeyUser`` und ``Impersonator``.

Service-Schlüssel ausstellen
----------------------------
Erstellen Sie im Teamraum einen Service-Key für das GEVER gem. Dokumentation von `ftw.tokenauth <https://github.com/4teamwork/ftw.tokenauth#1-issue-service-key>`__

Service-Schlüssel im GEVER registrieren
---------------------------------------
Der von `ftw.tokenauth <https://github.com/4teamwork/ftw.tokenauth>`__ generierte Schlüssel welcher zum Download angeboten wird, muss nach dem Erstellen im GEVER zur Verfügung gestellt werden.

GEVER sucht im Ordner ``~/.opengever/ftw_tokenauth_keys`` nach entsprechenden Schlüsseln.

Erstellen Sie ein ``.json`` z.B. ``teamraum_dev.json`` mit dem gesamten Schlüssel als Inhalt. GEVER wird später anhand der ``token_uri`` im Schlüssel automatisch das korrekte Schlüssel-File für den Request auf den Teamraum verwenden.
