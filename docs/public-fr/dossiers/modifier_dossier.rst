.. _label-modifier-dossier:

Modifier un dossier
-------------------

Modifier les métadonnées d’un dossier
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pour modifier les propriétés et métadonnées d’un dossier, cliquez sur "Modifier".

Imprimer une page de couverture ou les détails de l’affaire
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

|img-modifierdossier01|

Par le menu *Actions*, il est possible d’imprimer la page de couverture ou les détails de l’affaire.

Afficher les métadonnées d’un dossier
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

En cliquant sur l’action Afficher les métadonnées, il est possible d’avoir un aperçu de l’ensemble des métadonnées du dossier en question. Il est également possible d’accéder aux dossiers liés via cette page.

|img-modifierdossier02|

.. _label-beteiligungen:

Ajouter des participants à un dossier
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dans OneGov GEVER, il existe 4 rôles par défaut. Seul le rôle Responsable est obligatoire. Des rôles additionnels peuvent être attribués à des fins de documentation.

+-------------------------+-----------------------------------------------------------------------------------------------------------------------+
| **Rôle**                | **Clarification**                                                                                                     |
+=========================+=======================================================================================================================+
| *Responsable*           | Collaborateur administratif responsable. Gère le dossier et est responsable d’assurer l’intégrité de son contenu.     |
+-------------------------+-----------------------------------------------------------------------------------------------------------------------+
| *Participation*         | Intervenants internes ou externes, participant activement au déroulement de l’affaire.                                |
+-------------------------+-----------------------------------------------------------------------------------------------------------------------+
| *Signature finale*      | Cas particulier de participation.                                                                                     |
+-------------------------+-----------------------------------------------------------------------------------------------------------------------+
| *Prise de connaissance* | Pas de participation active au déroulement de l’affaire. Les documents reçus uniquement pour information.             |
+-------------------------+-----------------------------------------------------------------------------------------------------------------------+

.. note::
   - La personne responsable doit toujours être un membre du mandant courant
   - Les participants additionnels peuvent être membres du même mandant un d’un autre. Les participants externes peuvent également être sélectionnés, pourvu qu’ils aient été saisis sous *Contacts*.
   - Une participation ne donne pas de droits d’accès additionnels au dossier.

Alors que le responsable est directement saisi dans les propriétés du dossier, les autres participations sont ajoutées par l’intermédiaire de *Ajout d'un élément → Participation* ou saisis dans l’onglet *Participations*.

|img-modifierdossier03|

En premier, la personne désirée est sélectionnée puis le rôle pertinent lui est assigné. L’ajout du participant est finalisé par un clic sur « Etablir ».

|img-modifierdossier04|

Fermer un dossier
~~~~~~~~~~~~~~~~~

La fermeture d’un dossier est, selon la configuration, disponible à tous les utilisateurs ou uniquement au responsable et les utilisateurs bénéficiant de droits spéciaux.

Avant la fermeture, les règles suivantes doivent être observées :

- Toutes les tâches doivent être fermées.
- Toutes les requêtes mises à l’ordre du jour doivent être fermées.
- Si le dossier contient des sous-dossiers, tous les contenus doivent être enregistrés dans des sous-dossiers. Selon besoin, cette règle peut être désactivée dans les options de configuration.

De plus, la date de clôture doit être prise en considération. Celle-ci doit porter au moins la date à laquelle un document du dossier a été modifié. Lors de la clôture du dossier, le système vérifie ce point. Si, par exemple, lors de la création du dossier, une date de fin se situant avant celle de la dernière modification d’un document a été saisie, OneGov GEVER affichera une erreur et le dossier ne pourra pas être fermé tant que cette date n’aura pas été corrigée.

Une fois toutes les conditions ci-dessus remplies, le dossier peut être fermé via l’action *Fermer*.

|img-modifierdossier05|

Après la fermeture du dossier, et si cette option est activée, le système génère automatiquement un PDF contenant l’historique, qui liste toutes les activités du dossier ainsi que les requêtes et tâches qui y ont été créées

|img-modifierdossier06|

|img-modifierdossier07|

Si l’option est active, il est également possible de générer un PDF listant les tâches.

|img-modifierdossier08|

|img-modifierdossier09|

Réactiver et modifier un dossier
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Les dossiers peuvent être ré-ouverts (selon la configuration) uniquement par les utilisateurs disposant des droit adéquats, tels que les personnes ayant les droits de type *secrétariat*. Pour réactiver un dossier, sélectionnez *Actions → Rouvrir*. L’état du dossier passe à nouveau à *En cours* et le contenu peut être modifié.

Effectuez les changements nécessaires dans le dossier puis sélectionnez *Actions → Fermer*.

Si l’année d’enregistrement n’a pas changé, sélectionnez *Fermer et utiliser le numéro de système existant*. Autrement, sélectionnez *Fermer et  libérer le numéro de système*. Une fois effacés, les numéros de système ne sont plus à disposition.

Annuler un dossier
~~~~~~~~~~~~~~~~~~

Si un dossier a été ouvert par erreur, il peut être annulé via le menu Actions → Annuler. Les dossiers annulés ne peuvent plus être modifiés. Le personnes disposant de droits de secrétariat voire les collaborateurs administratifs disposant de droits spéciaux peuvent, selon la configuration, réactiver des dossiers annulés. (*Actions → Rouvrir*)

L’onglet Info – Qui a accès au dossier ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sous l’onglet *Info*, il est possible de voir quels groupes et utilisateurs ont accès au dossier.

Pour voir le membres d’un groupe, cliquez sur son nom.

Les droits sont établis au niveau du numéro de classement de la structure d’organisation et sont repris par les dossiers qui s’y trouvent.

|img-modifierdossier10|

L’onglet Historique – Qui a fait quoi et quand ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sous l’onglet *Historique* se trouve un listing complet de qui a effectué quelles modifications dans le dossier. L’historique assure la traçabilité et ne peut être édité.

|img-modifierdossier11|

Export ZIP
~~~~~~~~~~

Un dossier entier peut être combiné en un seul fichier ZIP et téléchargé depuis le serveur. Pour ce faire :

1.	Naviguez vers le dossier que vous désirez exporter.

2.	Ouvrez le menu déroulant «Actions» et cliquez sur «Exporter au format ZIP»

3.	Choisissez un endroit où sauvegarder le fichier ZIP.


.. note::

   Il est également possible d’exporter une sélection restreinte de documents sous forme de fichier zip. Vous trouverez les instructions à ce sujet dans le chapitre couvrant l’:ref:`label-export-zip-documents`.

.. |img-modifierdossier01| image:: ../_static/img/img-modifierdossier01.png
.. |img-modifierdossier02| image:: ../_static/img/img-modifierdossier02.png
.. |img-modifierdossier03| image:: ../_static/img/img-modifierdossier03.png
.. |img-modifierdossier04| image:: ../_static/img/img-modifierdossier04.png
.. |img-modifierdossier05| image:: ../_static/img/img-modifierdossier05.png
.. |img-modifierdossier06| image:: ../_static/img/img-modifierdossier06.png
.. |img-modifierdossier07| image:: ../_static/img/img-modifierdossier07.png
.. |img-modifierdossier08| image:: ../_static/img/img-modifierdossier08.png
.. |img-modifierdossier09| image:: ../_static/img/img-modifierdossier09.png
.. |img-modifierdossier10| image:: ../_static/img/img-modifierdossier10.png
.. |img-modifierdossier11| image:: ../_static/img/img-modifierdossier11.png
