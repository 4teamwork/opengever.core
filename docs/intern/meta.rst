Meta
====

Dieser Bereich enthält Informationen *über* das Erstellen von Dokumentation für GEVER.

.. contents::
   :local:
   :backlinks: none

Arbeiten an der Dokumentation
-----------------------------

git-lfs installieren
^^^^^^^^^^^^^^^^^^^^

Für das Arbeiten an der Dokumentation muss einmal systemweit ``git-lfs``
installiert werden, damit die Screenshots via ``git-lfs`` heruntergeladen
werden können. Dies muss pro Gerät nur ein einziges Mal gemacht werden, und
muss nicht für jedes neue Build-Environment wiederholt werden:

.. code-block:: bash

   brew install git-lfs
   git lfs install


Erstellen eines Build-Environments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Für das builden der Dokumentation wird ein lokaler checkout des
``opengever.core`` Repositories benötigt. Eine GEVER-Instanz muss nicht
aufgesetzt werden, aber buildout muss ausgeführt werden um Sphinx zu
installieren und die nötigen build-scripts zu erzeugen.

Das initiale Einrichten eines Build-Environments geschieht wie folgt:

.. code-block:: bash

   cd ~/projects
   git clone git@github.com:4teamwork/opengever.core.git opengever.core-docs
   cd opengever.core-docs
   bin/enable-lfs
   ln -s sphinx-standalone.cfg buildout.cfg
   python bootstrap.py && bin/buildout

Dies muss nur einmal gemacht werden, und dieses Build-Environment kann
wiederverwendet werden für weitere Arbeiten an der Dokumentation.


Eigenen Branch erstellen
^^^^^^^^^^^^^^^^^^^^^^^^

Für das Arbeiten an der Dokumentation sollte ein eigener Branch erstellt
werden:

.. code-block:: bash

   git checkout -b my-doc-improvements

Mit diesem Befehl wird ein neuer Branch ``my-doc-improvements`` erstellt,
ausgehend vom aktuellen branch (üblicherweise ``master``), und ``git``
wechselt unmittelbar auf den neuen branch.

.. hint::

   Wenn der lokale checkout nicht aktuell ist, sollte dieser zuerst
   aktualisiert werden! Siehe :ref:`updating-local-checkout`


Builden der Dokumentation
^^^^^^^^^^^^^^^^^^^^^^^^^

Die vorhandene Dokumentation ist in separate Sphinx-Projekte gegliedert,
welche als Unterverzeichnisse in ``docs/`` existieren (z.B. ``api`` und
``intern``).

.. note::

   Jedes dieser Projekte enthält ein ``conf.py`` welches die
   Sphinx-Konfiguration für dieses Projekt enthält. Der eigentliche Inhalt des
   Projekts beginnt mit dem Dokument ``index.rst``, von welchem aus weitere
   Dokumente eingebunden werden.

Um den aktuell auf dem Filesystem vorhandenen Stand der Dokumentation zu
builden, wird das Build-Script für das entsprechende Projekt aufgerufen.
Dieses ist gemäss dem Namen des Projekts im ``docs/`` Verzeichnis benannt.

Beispiel für die interne Dokumentation:

.. code-block:: bash

   bin/docs-build-intern

Dieses Script wird eine Menge Output produzieren, und ganz am Schluss einen
Hinweis darauf geben, wo das Resultat des Builds zu finden ist:

.. code-block:: none

   Build finished. The HTML pages are in _build/html.

*(Wenn dieses Script Warnungen über ungültige Syntax ausgibt, sollte dies
nach Möglichkeit korrigiert werden.)*

Der dort angegebene Pfad ist relativ zum Verzeichnis des Projekts. Für die
interne Dokumentation kann der HTML-Output also z.B. wie folgt im Browser
geöffnet werden:

.. code-block:: bash

   open docs/intern/_build/html/index.html


Änderungen vornehmen
^^^^^^^^^^^^^^^^^^^^

Nachdem ein erster build der Dokumentation erstellt wurde, um sicherzustellen
dass alles funktioniert, können jetzt Änderungen an der Dokumentation
vorgenommen werden.


Publizieren der Dokumentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Für das Publizieren der Dokumentation gibt es pro Projekt ein
``<proj>-build-and-publish`` Script welches die Dokumentation mit einem
builder baut der für die Publizierung auf einem Webserver geeignet ist, und
mit ``rsync`` auf den entsprechenden Webserver publiziert.


Damit das Publizieren mit ``rsync`` funktioniert, muss der persönliche Benutzer
für den entsprechenden Server in der  ``~/.ssh/config`` hinterlegt werden.

.. code-block:: bash

   Host seth.4teamwork.ch
     User <user>


Um z.B. die interne Doku zu publizieren:

.. code-block:: bash

   bin/docs-build-and-publish-intern

Das Publizieren ist völlig unabhängig von ``git``. Publiziert wird, was im
bei einem frischen ``dirhtml`` build der Dokumentation rauskommt, so wie sie
im Moment auf dem Filesystem vorliegt.


Committen und pushen der Änderungen
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Um die Änderungen an der Dokumentation mittels ``git`` einzuchecken, kann wie
folgt vorgegangen werden:

Übersicht über die lokalen Änderungen erhalten:

.. code-block:: bash

   git status

.. warning::

   Hier lohnt es sich, im Output von ``git status`` nochmals sicherzustellen,
   dass man sich nicht auf dem ``master`` branch befindet!

Gewünschte Änderungen stagen für das committen:

.. code-block:: bash

   git add docs/intern

Committen und im sich öffnenden Editor eine commit message vergeben:

.. code-block:: bash

   git commit

.. hint::
   Um zu verhinden, dass der CI Governor einen branch testet, der nur Updates
   an der Dokumentation enthält, kann in der commit message das Tag
   ``[ci skip]`` verwendet werden. Dieses sollte auf einer eigenen Zeile am
   Ende der commit message eingeführt werden, damit ``git log`` übersichtlich
   bleibt.


Den eigenen branch pushen:

.. code-block:: bash

   git push

Beim ersten mal wo versucht wird, einen neuen branch auf den remote zu pushen,
wird ``git`` dies nicht können, weil noch kein upstream branch definiert ist.
Es wird aber eine hilfreiche Meldung ausgegeben, wie man dies einrichten kann:

.. code-block:: bash

   fatal: The current branch <neuer-branch-name> has no upstream branch.
   To push the current branch and set the remote as upstream, use

      git push --set-upstream origin <neuer-branch-name>

Diese Zeile kann so (wie sie **lokal** von git ausgegeben wird) copy pasted
und ausgeführt werden, damit wird gleichzeitig ein upstream branch definiert
und die Änderungen auf den remote gepusht. Für alle zukünftigen Updates für
diesen Branch reicht danach ein simples ``git push``.


.. _updating-local-checkout:

Aktualisieren des lokalen Checkouts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Ein lokaler Checkout der nicht aktuell gegenüber dem ``master`` auf dem remote
ist, sollte zuerst aktualisiert werden, **bevor** ein neuer Branch für eigene
Arbeiten erstellt wird.

Dazu wird zuerst auf den ``master`` branch gewechselt:

.. code-block:: bash

   git checkout master

Dann kann der ``master`` gepullt werden:

.. code-block:: bash

   git pull

Jetzt kann der neue Branch erstellt und auf diesen gewechselt werden:

.. code-block:: bash

   git checkout -b my-new-branch


Output-Formate
^^^^^^^^^^^^^^

Sphinx unterstützt verschiedenste Output-Formate, welche mittels sogenannter
*builder* produziert werden.

``html``
''''''''

Die build scripts verwenden per default den ``html`` builder. Dieser
produziert HTML-Dateien für das lokale Betrachten im Browser, im Stil von
``kurzreferenzen/administration.html``.

``dirhtml``
'''''''''''

Für die Publikation auf einem Webserver möchte man hingegen schöne URLs ohne
eine Endung ``.html``, und dieser Stil wird vom ``dirhtml`` builder produziert:

Dokumente im Stil ``kurzreferenzen/administration/index.html``, und Links welche
dann nur auf ``/kurzreferenzen/administration/`` zeigen. Diese HTML-Struktur
ist dafür geeignet für die Publikation, aber nicht zum lokal anzeigen. Die
Publikations-Scripts builden und syncen den Output des ``dirhtml`` builders.

``latexpdf``
''''''''''''

Der ``latexpdf`` builder erzeugt LaTeX-Output als Zwischenstufe, und erzeugt
davon ein PDF. Beispiel:

.. code-block:: bash

   bin/docs-build-intern latexpdf
   open docs/intern/_build/latex/OneGovGEVERIntern.pdf
