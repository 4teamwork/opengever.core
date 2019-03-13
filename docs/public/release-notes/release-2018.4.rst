OneGov GEVER Release 2018.4
===========================

Mit dem Release 2018.4 konnten die OGIPs 26 (sequenzielle Aufgaben), 36
(Benachrichtigung bei Anträgen) sowie 45 (Verbesserung von Berechtigungen von Aufgaben)
umgesetzt werden. Zudem sind neu die zuletzt verwendeten Dokumente besser ersichtlich.
Auch können Administratoren jetzt einen Export des aktuellen Ordnungssystems selbstständig
anstossen. Und: Aufgaben können neu mit Emojis kommentiert werden.

OGIP 36 - Benachrichtigungen bei Anträgen (SPV)
-----------------------------------------------

Durch den `OGIP 36  <https://my.teamraum.com/workspaces/onegov-gever-innovation-session/ogip?overlay=24f872fc7f2c476387d082a79d9a756f#documents>`_ werden gevergestützte Benachrichtigungen für die Sitzungs- und Protokollverwaltung
zur Verfügung gestellt. Dadurch soll erreicht werden, dass die Kommunikation - konkret
die Benachrichtigungen - zwischen Antragsstellenden und Sitzungsplanenden
innerhalb von OneGov GEVER stattfinden kann.

Dazu wurde beim Antrag neu das Feld „Antragssteller“ hinzugefügt. Dadurch wird die
in diesem Feld hinterlegte Person bei diversen Aktionen (z.B. Antrag
zurückweisen, traktandieren etc.) des Antrags benachrichtigt.

|img-release-notes-2018.4-1|

OGIP 26 - sequenzielle Abläufe
------------------------------

Durch den `OGIP 26 <https://my.teamraum.com/workspaces/onegov-gever-innovation-session/ogip?overlay=031a6405b15e40799a1b2232c68e6c9e#documents>`_ werden
sequenzielle Aufgabenabläufe ermöglicht. Dadurch können voneinander abhängige
Aufgabenketten nun auch in OneGov GEVER abgebildet werden.

Bis jetzt war es mit Standardabläufen nur möglich, parallele Aufgabenabläufe auszulösen.
Parallel bedeutet in diesem Fall, dass alle Aufgaben der Aufgabenkette gleichzeitig ausgelöst
werden und den Status „Offen“ erhalten. Beim sequenziellen Ablauftyp werden zwar alle Aufgaben
beim Auslösen des Standardablaufs aktiviert, jedoch erhält nur die erste Aufgabe in
den Status „Offen“. Die weiteren Aufgaben befinden sich im Status „Geplant“.
Wird eine Aufgabe abgeschlossen, löst dies die nächste Aufgabe aus, welche vom
Status „Geplant“ in „Offen“ wechselt. Der gesamte Funktionsumfang kann in
der `Dokumentation <https://docs.onegovgever.ch/user-manual/standardablaeufe/>`_ nachgelesen werden.

Zuletzt verwendete Dokumente
----------------------------

Neu steht in der Service-Navigation eine Übersicht zum Status von Dokumenten zur Verfügung.
Beim Klick auf das Icon erscheint eine Übersicht, welche alle ausgecheckten sowie
kürzlich bearbeiteten Dokumente enthält (eingeloggter Benutzer).

|img-release-notes-2018.4-2|

OGIP 45 -  Verbesserung von Berechtigungen von Aufgaben
-------------------------------------------------------

Der `OGIP 45 <https://my.teamraum.com/workspaces/onegov-gever-innovation-session/ogip?overlay=13da59c6c70547fc83989a7c861dbd1b#documents>`_ hat einerseits ermöglicht, dass die Aufschlüsselung, wie ein Benutzender
eine Berechtigung erhalten hat, ersichtlich wird. Dafür ist neu im Info-Tab sowie
unter Aktionen à Freigabe ein Tool-Tipp mit einem blauen „?“ verfügbar, bei welchem
sich Sachbearbeitende informieren können, warum ein Benutzender eine Berechtigung hat.

|img-release-notes-2018.4-3|

Weiter wurde mit diesem OGIP 45 ermöglicht, dass Berechtigungen, welche mittels Aufgabe
auf OneGov GEVER Inhalte erteilt wurden, beim Abschluss der Aufgabe wieder entzogen werden.

Diverse Verbesserungen
----------------------

- Microsoft Publisher Dateien werden neu vom Office Connector unterstützt.

- Eincheck-Kommentare von Dokumenten können neu als Tool Tipp oder direkt in der
  Dokument-Vorschau gelesen werden. Mehr zu diesem Thema lässt sich im `Feedbackforum <https://feedback.onegovgever.ch/t/einchecken-kommentar-nicht-vollstaendig-sichtbar/1014/6>`_ nachlesen.

- Fehler, welche durch den eCH-0147 Import generiert werden, können gezielter behandelt werden.

- Neu können beim Kommentieren von Aufgaben Emojis verwendet werden.

- Administratoren können neu das aktuelle Ordnungssystem exportieren.

- Schlagworte werden neu in der Dokumenten-Detailansicht dargestellt.

- PDFs werden nach der Dokumenterstellung neu automatisch erstellt, wodurch sofort
  die PDF-Vorschau ersichtlich wird.

- Das Metadatumfeld „externe Referenz“ ist neu klickbar.

- Anpassungen Aufgabenworkflow: Abgelehnte Aufgaben werden neu direkt dem Auftragnehmer
  zurückzugewiesen. Weiter wurde der Status „Storniert“ vom Status „Abgebrochen“ abgelöst.

- An der RESTful API wurden diverse Verbesserungen vorgenommen. Die Schnittstelle
  wird auch bereits von diversen Drittpartnern eingesetzt.

Sitzungs- und Protokollverwaltung
---------------------------------

- In den Sitzungsvorlagen können neu wiederverwendete Zwischentitel vordefiniert werden.

- Statusänderungen der Anträge können neu alle kommentiert werden.

- Beim Erstellen eines Antrags kann neu ein bestehendes Dokument im Dossier als Antrag ausgewählt werden.

- Anträge und Traktanden haben neu das Feld „Beschreibung“.

- Neu befindet sich ein Button „Antrag erstellen“ beim Dokumenten-Tab eines
  Dossiers. Damit können Anträge direkt mit mehreren Dokumenten als Beilage erstellt werden.

- Es können neu mehrere unterschiedliche Antragsvorlagen für Ad-Hoc Anträge konfiguriert werden.

- Neu stehen Doc-Properties auch für Dokumente, die sich in Anträgen und
  in Aufgaben befinden, zur Verfügung.

- Das Datumsformat der generierten Protokolle/Protokollauszüge
  (aus Sablon-Vorlagen) kann neu verwendet werden.

- Das Generierungsdatum steht neu auch als Variable für die Sablon-Vorlagen zur Verfügung.

- Das Gesamt-Protokoll einer Sitzung ist neu auch bearbeitbar bevor die Sitzung als abgeschlossen gilt.

- Komiteeauflistungen werden neu alphabetisch nach Titel der Kommittees sortiert.

.. |img-release-notes-2018.4-1| image:: ../_static/img/img-release-notes-2018.4-1.png
.. |img-release-notes-2018.4-2| image:: ../_static/img/img-release-notes-2018.4-2.png
.. |img-release-notes-2018.4-3| image:: ../_static/img/img-release-notes-2018.4-3.png

.. disqus::
