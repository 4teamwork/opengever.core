Übersetzungen
=============

OneGov GEVER steht in den zwei Sprachen Deutsch und Französisch zur Verfügung. Die deutschen Übersetzungen werden jeweils vom Entwickler selbst erstellt bzw. aktualisiert. Die französischen Übersetzungen werden durch eine externen Übersetzerin erstellt und bearbeitet.

Deshalb werden keine französischen Übersetzungen durch einen Entwickler gemacht und stattdessen leer gelassen, damit neue/aktualisierte Übersetzungen leicht ersichtlich sind.


Weblate
-------
Für das Aktualisieren und Bearbeiten der Übersetzungen verwenden wir die Software ``Weblate`` welche via http://translations.onegovgever.ch/ erreichbar ist.

Login: via GitHub

Deployment: /apps/02-django-translations.onegovgever.ch auf seth.4teamwork.ch


Aktualisierung der Übersetzungen:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1.	Aktualisierung des ``opengever.core`` Repository in ``/var/data_dir/vcs/onegov-gever/opengever-activity``.
2.	``loadpo`` und ``rebuild_index`` scripts ausführen

.. code-block:: bash

  . bin/activate
  python src/weblate/manage.py loadpo --all
  python src/weblate/manage.py rebuild_index --all
