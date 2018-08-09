OneGov GEVER Release 3.6
========================

Dieser Release steht ganz im Zeichen der neuen **Sitzungs- und Protokollverwaltung**
und bringt zahlreiche Erweiterungen und Korrekturen. Dabei konnten viele Rückmeldungen
aus dem Feedback-Forum berücksichtigt werden.

Neue Features
-------------

- Der Workflow von Traktanden wurde so erweitert, dass abgeschlossene Traktanden zur
  Überarbeitung wieder geöffnet werden können. Beim erneuten Abschliessen werden die
  bestehenden Protokollauszüge automatisch aktualisiert.

- In den Wordvorlagen für Protokolle und Protokollauszüge steht nun auch der Titel
  der Ordnungsposition zu einem Antrag als Protokollvariable zur Verfügung.

- Der Sitzungstitel kann neu bearbeitet werden. Standardmässig wird der Name des
  Gremiums und das Sitzungsdatum als Titel vorgeschlagen.

- Die Meldung zu gesperrten Protokoll-Dokumenten wurde verbessert. Neu wird darauf
  hingewiesen, dass das Dokument durch eine Sitzung gesperrt wurde.

- Dokumente, die in einer älteren Version eingereicht wurden, können neu direkt in
  der Antragsansicht aktualisiert werden.

- Statt allgemein von "Kommission" zu sprechen, werden neu die treffenderen Begriffe
  "Gremium" und "Gremien" verwendet.

- Um die rasche Navigation innerhalb der Sitzungs- und Protokollverwaltung zu
  erleichtern, werden zusätzliche Links angezeigt:

  - Die zugehörige Sitzung bei traktandierten Anträgen ist verlinkt

  - Das Gremium sowie das Dossier des Antragstellers bei eingereichten Anträge ist verlinkt

  - In der Sitzungsansicht wird zu den nicht traktandierten Anträgen verlinkt

- Die Dateinamen der Protokollauszüge setzen sich neu aus Antragstitel, Sitzungstitel
  und Sitzungsdatum zusammen.

- Das Dropdown-Menü zur Auswahl eines Gremiums ist nun durchsuchbar.

- Das Feld "Standort" einer Sitzung wurde zu "Sitzungsort" umbenannt.

- Bei Word-Vorlagen zu Protokollen und Protokollauszügen wird nun, wie bei Dokumenten
  allgemein, der Reiter "Versionen" eingeblendet.

- Einem Antrag angehängte Beilagen werden übersichtlicher auf der Antragsansicht dargestellt.

- Der Reiter "Anträge" stellt zusätzlich die Spalten "Laufnummer" und "Sitzung" dar.
  Die Spalten "Ausgangslage" und "Antrag" wurden entfernt.

Korrekturen
-----------

- Verbesserte Konfliktbehandlung beim Speichern eines Protokolls. Es wird
  verhindert, dass ein Benutzer neuere Protokollversionen versehentlich überschreiben kann.

- Die Performance für Deployments mit sehr vielen Organisationseinheiten wurde optimiert.

- Das Protokoll kann nicht mehr gespeichert werden, wenn es von einem anderen
  Benutzer zur Bearbeitung gesperrt wurde.

- Konflikte bei der Protokollbearbeitung werden beim Speichern angezeigt.

- Beschlossene Traktanden können in der Protokollansicht nicht mehr bearbeitet werden.

- Beim Arbeiten mit dem WYSIWYG-Editor wird verhindert, dass ungültige
  HTML-Elemente per Copy&Paste eingefügt werden können (Weblinks, Zitate, Dateien, Bilder).

- Die Antragsansicht wurde überarbeitet.

Allgemeine Anpassungen
----------------------

- Weblinks in Office-Dokumenten, die auf OneGov GEVER zeigen, werden nun ohne
  Fehlermeldung im Webbrowser geöffnet.

- Beim Versenden von Dokumenten aus geschlossenen Dossiers ist es nicht mehr
  möglich, gleichzeitig eine Kopie des E-Mails im Dossier abzulegen.

- Die französische Übersetzung von "In Bearbeitung" wird neu
  mit "En cours de traitement" übersetzt (gemäss eCH-0039).

.. disqus::
