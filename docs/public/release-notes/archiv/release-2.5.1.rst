OneGov GEVER Release 2.5.1
==========================

Bugfixes und kleine Anpassungen
-------------------------------

- Beim E-Mail-Versand von Dokumenten aus OneGov GEVER wurden im versandten E-Mail
  die MIME Parts nicht in der richtigen Reihenfolge angeordnet. Dies führte bei
  gewissen Mailprogrammen (z.B. Novell GroupWise) zu Problemen bei der Darstellung
  dieser E-Mails. Die MIME Parts werden jetzt in jedem Fall in der richtigen
  Reihenfolge angeordnet (zuerst Text-Parts, dann Attachment-Parts).

- Ein Fehler im Umgang mit Objektreferenzen beim Zurücksetzen einer Dokumentversion wurde behoben.

- Beim E-Mail-Versand von Dokumenten, welche Umlaute im Dateinamen enthalten
  und keinen Titel gesetzt haben, kam es zu Codierungsproblemen bei den Dateinamen.
  Da für die Codierung von Sonderzeichen in Dateinamen von E-Mail-Anhängen wie
  auch Datei-Uploads kein einheitlicher Standard existiert und die Implementierungen
  auf Seiten der E-Mail Clients bzw. Webbrowser drastisch variieren, wurde folgendes
  Verhalten umgesetzt: Beim Upload von Dateien in OneGov GEVER wird nun in jedem Fall der Dateiname
  normalisiert, also bestehende Sonderzeichen ersetzt oder umgeschrieben. Z.B.
  wird der Dateiname "flückiger.pdf" zu "flueckiger.pdf".

- Das Verschieben von abgeschlossenen Weiterleitungen in den entsprechenden
  Jahresordner hat in einem bestimmten Fall (mandanteninterne Weiterleitung wird
  direkt abgeschlossen) nicht funktioniert. Dies wurde korrigiert.

- Erstellen von Journaleinträgen für den Download einer Dokument-Kopie.

- Ein Fehler beim Stornieren von bestimmten Dossiers wurde behoben.

- Die Aufgabenübersicht wurde so angepasst, dass Administratoren in
  jedem Fall klickbare Links auf alle Aufgaben sehen.

- Mit dem Release 2.5 wurde eine Anpassung eingeführt, die bei Downloads einer
  Dokumentenkopie einen Hinweis anzeigt, dass es sich dabei um eine Kopie des
  Dokuments handelt. Auf der Seite mit den Dokument-Eigenschaften wird nun dieser Hinweis auch angezeigt.

- Fine-tuning typographischer Details des Dossier-Deckblatts.

- Ein Fehler beim Mutieren des Titels von E-Mails wurde behoben.

- Ein Fehler beim Erledigen von mandantenübergreifenden Aufgaben wurde behoben.

- Ein Fehler beim Setzen der Defaultwerte im Formular zum
  Extrahieren von Mail-Anhängen wurde behoben.

- Das Erzeugen von doppelten Journaleinträgen beim Hinzufügen
  von gewissen Objekten wurde korrigiert.

.. disqus::
