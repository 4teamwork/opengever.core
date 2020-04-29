.. _policies-repository:

Ordnungspositionen
==================
Unter `ordnungssystem.xlsx <https://github.com/4teamwork/opengever.core/blob/master/opengever/examplecontent/profiles/repository_minimal/opengever_repositories/ordnungssystem.xlsx>`_
befindet sich ein Beispiel-Ordnungssystem.

Diese Datei wird beim Installieren von GEVER für das Ordnungssystem verwendet. Oft ist die Datei fehlerhaft und der Import schlägt fehl.

Die Richtigkeit der Excel-Datei kann mittels :ref:`bundle-validator` validiert werden.

Häufige Fehler
--------------
Format Aktenzeichen-Spalte
~~~~~~~~~~~~~~~~~~~~~~~~~~
Die Akzenzeichen-Spalte muss für den Import explizit als ``Text`` formatiert sein. Dazu benötigt jede Zelle ein ``'`` vor dem Aktenzeichen. Die Formatierung kann automatisiert wie folgt durchgeführt werden:

Dialog "Daten" -> "Spalten in Text" verwenden:

    |fix_ordnungsposition_1|

    |fix_ordnungsposition_2|

Werden die Ordnungspositionen während der Installation korrekt erstellt, ist die Datei gültig.

 .. |fix_ordnungsposition_1| image:: ../_static/img/fix_ordnungsposition_1.png
 .. |fix_ordnungsposition_2| image:: ../_static/img/fix_ordnungsposition_2.png
