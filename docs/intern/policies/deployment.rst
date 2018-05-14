Deployment
==========

Für das deployment muss im Betriebs-Tracker ein Ticket erstellt werden.
"GEVER deployment Einrichten" mit den nötigen Daten in der Beschreibung sollten genügen.
Benötigt werden:
- LDAP Ast und Gruppen (diese Angaben wurden bei der Erstellung der Policy gemacht)
- Portal
- DNS Eintrag
- Bumblebee

Die generierte buildout-Datei im repository ist mit den Angaben des im Betriebs-Tracker erstellten Tickets anzupassen.
Erst mit diesen Anpassungen kann die policy installiert werden.

Auf dem zu deployenden repository ist die policy zu clonen.
Achte darauf, dass der Name des Zielordners dem Muster der anderen Deployments entspricht.
Vergiss nicht, die Postgresql Datenbank mit ``createdb`` zu erstellen.

Führe danach die Installation des GEVERs aus.
Der Pfad zum Python-Executable kann einer Instanz einer bereits eingerichteten policy entnommen werden.

Nach dem Buildout kann ``bin/supervisord`` gestartet werden und mit ``bin/supervisorctl`` die einzelnen Instanzen gestartet werden.

Das GEVER kann nun mittels SSH-Tunnel noch installiert werden.
