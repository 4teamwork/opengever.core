.. _chapitre-deroulement_standard:

Travailler avec des déroulements standard
=========================================

Qu’est-ce qu’un déroulement standard?
-------------------------------------

Les séquences de tâches récurrentes (p. ex. Étapes de projet prédéfinies) peuvent être enregistrées dans la section « Modèles ». Ces séquences de tâches prédéfinies sont aussi nommées *déroulements standard*.

La création et modification de déroulements standard est réservée aux utilisateurs ayant un profil qui inclut la gestion de modèles. La plupart du temps, il s’agit des administrateurs. De ce fait, la création de déroulements standard est couverte dans `la documentation admin <https://docs.onegovgever.ch/admin-manual/standardablauferstellen/>`_ (disponible seulement en Allemand).

|img-deroulstandard-1|

Sous *Modèles*, En cliquant sur un déroulement standard, on obtient une liste des tâches et leurs détails respectifs.

a.  Titre de la tâche

b.  Type de tâche

c.  Mandant

d.  Mandataire

e.  Nombre de jours donnés pour compléter de la tâche

f.  Présélectionné : Indication si la tâche doit être automatiquement sélectionnée lorsqu’un déroulement standard est déclenché dans un dossier.

|img-deroulstandard-2|

Déroulements parallèles et séquentiels
--------------------------------------
Les déroulements standard et séquentiels se distinguent de la manière suivante : Parallèle signifie que plusieurs tâches peuvent être complétées en même temps. Séquentiel signifie toutes les tâches sont créés dès le début, mais déclenchées l’une après l’autre. Ainsi la tâche suivante n’est activée que lorsque la tâche précédente a été complétée. L’utilisateur peut définir, à l’aide du menu déroulant, quel type de déroulement doit être utilisé.

Le type de séquence est défini par le créateur du déroulement standard et ne peut pas être modifié lors de l’exécution. Les différences entre les 2 types de déroulements sont couvertes en détails plus loin.


Déclencher un déroulement standard
----------------------------------

Dans un dossier ou sous-dossier, sélectionnez *Ajout d’un élément→ Déclencher un déroulement standard*

|img-deroulstandard-3|

Sélectionnez ensuite le déroulement standard à utiliser, puis cliquez sur *Continuer*.

|img-deroulstandard-4|

Les modèles de tâches marqués comme présélectionnés sont déjà inclus. Les tâches requises peuvent être ajoutées/ôtées par l’intermédiaire d’un clic dans la case à cocher.

|img-deroulstandard-5|

À l’étape suivante, il faut définir le mandataire de chaque tâche. Si le modèle de tâche contient déjà une entrée pour le mandataire, celui-ci sera proposé par défaut. Mais il peut bien sûr aussi être modifié.

|img-deroulstandard-6|

En cliquant sur *Enclencher*, les tâches sélectionnées sont reprises par le dossier. Elles peuvent maintenant être traitées comme convenu (Voir :ref:`chapitre-taches`). C’est ici que les différences entre une séquence parallèle et séquentielle deviennent visibles, en particulier au niveau de l’état.

Lors de l’activation d’un déroulement standard *parallèle*, une tâche principale avec plusieurs sous-tâches est créée. Dans les propriétés de la tâche principale, on peut voir qu’il s’agit d’un déroulement standard parallèle. Si un déroulement standard parallèle est déclenché, toutes les tâches sont automatiquement passées dans l’état « en traitement » et peuvent donc être traitées en même temps.

Lors de l’activation d’un déroulement standard *séquentiel*, une tâche principale avec plusieurs sous-tâches est également créée. Dans les propriétés de la tâche principale, on peut voir qu’il s’agit d’un déroulement standard séquentiel. Lorsqu’un déroulement standard séquentiel est déclenché, la première tâche est automatiquement passée dans l’état « ouvert », les tâches subséquentes sont marquées comme « planifiées ». Ces dernières sont donc déjà visibles mais dépendent de la conclusion de la tâche précédente pour être activées.

|img-deroulstandard-7|


Points à considérer avec les déroulements standard séquentiels
--------------------------------------------------------------

-   Si une tâche est refusée, elle est réassignée au mandant. Ce dernier a la possibilité de réactiver la tâche (et ensuite de la réassigner ou la clôturer lui-même). Pour les tâches séquentielles, il est également possible d’omettre une tâche.

|img-deroulstandard-8|

-   Dans le sommaire des propriétés de la tâche principale d’un déroulement standard, il est possible d’insérer directement une nouvelle tâche dans la liste des tâches existante. Le déroulement standard peut ainsi être complété individuellement. Le formulaire « ajouter une nouvelle tâche » se comporte de la même manière que :ref:`l’ajout d’une tâche standard <label-creer_tache>` et insert automatiquement une nouvelle tâche dans la séquence.

|img-deroulstandard-9|

.. |img-deroulstandard-1| image:: _static/img/img-deroulstandard1.png
.. |img-deroulstandard-2| image:: _static/img/img-deroulstandard2.png
.. |img-deroulstandard-3| image:: _static/img/img-deroulstandard3.png
.. |img-deroulstandard-4| image:: _static/img/img-deroulstandard4.png
.. |img-deroulstandard-5| image:: _static/img/img-deroulstandard5.png
.. |img-deroulstandard-6| image:: _static/img/img-deroulstandard6.png
.. |img-deroulstandard-7| image:: _static/img/img-deroulstandard7.png
.. |img-deroulstandard-8| image:: _static/img/img-deroulstandard8.png
.. |img-deroulstandard-9| image:: _static/img/img-deroulstandard9.png
