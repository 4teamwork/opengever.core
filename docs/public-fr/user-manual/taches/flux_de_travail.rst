.. _label-taches-flux-travail:

Aperçu d’un flux de travail typique
-----------------------------------

Après avoir sauvegardé, la tâche se retrouve dans l’état *ouvert*.

**Séquence typique de complétion d’une tâche**

-   Mandant créé la tâche – État : *Ouvert*

-   Mandataire accepte la tâche – État : *En traitement*

-   Mandataire complète la tâche – État : *Accompli*

-   Mandant conclut la tâche – État : *Clôturé*


.. note::
   Pour les types de tâche « pour prise de connaissance » et « Pour réalisation immédiate » : Comme le mandant n’attend pas de réponse pour vérification, le flux de travail est raccourci.

   - « Pour prendre connaissance » : Cette tâche peut être fermée sans être acceptée au préalable.

   - « Pour réalisation immédiate » : Cette tâche peut être fermée directement après avoir été acceptée.

   Les utilisateurs ayant accès à la boîte de réception peuvent également déclencher des actions concernant les tâches additionnelles lorsqu’ils ne sont pas les mandataires.

**Exceptions**

-   Si le mandataire décline une tâche, celle-ci est retournée au mandant – État : *Refusé*

-   Si le mandant annule une tâche, sont état passe à *Annulé*

-   Si le mandant rouvre une tâche après que celle-ci ait déjà été accomplie ou refusée, l’état de la tâche passe à *Ouvert*

-   Si le mandant assigne une tâche à une autre personne, l’état de celle-ci reste *Ouvert*.

**Déroulement séquentiel**

Avec ce type de déroulement, *Planifié* et *Omis* viennent s’ajouter à la liste des états de tâche possibles. Avec ce genre de déroulement, les tâches sont traitées l’une après l’autre, c’est-à-dire que la tâche subséquente n’est déclenchée que lorsque la précédente a été fermée. Lorsqu’un déroulement standard séquentiel est déclenché la première tâche passe donc en statut *Ouvert* tandis que toutes les autres restent en *Planifié* jusqu’à ce que ce soit leur tour. Les tâches d’un déroulement séquentiel peuvent également être *Omises*, une action qui se reflète bien sûr dans son état.

**Autorisations avec les différentes tâches**

Les droits sur les documents suivants viennent compléter les droits existants au niveau numéro de classement et dossier pour la durée de la tâche. Aussitôt que la tâche est accomplie, ces droits sont à nouveau retirés au mandataire.

============================ =========================
Type de tâche                Droits du mandataire
============================ =========================
Pour prendre connaissance    Lecture uniquement

Pour réalisation immédiate   Lecture et modification

Pour Accord	                 Lecture et modification

Pour contrôle/correction     Lecture et modification

Pour prise de position       Lecture et modification

Pour rapport/demande         Lecture et modification

============================ =========================

En plus du mandataire, les membres du groupes « Boîte de réception » obtiennent également les droits nécessaires, dans l’idée de la règle de suppléance.

**Déroulement d’une tâche**

Le schéma suivant illustre la façon dont interagissent les actions et états des tâches.

|img-flux_de_travail-01|

.. |img-flux_de_travail-01| image:: ../../_static/img/img-flux_de_travail-01.png
