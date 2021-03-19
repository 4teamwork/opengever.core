Seriendruckfelder in Sablon-Vorlagen verwenden
----------------------------------------------

Um über eine Liste von Einträge iterieren zu können, muss dies in der
Wordvorlage über die folgenden Felder (in eckigen Klammern) gesteuert werden:

.. code-block:: none

    [<liste>:each(member)]
    ...
    [<liste>:endEach]

wobei ``<liste>`` einem Metadatum vom Typ Liste entspricht, also z.B.
``participants``.
Der Text zwischen den beiden Seriendruckfeldern (angedeutet durch ...) wird
dabei bei jedem Schleifendurchlauf neu im erzeugten Word eingefügt.
Damit der Inhalt eines Metadatums in einer Vorlage eingefügt wird, muss im
Seriendruckfeld dem Namen des gewünschten Metadatums ein Gleichheitszeichen
(``=``) vorangestellt werden, z.B. liefert ``[=meeting.date]`` das
Sitzungsdatum, das an der entsprechenden Stelle in der Wordvorlage eingefügt
wird.

Zusätzlich können Kommentare in der Wordvorlage hinterlegt werden, die in den
generierten Worddokumenten (Protokoll, Protokollauszug) nicht mitgegeben
werden. Kommentare müssen dazu zwischen die Felder ``comment`` und
``endComment`` befinden.

Eine Dokumentation der DSL findet man unter: https://github.com/senny/sablon#conditionals
Beispiele einer Sablon Datei findet man unter: https://github.com/senny/sablon#examples
