Le triage
=========

Dossiers expirés
----------------

En OneGov GEVER, le triage de contenus n’est possible qu’au niveau du dossier.
Seuls les dossiers annulés ou clos dont le délai de conservation est échu peuvent être triés.

La durée de conservation est calculée d’après l’exercice. Voici un exemple:

   - Clôture du dossier : 03.01.2013

   - Durée de conservation : 10 ans

   - Triage possible : 01.01.2024

Un aperçu des « dossiers expirés », c’est-à-dire des dossiers entrant en ligne de
compte pour le triage, est fourni par le filtre statut `offert`. Celui-ci
est disponible sur toutes les listes de dossier.

Création et archivage d’offre
-----------------------------

En ce qui concerne l’offre, il s’agit d’un type de contenu séparé comportant, en
plus des métadonnées supplémentaires, avant tout des références aux différents
dossiers. En outre, l’objet « offre » met à disposition le flux de travail complet
pour le triage. Ce flux se compose des étapes suivantes:

1. Création d’offre
2. Finalisation de l’évaluation
3. Remise de l’offre
4. Confirmation d’archivage
5. Destruction des dossiers

|img-triage-6|

Création et évaluation d’offre
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Les offres de triage peuvent être créées au niveau du plan ou du numéro de classement.
Pour créer une offre à partir de la liste des dossiers directement, avec la possibilité
de choisir les dossiers, il existe l’action affichage à onglet `offre de triage`.

|img-triage-1|

Après sa création, l’offre se trouve au statut ``en cours de traitement``
(``disposition-state-in-progress``). Ce statut permet encore de traiter les
métadonnées de l’offre ainsi que les dossiers qu'elle contient.

En plus, il est possible d’évaluer l’offre, c’est-à-dire de décider si un dossier
doit être archivé ou pas. A cet égard GEVER effectue automatiquement une évaluation
préliminaire sur la base de la métadonnée ``valeur archivistique``.

A la suite, cette évaluation peut être adaptée et préparée par les gestionnaires
des dossiers à travers l’affichage d’offre. L’évaluation peut être adaptée ou bien
au niveau du numéro de classement pour tous les dossiers y contenus ou bien séparément pour chaque dossier.

|img-triage-2|

Les dossiers annulés figurent sur une liste séparée. L’évaluation préliminaire
automatique selon la métadonnée ``valeur archivistique`` n’est pas effectuée.
Les dossiers annulés sont, par défaut, évalués comme étant ``sans valeur archivistique``.

|img-triage-3|

Selon la façon de travailler une autorisation peut être attribuée au mandant GEVER
pour que celui-ci puisse effectuer l’évaluation directement dans le système GEVER,
ou bien une liste d’évaluation (Excel) peut être générée et transmise à l’archive.
Pour le moment, l’importation automatique de la liste d’évaluation n’est pas possible.

Finaliser l’évaluation
~~~~~~~~~~~~~~~~~~~~~~

Si l’évaluation a été faite par l’archive, elle peut être finalisée. Ainsi, l’offre
est mise en état ``évaluée`` (``disposition-state-appraised``) et ne peut plus être éditée ou modifiée.

Soumission de l’offre
~~~~~~~~~~~~~~~~~~~~~

Ensuite, l’offre peut être soumise. Par la suite, l’action ``télécharger le paquet
de versement`` est disponible en téléchargement offrant, pour les dossiers contenus,
l’export eCH-0160 avec une évaluation positive.

Pour le cas, où l’offre ne contient que des dossiers qui ne sont pas à livrer aux
archives, les étapes 3 et 4 peuvent être sautées, les dossiers peuvent être triés
directement et l’offre peut être clôturée.

Confirmer l’archivage
~~~~~~~~~~~~~~~~~~~~~

Si le processus Ingest à partir du paquet SIP avec transfert aux archives de longue
durée a réussi, l’archivage peut être confirmé, de préférence directement par
la personne responsable dans l’archive.

Détruire les dossiers
~~~~~~~~~~~~~~~~~~~~~

Le processus de triage est achevé par la destruction des dossiers. Ainsi, tous
les dossiers contenus dans l’offre (y inclus les dossiers sans valeur archivistique)
sont détruits, c’est-à-dire effectivement supprimés du système GEVER.

Après la clôture de l’offre, donc après que les dossiers ont été détruits, il est
en plus possible de télécharger un protocole de suppression généré de façon automatique.

D’autres manières de destruction (comme effacer uniquement les données primaires,
retirer l’autorisation de lecture, etc.) ne sont actuellement pas possibles, ni ne sont prévues.

Refuser l’offre
~~~~~~~~~~~~~~~

Une offre sous le statut `en cours de traitement` ou `livré` peut, en plus,
être refusée par l’archiviste ; ainsi l’offre sera remise au statut `en cours de traitement`.

Historique
----------

Pour chaque offre, un historique est généré et affiché de façon similaire comme
pour les tâches ou les requêtes.

|img-triage-4|

Liste
-----

Au niveau du système de classification, l’onglet supplémentaire `offres` est à
disposition des utilisateurs ayant le rôle de `gestionnaire des dossiers` ou `d’archiviste`.
Cet onglet propose une liste avec toutes les offres du système de classification en question.
Par défaut, seules les offres actives figurent sur la liste, mais les offres
clôturées peuvent également être affichées au moyen du filtre de statut `tous`.

|img-triage-5|

Autorisation
------------

La création ainsi que la vision d’une offre sont protégées. Elles demandent une
autorisation dont ne disposent que les rôles de `gestionnaire`, de `gestionnaire des dossiers`
et d’`archiviste`.

Le nouveau rôle de `gestionnaire des dossiers` est attribué globalement. Il est
attribué à un cercle d’utilisateurs relativement petit, notamment aux personnes
responsables du triage pour le mandant concerné.

Le nouveau rôle `d’archiviste` est attribué globalement aux collaboratrices et
collaborateurs des archives qui sont autorisés à évaluer des offres et de les
verser aux archives de longue durée. Les utilisateurs occupant le rôle d’archiviste
peuvent accéder à tous les dossiers offerts ou archivés, même s’ils ne sont pas attribués
au mandant concerné. Ceci permet aux collaborateurs des archives d’examiner les dossiers
pendant la phase d’évaluation.

Les possibilités de configuration
---------------------------------

Clôture d’un dossier
~~~~~~~~~~~~~~~~~~~~

Les options suivantes sont disponibles pour la clôture d’un dossier et peuvent être
activées ou désactivées par mandant:

- ``Création automatique d’un PDF``: lors de la clôture d’un dossier chaque document
  de celui-ci est converti en format d’archivage et classé en tant que fichier
  séparé dans le champ « fichier d’archivage ». La conversion se fait de façon asynchrone.

- ``Le journal PDF``: lors de la clôture d’un dossier, un PDF est créé contenant
  le journal complet du dossier. Ce PDF est classé dans le dossier en tant que fichier séparé.

- ``Vider la Corbeille``: tous les documents se trouvant dans la Corbeille lors
  de la clôture du dossier sont supprimés.

Les rôles et les autorisations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Par le processus de triage deux nouveaux rôles ont été introduits, celui
du ``gestionnaire des dossiers`` et celui de ``l’archiviste``.
Les rôles sont attribués globalement par mandant et sont liés aux autorisations suivantes:

``Le gestionnaire des dossiers``:

- Création et traitement des offres
- Accès aux offres
- Livraison d’offres
- Clôture d’une offre, comportant aussi la destruction du dossier

``L’archiviste``:

- Finalisation de l’évaluation d’offre
- Accès aux offres (même à celles d’autres mandants)
- Confirmation de l’archivage

Feature Flag
~~~~~~~~~~~~

Les fonctionnalités supplémentaires ne sont pas protégées par un Feature Flag
séparé mais par les nouveaux rôles, celui du ``gestionnaire des dossiers`` et
celui de ``l’archiviste``. Par défaut, ces rôles ne sont attribués à aucun groupe.


.. |img-triage-1| image:: ../_static/img/img-triage-1.png
.. |img-triage-2| image:: ../_static/img/img-triage-2.png
.. |img-triage-3| image:: ../_static/img/img-triage-3.png
.. |img-triage-4| image:: ../_static/img/img-triage-4.png
.. |img-triage-5| image:: ../_static/img/img-triage-5.png
.. |img-triage-6| image:: ../_static/img/img-triage-6.png
