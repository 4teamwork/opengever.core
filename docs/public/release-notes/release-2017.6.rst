OneGov GEVER Release 2017.6
===========================

Im Release 2017.6 werden diverse generelle Korrekturen am System vorgenommen
sowie zusätzliche Funktionen bei der Migrationsschnittstelle,
bei den Dokumenten sowie bei der RESTful API ermöglicht.

Korrekturen
-----------

Bei den nachstehend aufgelisteten Punkten wurden kleinere Korrekturen vorgenommen:

- Import / Export bei der Schnittstelle eCH-0147/39

- Blättern durch Suchresultate in PDF Vorschau

- Bearbeitung von Dossiers, bei welchen inaktive Benutzer federführend sind

- Versand von Dokumenten im Eingangskorb via Outlook

Migration
---------

- Neu ist es möglich, aus Drittsystemen (z.B. einem Filesystem) nachträglich
  Daten in OneGov GEVER zu migrieren.

- Des weiteren kann mittels dem `OGG Bundle Validator <https://ogg.4teamwork.ch/>`_ im Voraus geprüft werden,
  ob ein im Excel vorbereitetes Ordnungssystem dem Spezifikationen von
  OneGov GEVER entspricht. Falls die Validierung nicht gelingt, wird die genaue
  Fehlermeldung angezeigt, um das Ordnungssystem auf diesen Punkt nochmals zu überarbeiten.

- Zudem ist nun auch eine automatisierte Migration von Benutzern möglich.

Dokumente
---------

- Technische Verbesserungen bei der Versions-Erstellung von Dokumenten

- Die Gallerie-Ansicht ist neu nach "zuletzt bearbeitet" (last modified) sortiert

- Dokumente können neu vom Eingangkorb direkt in ein Dossier verschoben werden

RESTful API
-----------

- Unterstützung von Checkin/Checkout-Prozess inkl. Locking

- Durch die Erweiterung der Scanner Schnittstelle, wir ein Upload von Dokumenten
  in OneGov GEVER von einem Scanner-Gerät möglich. Mehr Details dazu finden
  Sie in der `Dokumentation <https://docs.onegovgever.ch/dev-manual/api/scanin/?highlight=scann>`_ .

.. disqus::
