Schnittstellen
==============

Die folgende Kapitel beschreiben die zur Verfügung stehenden Schnittstellen und Anbindungen von Drittprodukten.


REST API
--------
Für die Anbindung von Drittprodukten, wird von OneGov GEVER eine REST Schnittstelle angeboten. Diese ist in der `API Dokumentation <https://docs.onegovgever.ch/dev-manual/api/>`_ ausführlich dokumentiert inkl. verschiedenen Anwendungsbeispielen.


eCH-0039 / eCH-9147
-------------------

OneGov GEVER unterstützt die Schnittstellen `eCH-0147 <https://www.ech.ch/vechweb/page?p=dossier&documentNumber=eCH-0147>`_ und `eCH-0039 <https://www.ech.ch/vechweb/page?p=dossier&documentNumber=eCH-0039>`_.

Es stehen Aktionen zur Verfügung für den Export und Import von Dossiers oder einzelnen Dokumente mittels eCH-0147 Nachricht. Eine genaue Beschreibung der Funktionalität befindet sich im `User Manaual <https://docs.onegovgever.ch/user-manual/dossiers/ech-schnittstelle/>`_.


Aussonderungsprozess nach eCH-0160
----------------------------------

OneGov GEVER bietet Unterstützung für den kompletten Aussonderungsprozess, inkl. dem Abliefern von Dossiers nach `eCH-0160 Standard <https://www.ech.ch/vechweb/page?p=dossier&documentNumber=eCH-0160>`_. Der Aussonderungsprozess ist in der Admin-Dokumentation im Kapitel `Aussonderung <https://docs.onegovgever.ch/admin-manual/aussonderung/>`_ ausführlich dokumentiert.


Kontakte
--------

Mit der Entwicklung des neuen Kontaktmoduls, wurde auch ein Duplikations-Mechanismus entwickelt, welche es erlaubt, externe Datenbanken oder Applikationen als Datenquellen anzubinden.

So werden beispielsweise im Staatsarchiv des Kanton BS die Kontaktdaten aus der ScopePartner Datenbank dupliziert und stehen im GEVER für den Briefversand, Dossierbeteiligungen etc zur Verfügung.

.. note::

    Folgendes gilt es bei der Verwendung des neuen Kontaktmoduls zu beachten:
     - Zurzeit wird noch kein Möglichkeit für die Bearbeitung von Kontakten angeboten
     - Die Kontakten werden global, also pro Mandantenverbund verwaltet, und sind demnach für alle Benutzer des Verbunds ersichtlich


Migrationsschnittstelle OGGBundle
---------------------------------

Im Rahmen der GEVER Einführung im Kanton SG und den damit verbundenen Datenmigrationen, wurde das JSON-Zwischenformat OGGBundle spezifiziert und entwickelt. Die Datenschnittstelle ermöglicht eine Migration von Ordnungssystemen, Dossiers und Dokumente, wobei auch ein Import in ein bestehendes Ordnungssystem möglich ist. Weitere Details finden sie in der `Spezifikation von OggBundle <https://docs.onegovgever.ch//dev-manual/oggbundle/>`_.
