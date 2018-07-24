OneGov GEVER Release 3
======================

Hauptbestandteil des **Major-Releases 3.0** ist ein Erweiterung des bestehenden Mandantenkonzept.
Mit dem neuen Release wird OneGov GEVER nun noch attraktiver für Lösungen in kleineren
Verwaltungen und Organisationen, u.a. **politische Gemeinden** und **Kirchgemeinden**. Innerhalb
einer einzelnen Installation von OneGov GEVER können dabei beliebig viele Ämter im
gleichen Registraturplan hinterlegt werden. **Organisationsübergreifende Zusammenarbeit**
ist im gleichen Umfang möglich wie es bereits in den früheren Releases im Rahmen von
kantonalen Organisationen möglich war.

|img-release-notes-3.0-1|

Mit dem flexibleren Mandantenkonzept kann nun die Installation optimal an die
Grösse des Kunden angepasst werden. Damit lassen sich Installations- und Betriebskosten
von OneGov GEVER bei kleinen Installationen nochmals deutlich senken.

Mit dem neu eingeführten **Amtswechsler** kann der angemeldete Benutzer zudem sehr
rasch zwischen verschiedenen Rollen hin- und herwechseln. Speziell von Mitarbeitenden
in Gemeinden, die mehrere Funktionen wahrnehmen, wird diese Möglichkeit sehr geschätzt.

Verbesserung der Benutzerführung bei Aufgaben:
----------------------------------------------

|img-release-notes-3.0-2|

Die vielfach gelobte **Einfachheit in der Bedienung** von OneGov GEVER wurde im Bereich
der Aufgaben nochmals verbessert. U.a. wurde das User Interface überarbeitet und
präsentiert sich jetzt noch aufgeräumter:

- Sämtliche Aufgaben-Aktionen wurden als Bedienknöpfe prominenter positioniert;
  so sind häufig genutzte Funktionen mit nur einem Mausklick erreichbar. Zudem wurde
  jede Aktion mit einem aussagekräftigen Icon versehen.

- Aufgaben-Aktionen, die nur für stellvertretende Personen zur Verfügung stehen,
  werden gruppiert in einem Dropdown-Menü dargestellt und sind deshalb besser
  von den übrigen Aktionen unterscheidbar.

- Der Aufgabenverlauf ist übersichtlicher gestaltet und bietet einen raschen
  Überblick über die bisherigen Arbeitsschritte zu einer Aufgabe.

- Alle Aufgabenformulare und -auflistungen wurden vereinheitlicht.

- Separate Icons und Wasserzeichen wurde für Unteraufgaben hinzugefügt (`#542 <https://github.com/4teamwork/opengever.core/issues/542>`_).
  Damit sind Unteraufgaben optisch besser von Hauptaufgaben unterscheidbar.

- Dokumente können neu per Drag'n'Drop zu Aufgaben hinzugefügt werden (`#339 <https://github.com/4teamwork/opengever.core/pull/339>`_).

- Überfällige Aufgaben werden neu in der Übersicht entsprechend markiert (`#333 <https://github.com/4teamwork/opengever.core/issues/333>`_).

- Aufgaben im Eingangskorb können nun wie bei sonstigen Aufgabenauflistungen
  gedruckt und als PDF exportiert werden (`#575 <https://github.com/4teamwork/opengever.core/pull/575>`_).

- Der Statusfilter bei Aufgaben in Jahres-Abschlussordnern wurde entfernt (`#330 <https://github.com/4teamwork/opengever.core/issues/330>`_).

Ordnungssystem (Aktenplan, Registraturplan):
--------------------------------------------

|img-release-notes-3.0-3|

- Die Performance bei der Darstellung wurde deutlich optimiert (`#476 <https://github.com/4teamwork/opengever.core/pull/476>`_). Auch grössere
  Registraturpläne mit mehreren tausend Ordnungspositionen können sehr rasch dargestellt werden.

- Jeder Benutzer kann Ordnungspositionen, in denen er oder sie häufig arbeitet,
  als Favorit markieren. Diese sind dann über den Favoriten-Reiter schnell aufrufbar (`#547 <https://github.com/4teamwork/opengever.core/pull/547>`_).

Weitere Anpassungen:
--------------------

- Sicherheitsoptimierungen: Potentielle XSS-Sicherheitslücken wurden behoben (`#627 <https://github.com/4teamwork/opengever.core/pull/627>`_)

- In der persönlichen Übersicht wird nun der angemeldete Benutzer angezeigt (`#348 <https://github.com/4teamwork/opengever.core/pull/348>`_).

- Die Benutzerführung zum Herunterladen einer Datei wurde verbessert.
  So kann nun jeder Benutzer selber einstellen, ob das Hinweis-Fenster "Kopie-Herunterladen"
  immer angezeigt werden soll (`#425 <https://github.com/4teamwork/opengever.core/pull/425>`_). Dokumente, die nicht digital verfügbar sind,
  können nicht mehr heruntergeladen werden (`#463 <https://github.com/4teamwork/opengever.core/issues/463>`_, `#568 <https://github.com/4teamwork/opengever.core/pull/568>`_)

- Der Dokument-Checkin wurde vereinfacht, Dokumente können neu direkt ohne
  Kommentar eingecheckt werden (`#280 <https://github.com/4teamwork/opengever.core/pull/280>`_).

- DocProperties in DOCX-Dokumenten werden neu bei jedem Check-In/Check-Out
  aktualisiert. Beim Aktualisieren wird ein Journaleintrag erstellt (`#551 <https://github.com/4teamwork/opengever.core/pull/551>`_).

- Gruppenmitglieder werden beim Auflisten neu alphabetisch sortiert (`#360 <https://github.com/4teamwork/opengever.core/issues/360>`_).

- Allgemeine Verbesserungen im Responsive Design.

- Der Referenz-Präfix Manager ermöglicht nun auch das Freigeben
  von bereits entfernten Ordnungspositionen (`#527 <https://github.com/4teamwork/opengever.core/pull/527>`_).

- Diverse kleinere allgemeine Korrekturen, Verbesserungen und Anpassungen.

.. |img-release-notes-3.0-1| image:: ../../_static/img/img-release-notes-3.0-1.png
.. |img-release-notes-3.0-2| image:: ../../_static/img/img-release-notes-3.0-2.png
.. |img-release-notes-3.0-3| image:: ../../_static/img/img-release-notes-3.0-3.png

.. disqus::
