OneGov GEVER Release 2020.1
===========================

Im Release 2020.1 wurde die GEVER API noch stark weiterentwickelt. Anpassungen an den existierenden Endpoints wurden unternommen, um die Weiterentwicklung des neuen GEVER Frontends zu unterstützen. Es gab auch neue Endpoints, um die Kommunikation zwischen OneGov GEVER und dem neuen Teamraum zu ermöglichen.


OfficeConnector Support
-----------------------

OfficeConnector wird ab diesem Release nur noch über die REST-API mit GEVER kommunizieren.
Dies führt zu einer Performanceverbesserung für Kunden, die dieses Feature noch nicht aktiviert hatten. GEVER wird aber nur noch OfficeConnector ab Version 1.9.0 unterstützen (wir empfehlen die neuste verfügbare Version zu verwenden).


Neue Funktionalitäten in der SPV
--------------------------------
- Verschieben von Anträgen wurde ermöglicht.
- Neu ist es möglich, direkt aus einem Antrag eine Aufgabe zu erstellen.
- Neu können Anhänge zu Anträgen aus der Sitzungsansicht bearbeitet werden.


Erweiterung OGG-Bundle
----------------------
Die Datenschnittstelle OGG-Bundle zur Migration wurde erweitert und kann nun
mehr Metadaten setzen, dies ist insbesondere bei Migrationen ab
Windows-Dateisystemen nützlich.

Sonstiges und Bugfixes
----------------------
- Eine Performanceverbesserung von Dossierabschluss wurde eingeführt.
- Berechtigungen von Administratoren wurden angepasst um Probleme mit Dossier stornieren und dem Hinzufügen von Schlagwörtern zu beheben.
