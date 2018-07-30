Generierte Dokumente
====================

Die erzeugten Dokumente werden aus vielen Vorlagen erstellt.
Dieses Dokument setzt sich zum Ziel, Einsicht in diese Dokumenterstellung zu geben.

Vorprotokoll / Protokoll
------------------------

Vorprotokolle / Protokolle werden aus einem Protokoll-Kopf, einer Reihe von Traktanden und einem Protokoll-Schlussteil zusammengestellt.
Im Protokoll-Kopf werden die Metadaten des Gremiums und der Sitzung dargestellt, so wie eine Traktandenliste.
Im Protokoll-Schlussteil sind meist die Unterschriften der Zuständigen zu finden.

Bei den Traktanden wird unter Zwischentitel und echten Traktanden unterschieden:
Zwischentitel werden verwendet, um die Traktanden zu gruppieren und beinhalten nur text.
Diese werden mit der Zwischentitel-Vorlage erstellt.
Die echten Traktanden werden aus der Traktandum-Kopf-Vorlage, dem Antrags- / Beschlussdokument selbst und der Traktandum-Schlussteil-Vorlage zusammengestellt.

Grafisch dargestellt sieht dies so aus::

    +--------------------------------------------+
    | +----------------------------------------+ |
    | |                                        | |
    | | Vorlage Protokoll-Kopf                 | |
    | |                                        | |
    | +----------------------------------------+ |
    |                                            |
    | Für jedes Traktandum / jeden Zwischentitel |
    |                                            |
    |   Falls Zwischentitel                      |
    |                                            |
    |     +------------------------------------+ |
    |     |                                    | |
    |     | Vorlage Zwischentitel (*)          | |
    |     |                                    | |
    |     +------------------------------------+ |
    |                                            |
    |   Falls Traktandum                         |
    |                                            |
    |     +------------------------------------+ |
    |     |                                    | |
    |     | Vorlage Traktandum Kopf (*)        | |
    |     |                                    | |
    |     +------------------------------------+ |
    |                                            |
    |     +------------------------------------+ |
    |     |                                    | |
    |     | Antrags- / Beschlussdokument       | |
    |     |                                    | |
    |     +------------------------------------+ |
    |                                            |
    |     +------------------------------------+ |
    |     |                                    | |
    |     | Vorlage Traktandum Schlussteil (*) | |
    |     |                                    | |
    |     +------------------------------------+ |
    |                                            |
    | +----------------------------------------+ |
    | |                                        | |
    | | Vorlage Protokoll-Schlussteil (*)      | |
    | |                                        | |
    | +----------------------------------------+ |
    +--------------------------------------------+

Die mit (*) markierten Vorlagen sind optional.

Protokollauszug
---------------

Protokoll-Auszüge werden aus einem Protokollauszug-Kopf, dem Beschlussdokument und einem Protokollauszug-Schlussteil.
Im Protokoll-Kopf werden die Metadaten des Gremiums, der Sitzung und des Traktandums dargestellt.
Im Protokoll-Schlussteil sind meist die Unterschriften der Zuständigen zu finden.

Grafisch dargestellt sieht dies so aus::

    +---------------------------------------------+
    | +-----------------------------------------+ |
    | |                                         | |
    | | Vorlage Protokollauszug-Kopf            | |
    | |                                         | |
    | +-----------------------------------------+ |
    | +-----------------------------------------+ |
    | |                                         | |
    | | Beschlussdokument                       | |
    | |                                         | |
    | +-----------------------------------------+ |
    | +-----------------------------------------+ |
    | |                                         | |
    | | Vorlage Protokollauszug-Schlussteil (*) | |
    | |                                         | |
    | +-----------------------------------------+ |
    +---------------------------------------------+

Die mit (*) markierten Vorlagen sind optional.
