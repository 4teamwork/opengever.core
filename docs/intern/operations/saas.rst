SaaS Deployments
================


SaaS Policies für Release vorbereiten
-------------------------------------

Das package . _opengever-deployments: https://github.com/4teamwork/opengever-deployments/
steht dabei zur Verfügung.

- Meta-package auschecken: ``git clone https://github.com/4teamwork/opengever-deployments``
- entweder: mit alle SaaS-policies nach `saas_dev_packages` auschecken: ``dev/checkout.py``
- neue gever version in ``versions.cfg`` aller policies einsetzen, commit message: ``Bump policy to 20xx.y.z release.``
- mit ``dev/for_all_saas_policies`` können commands für alle ausgecheckten policies ausgeführt werden


Release einspielen
------------------

Im Moment sind alle SaaS Deployments auf ``theta.4teamwork.ch`` installiert.
Skripte und Metadaten für die SaaS-Deployments/Policies werden im Moment im
`opengever-deployments <https://github.com/4teamwork/opengever-deployments>`_
Repository auf github gepflegt. Dieses ist auf dem Server
``theta.4teamwork.ch`` nach ``/home/zope/opengever-saas`` ausgecheckt und
muss manuell mittels ``git pull`` aktualisiert werden.


Einzelnes Deployment aktualisieren
----------------------------------

Zur Aktualisierung eines Deployments steht das Skript

.. code-block:: bash

    update_deployment

zur Verfügung. Es muss im buildout-directory des Deployments ausgeführt
werden. Das Skript reported auch in den Slack Channel `gever-notifications
<https://4teamwork.slack.com/archives/gever-notifications>`_.

Nachfolgend ein Beispiel wie ein Dev-Deployment aktualisiert werden kann:

.. code-block:: bash

    cd ~/theta.4teamwork.ch/01-dev.onegovgever.ch-fd/
    update_deployment


Operationen über alle SaaS Deployments
--------------------------------------

Im `opengever-deployments <https://github.com/4teamwork/opengever-deployments>`_
Repository wird ein JSON-File aller SaaS-Policies/Deployments gepflegt. Die
Liste der Deployments muss dort aktuell gehalten werden. Die Skripte

.. code-block:: bash

    for_all_saas_deployments
    for_all_saas_deployments_parallel

lesen diese Liste aus und wenden einen Bash-Command auf alle darin
aufgeführten Deployments auf dem Server ``theta.4teamwork.ch`` im Ordner
``/home/zope/theta.4teamwork.ch`` an.

Nachfolgend ein Beispiel wie man einen Command für alle SaaS-Deployments
ausführen kann:

.. code-block:: bash

    for_all_saas_deployments "git status"


Alle SaaS Deployments aktualisieren
-----------------------------------

.. code-block:: bash

    for_all_saas_deployments[_parallel] "update_deployment"
