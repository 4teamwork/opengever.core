OneGov GEVER Release 3.11
=========================

Mit dem Release 3.11 steht nun die RESTful API in OneGov GEVER zur Verfügung und
muss nicht mehr als Zusatzmodul installiert und aktiviert werden. In der Standardkonfiguration
von OneGov GEVER ist die API nicht aktiviert, kann aber sehr einfach eingerichtet werden.

Ausserdem beinhaltet dieser Release Performance-Verbesserungen, die anlässlich des
letzten `FEDEX Days von OneGov GEVER <https://www.4teamwork.ch/blog/ergebnisse-onegov-gever-fedex-day-2016>`_ entwickelt wurden. Natürlich beinhaltet auch
dieser Release weitere allgemeine Anpassungen und Korrekturen.

RESTful API
-----------

Die neue OneGov GEVER API ist eine `RESTful <https://de.wikipedia.org/wiki/Representational_State_Transfer>`_ HTTP API. Mit dieser API ist es möglich, aus
beliebigen Drittanwendungen auf OneGov GEVER zuzugreifen, um z.B. neue Inhalte
(Dossiers, Dokumente, etc.) zu erzeugen oder nach bestehenden Inhalten zu suchen.
Im Prinzip stehen alle Funktionen von OneGov GEVER neu auch über diesen Webservice
zur Verfügung. So können Fachanwendungen ihre Dokumente und Daten automatisiert direkt
in OneGov GEVER ablegen, ohne dass zusätzlich neue Schnittstellen entwickelt werden müssen.
Dabei bleibt es dem Integrator freigestellt, welche Programmiersprache er oder sie einsetzen
möchte, um auf OneGov GEVER zuzugreifen. Java, C++, .NET, Visual Basic, PHP, Python oder Ruby
sind eine kleine Auswahl von Programmiersprachen, die dazu verwendet werden können.

Weitere Informationen zur API können der öffentlich zugänglichen `OneGov GEVER Entwicklerdokumentation <https://docs.onegovgever.ch/dev-manual/api/basics/>`_
entnommen werden. Die Dokumentation richtet sich in erster Linie an Entwickler und
Integratoren von Drittanwendungen.

Gerne beraten wir Sie bei technischen Fragen, wenn Sie die Webschnittstelle verwenden möchten.

Verbesserungen und Anpassungen
------------------------------

- Es wurden im Bereich Performance zahlreiche Leistungssteigerungen erzielt, u.a. beim
  Erstellen neuer Inhalte sowie durch optimiertes Caching von Webinhalten.
  Der Fussbereich einer Seite (Footer) wird nun effizienter dargestellt.

- Verbesserte Sortierung von Referenznummern bei Ordnungspositionen.

- Neu steht die `DocProperty ogg.document.document_type <https://docs.onegovgever.ch/admin-manual/docproperties/>`_ zur Verfügung.

- Das Autocomplete Widget beim Erstellen eines manuellen Journaleintrags schränkt
  die Auswahl der Verweismöglichkeiten auf das aktive Dossier ein.

.. disqus::
