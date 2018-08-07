OneGov GEVER Release 2017.4
===========================

Dieser Release bietet erweiterte Unterstützung für Outlook-E-Mail-Formate.

E-Mails
-------

Bereits seit dem letzten Release werden E-Mail-Inhalte nicht nur im
archivtauglichen EML-Format, sondern auch als MSG-Dateien von Microsoft
Outlook abgespeichert. Speziell in Verbindung mit dem neuen Outlook-Addin
"OneGov GEVER Drag'n'Drop" wird die tägliche Arbeit mit OneGov GEVER
so noch attraktiver. Neu wird nun auch, falls vorhanden, die MSG-Datei für die
PDF-Generierung inkl. Vorschau verwendet, womit eine höhere Darstellungsqualität
erreicht wird. Ausserdem wird dieses Format  standardmässig zum Download angeboten,
so dass abgelegte E-Mails per Mausklick direkt in Outlook geöffnet werden können.

Wie bisher werden alle E-Mail-Inhalte von OneGov GEVER automatisch auch im
EML-Format abgelegt, das dann für die Aussonderung verwendet werden kann.

Migrationsschnittstelle
-----------------------

Das Migrations-Framework von OneGov GEVER (siehe Spezifikation `OGGBundle <https://docs.onegovgever.ch/dev-manual/oggbundle/>`_ ) unterstützt neu
auch den Import von \*.msg Dateien. Zudem wurden kleinere Anpassungen und Korrekturen an dieser Schnittstelle vorgenommen.

.. disqus::
