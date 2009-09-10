opengever.repository
====================


Diskussion
----------



Notizen
-------

* RepositoryFolder = Rubrik, Registraturposition
* Ändern einer Position: Unter-Rubriken werden nicht aktualisiert (Navi, Catalog)
* Title überschreiben: http://n2.nabble.com/Dexterity-computed-fields-tp3498400ef293351.html


To Do
-----

- INameFromTitle für Rubrik reparieren: contex.title wird verwendet
- record position: keine duplikate und >0
- i18n: Geben Sie de>>M<< Archivwert an
- Klassifizierung:
  - Klassifizierung: Klassifizierung wird mit Acquisition vom Container übernommen und kann noch mehr eingeschränkt werden, nicht aber weniger
  - Datenschutzstufe:
    - [no » yes] erlaubt, [yes » no] nicht erlaubt
    - nicht required, vererbbar
  - Öffentlichkeitsstatus: etwa gleich wie Datenschutzstufe
  - Archivwürdigkeit:
    - (1) Noch nicht bewertet (default)
    - (2) anbieten (weil teilweise archivwürdig?)
    - (3) Archivwürdig
    - (3) Nicht archivwürdig
    - (3) Sampling
  - Schutzfrist & Aufbewahrungsdauer:
    - Kann auf tieferer Ebene kleiner sein, nicht aber grösser
    - nicht required, vererbbar
- Welches ist die erste Position einer Rubrik? 0 oder 1? (momentan 0)
  - 1
- Darf die Position bei bestehenden Rubriken geändert werden?
  - ja
- Über wiviele Stufen werden die Positionen im Titel angezeigt? (Bund: 9)
  - Nicht limitiert
- Wo / welche Typen sind in der Rubrik hinzufügbar?
  - Rubrik, Dossier
  - Wenn Rubrik in Rubrik enthalten, kein Dossier hinzufügbar
- i18n: Record Position = Aktenzeichen » reference_number


