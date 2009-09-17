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
- record position:
    - keine duplikate
    X >0
    X i18n: Record Position = Aktenzeichen » reference_number
X i18n: Geben Sie de>>M<< Archivwert an
- Klassifizierung:
  - Klassifizierung: Klassifizierung wird mit Acquisition vom Container übernommen und kann noch mehr eingeschränkt werden, nicht aber weniger
  X Datenschutzstufe:
    X [no » yes] erlaubt, [yes » no] nicht erlaubt
    X nicht required, vererbbar
  X Öffentlichkeitsstatus: etwa gleich wie Datenschutzstufe
  X Archivwürdigkeit:
    X (1) Noch nicht bewertet (default)
    X (2) anbieten (weil teilweise archivwürdig?)
    X (3) Archivwürdig
    X (3) Nicht archivwürdig
    X (3) Sampling
  - Schutzfrist & Aufbewahrungsdauer:
    - Kann auf tieferer Ebene kleiner sein, nicht aber grösser
    - nicht required, vererbbar
X Welches ist die erste Position einer Rubrik? 0 oder 1? (momentan 0)
  X 1
X Darf die Position bei bestehenden Rubriken geändert werden?
  X ja
X Über wiviele Stufen werden die Positionen im Titel angezeigt? (Bund: 9)
  X Nicht limitiert
- Wo / welche Typen sind in der Rubrik hinzufügbar?
  - Rubrik, Dossier
  - Wenn Rubrik in Rubrik enthalten, kein Dossier hinzufügbar


