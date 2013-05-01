Opengever development installation
==================================

Die folgende Installationsanleitung beschreibt die Installation einer Mehr-Mandanten Installation von Opengever mit OGDS.

Einrichten SQL(OGDS)
--------------------
Das neue OGDS funktioniert mit einer SQL-Anbindung und kann folgendermassen installiert werden:

Installation des Buildouts aus git  gitolite@git.4teamwork.ch:opengever/buildout
Im buildout.cfg muss in instance1 ein DB-egg hinzugefuegt werden (opengever.sqliteconfig oder opengever.mysqlconfig)
Lokales MySQL Installieren (aus homebrew, ports oder selbst herunterladen, je nach Geschmack)
Das Einrichten der Datenbank und des Users kann ueber das SQL-Script gemacht werden:

$ cd src/opengever.ogds.mysql/opengever/ogds/mysql/
$ mysql -uroot -p < create_database.sql

Site mandant1
-------------
Neue Plone-Site mandant1 erstellen (Sollte dann unter http://localhost:8080/mandant1 erreichbar sein)
mandant1: Import opengever.policy.base
mandant1: Import opengever.ogds.base : example users / clients
mandant1: portal_registry : "opengever ogds base interfaces IClientConfiguration client_id" auf mandant1 setzen (dieser ist bereits konfiguriert im mysql)
mandant1: Import opengever.examplecontent: Developer

Site mandant2
-------------
Neue Plone-Site mandant2 erstellen (Sollte dann unter http://127.0.0.1:8080/mandant2 erreichbar sein)
mandant2: Import opengever.policy.base
mandant2: Import opengever.ogds.base : example users / clients
mandant2: portal_registry : "opengever ogds base interfaces IClientConfiguration client_id" auf mandant2 setzen (dieser ist bereits konfiguriert im mysql)

Erstellte User (passwort jeweils demo09:

hugo.boss (mandant1)
peter.muster (mandant2)
franz.michel (mandant1, mandant2)

Erstellte Gruppen:
og_mandant1_users
og_mandant1_inbox
og_mandant2_users
og_mandant2_inbox

Die Berechtigungen werden NICHT gesetzt! Dies muss manuell gemacht werden.
