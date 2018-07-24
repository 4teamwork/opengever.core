OneGov GEVER Release 2.9
========================

Am Beispiel des Kantons Zug wurde dessen Öffentlichkeitsgesetz (ÖffG) umgesetzt.
Das **Öffentlichkeitsgesetz** [Gesetz über das Öffentlichkeitsprinzip der Verwaltung
vom 20. Februar 2014; `BGS 158.1 <http://bgs.zg.ch/data/158.1>`_ ] ist am 10. Mai 2014 im Kanton Zug in Kraft getreten.
Es ist die gesetzliche Implementierung eines Paradigma-Wechsels im Umgang mit
amtlichen Dokumenten. Während früher der Grundsatz der Nicht-Öffentlichkeit der
Verwaltung galt, soll nun dieser Grundsatz durch das Prinzip der Öffentlichkeit der Verwaltung abgelöst werden.

|img-release-notes-2.9-1|

Das Gesetz bedingt im Kern die folgenden wesentlichen Anpassungen in OneGov GEVER:

- E-Mails müssen als vollwertige Dokumente behandelt werden, insbesondere müssen
  sie ebenfalls mit den notwendigen Metadaten zum Öffentlichkeitsstatus versehen werden können.

- Neu erstellte Objekte sollen für das Feld "Öffentlichkeitsstatus" den
  mandantenweit konfigurierten Default-Wert vorgeschlagen bekommen
  („Nicht geprüft“ in der Standard-Konfiguration).

- Die Metadaten zum Öffentlichkeitsstatus sollen nur noch auf Ebene Dokument geändert werden können.

- Die Metadaten zum Öffentlichkeitsstatus sollen neu auch auf Dokumenten in
  abgeschlossenen Dossiers angepasst werden können (durch Benutzer, welche Schreib-Berechtigung auf dem Dossier haben).

- Das Prinzip der Verschärfung des Öffentlichkeitsstatus soll deaktiviert werden.

- Der Wertebereich für das Feld "Öffentlichkeitsstatus" wird neu erweitert
  um den Wert "Eingeschränkt öffentlich".

Das neue Verhalten ist konfigurierbar und kann entsprechend pro Mandant
von OneGov GEVER parametrisiert werden.

Anpassungen bei E-Mails
-----------------------

|img-release-notes-2.9-2|

Neu soll ein E-Mail in OneGov GEVER wie ein **vollwertiges Dokument** behandelt werden.

Dies bedeutet, dass ein E-Mail mit denselben Metadaten wie klassische Dokumente
versehen wird. Insbesondere wird das E-Mail auch um die Metadaten aus dem Tab „Sichtbarkeit“ ergänzt.

Da die Header eines E-Mails andere sind als die Metadaten eines GEVER-Dokuments, wird
ein Mapping definiert, das beschreibt, welche E-Mail Header welchen Metadaten
eines GEVER-Dokuments entsprechen. Diese Metadaten werden zusätzlich zum eigentlichen
E-Mail redundant gespeichert. Das Original-Mail wird also nicht verändert, sondern
die neuen Metadaten werden zusätzlich geführt.

Beim Erstellen eines E-Mails (also beim Mail-In) werden diese Metadaten vom System
initialisiert, indem basierend auf dem Mapping die Werte aus den E-Mail Headern
in die Dokument-Metadaten kopiert werden. Die Metadaten können danach wie bei
anderen Dokumenten auch bearbeitet werden - das "Abfüllen" aus den E-Mail Headern
geschieht einmalig und es wird keinerlei Beziehung zwischen einem bestimmten
Metadatum und einem E-Mail Header gespeichert.

Folgende wesentlichen Anpassungen ergeben sich dadurch:

- Vereinheitlichung der E-Mail-Metadaten mit einem den Standard Dokument Metadaten

- Neues Tab Ansicht von E-Mails:

  - Übersichtstab

  - Vorschautab

- Einfacher Download der Originalnachricht im standardisierten EML-Format

- Verbesserte Metadaten-Zeile für E-Mails

- Verbesserte Darstellung des Formulars "Anhänge extrahieren"

- Zusammenführung der Laufnummern für Dokumente und E-Mails

- Vereinheitlichung der ID Generierung

- Erweiterungen beim Versand von Dokumenten:

  - Zusätzliche Option Kopie des versandten Mails in Dossier ablegen

  - Korrektur beim Versand von E-Mails als Anhang

Journalisierung / Nachvollziehbarkeit
-------------------------------------

- Separater Journaleintrag bei Änderungen am Öffentlichkeitsstatus sowie beim Entfernen von E-Mail-Anhängen

- Vereinheitlichung der Journalisierung von E-Mails

- Korrektur von doppelten Einträgen beim D'n'D Upload

Weitere Anpassungen
-------------------

- Das Tab "Übersicht" bei Dokumenten wurde überarbeitet

- Weitere Dokumenttypen stehen zur Auswahl

- Zusätzliche Spalte Öffentlichkeitsstatus bei Dokumentauflistungen

- Eigenständiges Formular für die Bearbeitung des Öffentlichkeitsstatus (ermöglicht auch eine Bearbeitung in abgeschlossenen Dossiers)

- Entfernung des Öffentlichkeitsstatus auf Dossiers und Ordnungspositionen

- Aktualisierung diverser Übersetzungen

- Vereinheitlichte Darstellung der Eigenschaften-Ansicht

- Diverses Bugfixing

.. |img-release-notes-2.9-1| image:: ../../_static/img/img-release-notes-2.9-1.png
.. |img-release-notes-2.9-2| image:: ../../_static/img/img-release-notes-2.9-2.png

.. disqus::
