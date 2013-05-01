opengever.repository
====================

Notizen
-------


- RepositoryFolder = Rubrik, Registraturposition
- aendern einer Position: Unter-Rubriken werden nicht aktualisiert (Navi, Catalog)
- Title ueberschreiben: http://n2.nabble.com/Dexterity-computed-fields-tp3498400ef293351.html
- INameFromTitle fuer Rubrik reparieren: contex.title wird verwendet
- record position:
    - keine duplikate
    - >0
    - i18n: Record Position = Aktenzeichen -> reference_number

- i18n: Geben Sie de >>M<< Archivwert an
- Klassifizierung:
  - getter mit acquisition
  - events beim aendern der parents
  - Klassifizierung: Klassifizierung wird mit Acquisition vom Container uebernommen und kann noch mehr eingeschraenkt werden, nicht aber weniger
  - Datenschutzstufe:
  - [no - yes] erlaubt, [yes - no] nicht erlaubt
  - nicht required, vererbbar
  - oeffentlichkeitsstatus: etwa gleich wie Datenschutzstufe
  - Archivwuerdigkeit:
  (1) Noch nicht bewertet (default)
  (2) anbieten (weil teilweise archivwuerdig?)
  (3) Archivwuerdig
  (3) Nicht archivwuerdig
  (3) Sampling


  - Schutzfrist & Aufbewahrungsdauer:
    - Kann auf tieferer Ebene kleiner sein, nicht aber groesser
    - nicht required, vererbbar

- Welches ist die erste Position einer Rubrik? 0 oder 1? (momentan 0)
  - 1
- Darf die Position bei bestehenden Rubriken geaendert werden?
  - ja
- ueber wiviele Stufen werden die Positionen im Titel angezeigt? (Bund: 9)
  - Nicht limitiert
- Wo / welche Typen sind in der Rubrik hinzufuegbar?
  - Rubrik, Dossier
  - Wenn Rubrik in Rubrik enthalten, kein Dossier hinzufuegbar


