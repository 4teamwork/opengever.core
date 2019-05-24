Travailler les documents
========================

External Editor / Office Connector
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pour le traitement des documents, External Editor ou Office Connector doivent
être installés. Nous conseillons Office Connector étant donné qu’il est
en permanence développé et amélioré par 4teamwork.

Vous pouvez télécharger Office Connector pour Windows et Mac `sur le site de 4teamwork <https://www.4teamwork.ch/fr/solutions/office-connector/>`_.
Là, vous trouverez également les liens de téléchargement
pour les deux applications qui ne sont plus entretenues,
External Editor pour Windows et ZopeEditManager pour Mac.

Principes de base
~~~~~~~~~~~~~~~~~

Pour pouvoir travailler des documents, le check-out doit avoir été fait. Une fois
que le check-out du document a été fait, le document n’est disponible que pour
le collaborateur ou la collaboratrice qui en a fait le check-out.

On reconnait un document dont le check-out a été fait au statut *En cours de
traitement* inscrit dans la colonne de la liste des documents.

Travailler uniquement les métadonnées (propriétés)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Avec la souris, allez dans la liste des documents sur l’icône du document dont
vous aimeriez travailler les propriétés (par exemple Titre, Description)
et choisissez l’option Modifier les métadonnées dans la fenêtre Tooltip affichée.

|img-document-20|

Vous trouverez également cette option dans le masque de propriétés
du document correspondant :

|img-document-21|

Dans le masque de saisie du document, les modifications souhaitées peuvent
être opérées dans un second temps.

Faire le check-out et éditer un document
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Avec la souris, allez dans la liste des documents sur l’icône du document
que vous aimeriez éditer et choisissez l’option Faire le check-out / Editer.

|img-document-22|

Le fichier n’est ouvert que par External Editor / Office Connector avec
l’application correspondante; il peut ensuite être travaillé. Pendant
le traitement, External Editor / Office Connector constitue un fichier
temporaire qui disparaitra à nouveau après le checkin.

Pendant le traitement, enregistrez régulièrement le fichier, en particulier avant
que vous ne quittiez votre place de travail pour un long moment. Quand vous aurez
fini le traitement, veuillez fermer le fichier et l‘application (par exemple Microsoft Word).
Dès la version 0.9.5, External Editor / Office Connector affiche si des modifications
ont été faites ou non, et ce grâce à un message d’information apparaissant après
la fermeture du travail.

**Important:** Un fichier ne peut être ouvert qu'en un seul exemplaire par
l'utilisateur qui a effectué le check-out pour être travaillé dans l’application
correspondante. Si pendant ce temps on veut ouvrir encore une fois ce même document
sur l’aperçu des documents dans OneGov GEVER avec l’icône du crayon ou un lien,
une indication correspondante apparaît alors.

Après la fermeture, le masque des propriétés du document sera affiché avec
les autres possibilités de traitement.

|img-document-23|

1. **Annuler le check-out:** Les changements effectués au document seront annulés et
   les données seront remises dans leur dernier état édité (= version avant le check-out).

2. **Checkin:** Avec Checkin, le document est à nouveau disponible pour les autres collaborateurs.

Envoyer avec un programme de mails :
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sous le bouton Editer / Faire le check-out apparaît en supplément le bouton
Envoyer avec le programme e-mail.

|img-document-24|

En cliquant dessus, le programme de mails s’ouvre avec un mail préparé dans
lequel le document est déjà inséré et où le lien OneGov GEVER vers le document
en question est consigné dans le texte du mail. Pour des fins documentaires, un BCC
est envoyé dans le dossier dans lequel le document est classé.

|img-document-25|

Le mail peut ensuite être travaillé au gré du collaborateur, être complété et
être envoyé au destinataire souhaité.

Faire le checkin directement:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Avec Office Connector, le checkin d’un document peut aussi être fait directement
(et non pas en deux étapes comme décrit plus haut dans le chapitre Faire
le check-out et éditer un document). Pour cela, faites le check-out du document
puis effectuez les modifications souhaitées, sauvegardez et fermez le document.
Un message automatique s’affiche ensuite, message avec lequel le checkin du document
peut directement être fait. Au besoin, un commentaire concernant les modifications
peut également être consigné :

|img-document-26|

Après avoir fait le checkin du document avec succès, le message
de confirmation suivant s’affiche :

|img-document-27|

Types de documents supportés
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

External Editor et Office Connector supportent les applications suivantes
à la condition que l’application respective soit installée sur l'ordinateur personnel.

====================== ========= =========
Application             Windows     Mac
====================== ========= =========
MS Excel                  x          x


MS Powerpoint             x          x


MS Word                   x          x


MS Visio                  x


MS Project                x


MS OneNote                x


Open office                          x


Acrobat Pro, Reader       x          x


Adone InDesign            x


Adobe Photoshop           x


Adobe Illustrator         x


MindManager               x


Preview                              x


TextEdit                             x


Apple Numbers                        x


Apple Keynote                        x


Apple Pages                          x

====================== ========= =========

Le traitement avec Adobe pour les fichiers graphiques (Photoshop, Illustrator, InDesign)
avec External Editor fonctionne, certes, mais n’est cependant pas conseillé, étant
donné que des erreurs ont déjà été constatées. Pour de tels fichiers et pour d’autres
fichiers qui ne sont pas supportés, ils doivent être suivis selon l’indication ci-après,
sous `Travailler des documents sans External Editor / Office Connector`_.

Travailler des documents sans External Editor / Office Connector
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Choisissez l‘action *Faire le check-out*. Après le check-out, cliquez sur *Modifier
les métadonnées*, le masque du document s’ouvre alors.

Choisissez maintenant *Remplacer par un nouveau fichier* et cherchez dans le système
de fichiers le fichier souhaité. Avec Sauvegarder et en faisant le checkin du document,
le nouveau fichier est sauvegardé comme la version la plus récente.

|img-document-28|

Cette action est aussi utile quand des fichiers ne peuvent pas être travaillés avec
External Editor ou quand External Editor n’est pas disponible.

Une autre manière de faire est aussi possible:

- Choisissez l‘action *Faire le check-out*.

- Choisissez Télécharger une copie et finalement Enregister le fichier pour
  l’enregistrer entre-temps dans le système de fichiers resp. sur le bureau. Attention:
  Par ce procédé, les modifications ne seront pas automatiquement importées dans GEVER
  et ne le seront que lorsque le document aura été à nouveau téléversé et que le checkin
  aura été effectué.

|img-document-29|

Travaillez le fichier et fermez-le après l’enregistrement des modifications.
Pour importer le fichier modifié vers OneGov GEVER, le fichier en question
peut être tiré vers GEVER via le drag‘n‘drop.

Avec Sauvegarder et en faisant le checkin du document, le nouveau fichier
est sauvegardé comme la version la plus récente.

.. |img-document-20| image:: ../_static/img/img-document-20.png
.. |img-document-21| image:: ../_static/img/img-document-21.png
.. |img-document-22| image:: ../_static/img/img-document-22.png
.. |img-document-23| image:: ../_static/img/img-document-23.png
.. |img-document-24| image:: ../_static/img/img-document-24.png
.. |img-document-25| image:: ../_static/img/img-document-25.png
.. |img-document-26| image:: ../_static/img/img-document-26.png
.. |img-document-27| image:: ../_static/img/img-document-27.png
.. |img-document-28| image:: ../_static/img/img-document-28.png
.. |img-document-29| image:: ../_static/img/img-document-29.png
