.. _label-standardablauf-admin:

Définir un déroulement standard
===============================

Le déroulement standard
-----------------------
Il est possible de définir des séquences de tâches récurrentes sous modèles, nommées « déroulements standard ». Seul des utilisateurs (administrateurs) disposant des droits de lecture et d’écriture dans la section des modèles sont autorisés à en créer ou à les modifier. Les déroulements standard peuvent être déclenchés par tous les utilisateurs participant à un dossier pour lequel le déroulement est utilisable. Plus de détails à ce sujet voir la documentation utilisateurs, sous le chapitre :ref:`Travailler avec des déroulements standard  <chapitre-deroulement_standard>`.

Créer un nouveau déroulement standard
-------------------------------------
Pour créer un nouveau déroulement standard, naviguez vers la section Modèles, puis cliquez sur *Ajout d’un élément -> Déroulement standard*.

|img-deroulementstandard-20|

Sur le nouvel écran de saisie, donnez un titre au déroulement standard et ajoutez-y, optionnellement, une brève description.

OneGov GEVER propose deux types de déroulements standard : parallèle et séquentiel. Parallèle implique que plusieurs tâches peuvent être déclenchées simultanément. Séquentiel implique qu’une tâche qui précède une autre doit être close avent que la suivante soit déclenchée. Le menu déroulant permet de choisir quel type de déroulement sera appliqué.

|img-deroulementstandard-30|

Dans l’écran suivant, le nombre désiré de tâches peut être ajoutés en cliquant sur *Ajout d’un élément -> Modèle de tâches*.

|img-deroulementstandard-22|

Le masque de saisie est rempli de manière similaire à celui de d’une tâche standard.

|img-deroulementstandard-23|

**Considérations concernant le mandant**

Au moment où le mandataire et le mandant d’une tâche doivent être saisis, il y a la possibilité de choisir soit un des utilisateurs enregistrés, soit juste un rôle. Cette dernière solution a pour avantage que, dans une première étape, il n’est pas encore nécessaire de définir le nom d’une personne spécifique, mais seulement un rôle, tel que *responsable de dossier*, *adjoint administratif*, etc.

Ce sera donc uniquement au moment du déclenchement du déroulement standard dans un dossier que les rôles seront remplacés par des utilisateurs spécifiques. La personne jouant le rôle de responsable de dossier correspond alors avec l’utilisateur qui est déjà connu comme responsable du dossier au niveau du système.

Les mandants définis par le modèle de tâches sont proposés au collaborateur responsable et peuvent être choisis par ce dernier lors du déclenchement d’un déroulement standard. Il est aussi possible de ne définir aucun mandant.


**Séquence**

Une fois le modèle de tâche sauvegardé, celui-ci apparaît automatiquement dans le déroulement standard. Il n’y a pas de limite sur le nombre de modèles de tâches qui peuvent être ajoutées. L’ordre des tâches au sein d’un déroulement standard peut être modifié par un glisser-déposer. Cela a surtout son importance pour les déroulements standard séquentiels.

**Activation**

Pour qu’un déroulement standard soit utilisable dans un dossier (ou sous-dossier), il doit être activé après la saisie. Ceci est effectué via Actions -> Activer.

|img-deroulementstandard-31|

À partir de ce point, un déroulement standard peut être ajouté et déclenché comme décrit le chapitre :ref:`Travailler avec des déroulements standard  <chapitre-deroulement_standard>` de la documentation utilisateurs.

.. |img-deroulementstandard-20| image:: img/media/img-deroulementstandard-20.png
.. |img-deroulementstandard-22| image:: img/media/img-deroulementstandard-22.png
.. |img-deroulementstandard-23| image:: img/media/img-deroulementstandard-23.png
.. |img-deroulementstandard-30| image:: img/media/img-deroulementstandard-30.png
.. |img-deroulementstandard-31| image:: img/media/img-deroulementstandard-31.png

.. disqus::
