.. _policies-deployment:

Deployment
===================================

Für das Deployment werden die Arbeiten im entsprechenden Jira-Ticket koordiniert.
Es müssen folgende Angaben im Delivery Team geklärt/kommuniziert werden:

 - Domain: [name].onegovgever.ch *e.g.: 4teamwork.onegovgever.ch*
 - Server: [name] *e.g.: ipet*
 - Deployment: [number] *e.g.: 09*
 - Plone-Site id: [id] *e.g.: 4tw*
 - postgres-db: ogds_[name] *e.g.: ogds_4teamwork*
 - LDAP Ast `ou=[name],ou=OneGovGEVER,dc=4teamwork,dc=ch` einrichten

Weitere Dinge, die man erledigen muss:

 - Initiale Gruppen: *e.g.: [name]_admins, [name]_users, [name]_inbox*
 - Portal einrichten
 - DNS, Haproxy etc. konfigurieren
 - Bumblebee einrichten und Secret mitteilen

Die generierte buildout-Datei im repository ist mit den Angaben des im Betriebs-Tracker erstellten Tickets anzupassen.
Erst mit diesen Anpassungen kann die policy installiert werden.

Auf dem zu deployenden repository ist die policy zu clonen.
Achte darauf, dass der Name des Zielordners dem Muster der anderen Deployments entspricht.
Vergiss nicht, die Postgresql Datenbank mit ``createdb`` zu erstellen.

Führe danach die Installation des GEVERs aus.
Der Pfad zum Python-Executable kann einer Instanz einer bereits eingerichteten policy entnommen werden.

Nach dem Buildout kann ``bin/supervisord`` gestartet werden und mit ``bin/supervisorctl`` die einzelnen Instanzen gestartet werden.

Das GEVER kann nun mittels SSH-Tunnel noch installiert werden.
