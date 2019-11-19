OneGov GEVER Release 2019.4
===========================

Der Release 2019.4 steht ganz im Zeichen des neuen GEVER Frontends. Zahlreiche API Endpoints wurden entwickelt oder erweitert, um OneGov GEVER bereit für das neue User Interface zu machen.

Mit dem Release 2019.4 besteht nun zum ersten Mal die Möglichkeit das neue Frontend auszuprobieren und zu testen.

Des Weiteren gab es Verbesserungen und Erweiterungen vor allem in den Bereichen Benachrichtigungen, Aussonderung und der Migrationsschnittstelle.

Benachrichtigungen und Erinnerungen
-----------------------------------
In den Benachrichtigungseinstellung stehen jedem Benutzer zwei neue Konfigurationsoptionen zur Verfügung. Einerseits kann definiert werden, ob er über eigene Aktion benachrichtigt werden soll, anderseits können Benachrichtigungen als Eingangskorbmitglied deaktiviert werden.

Ausserdem können bei Aufgaben neu auch Erinnerungen für ein spezifisches Datum definiert werden.

Migrationsschnittstelle
-----------------------
Unsere Migrationsschnittstelle OGGBundle hat folgende Erweiterungen erhalten:

- Die Migrationsschnittstelle unterstützt nun auch den Import von Mails im ``*.msg`` Format.
- Neu können Bundles für einen gesamtem Dateisystempfad generiert werden.

Aussonderung
------------
Das Aussonderungsmodul unterstützt neu den automatischen Transport eines SIP Packages auf eine entsprechende Aussonderugnsplatform.

Ebenfalls kann nun definiert werden, für welche Dateitypen eine PDF Repräsentation als Archivdatei generiert und verwendet werden soll. Desweitern enhalten die SIP Packages neben der Archivdatei neu auch die Originaldatei.

Erfassung von Sitzungs-Perioden in der SPV:
-------------------------------------------
Neu können Sitzungs-Perioden summarisch im Voraus erfasst werden. Die Restriktion von nur einer aktiven Periode wurde aufgehoben. Bei Sitzungsabschluss wird die zugehörige Periode einer Sitzung aufgrund des Sitzungsdatums ausgewählt.


Sonstiges und Bugfixes
----------------------
- Neu stehen auch Docproperties für den Dokumentersteller zur Verfügung.
- Dossiers und Subdossiers werden neu in den Inhaltsstatistiken getrennt aufgezeichnet und dargestellt.
- Änderungen an einem Dokument werden nicht mehr einzeln journalisiert, sondern nur noch das Einchecken bzw. Erstellen einer neuen Version.
- Die Berechtigung wird beim Ablehnen einer Aufgaben nun korrekt entzogen.
- Performanceverbesserungen bei der Auswahl von einzelnen Schlagworten aus einem grossen Schlagwortkatalog.
- Signierte Mails im ``*.p7m`` Format können neu auch in GEVER abgelegt werden inkl. entsprechender PDF-Vorschau.
- Die Bezeichnungen des Feldes Datenschutz und dessen Werte wurden vereinheitlicht.
