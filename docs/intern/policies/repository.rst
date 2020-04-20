.. _policies-repository:

Ordnungspositionen
==================

Die Ordnungspositionen werden im excel File auf default_content/opengever_repositories/ordnungssystem.xlsx definiert.
Diese Datei muss meist überabeitet und kontrolliert werden.
Meist entstehen Probleme beim Einlesen der Aktenzeichen-Spalte.
Deshalb sollte das Format (``Text``) dieser Spalte sichergestellt werden.
Hierfür am Besten den Dialog "Daten" -> "Spalten in Text" verwenden:

    |fix_ordnungsposition_1|

    |fix_ordnungsposition_2|

Die Richtigkeit der Excel-Datei kann mittels https://ogg.4teamwork.ch/validator validiert werden.

Bei der Erstellung einer Policy empfiehlt es sich die Policy lokal zu installieren und zu testen.
Hierfür muss das Policy Package zu den development-packages und eggs hinzugefügt werden.
Nicht zu vergessen ist der entsprechende Eintrag in http://kgs.4teamwork.ch/sources.cfg via https://github.com/4teamwork/kgs .

.. code-block:: ini

    [buildout]

    development-packages += opengever.name_of_your_policy_package

    [instance]
    eggs += opengever.name_of_you_policy_package

Für eine lokale Installation sollte der :ref:`version-control` bereits erstellt sein.

Führe danach ein buildout aus und installiere ein GEVER mit der richtigen policy.

 .. |fix_ordnungsposition_1| image:: ../_static/img/fix_ordnungsposition_1.png
 .. |fix_ordnungsposition_2| image:: ../_static/img/fix_ordnungsposition_2.png

Werden die Ordnungspositionen während der Installation korrekt erstellt, ist die Datei gültig.
Dafür muss die policy im src Ordner des verwendeten opengever.core sein.
Mache dann ein Eintrag in builout.cfg:
