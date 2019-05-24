Actions diverses
================

OneGov GEVER permet différentes actions qui peuvent être accomplies avec les documents :

- Consulter un document existant (mode lecture)

- Déplacer un document dans la corbeille

- Copier un document

- Envoyer un document par e-mail

- Export/Import ZIP

Consulter un document existant (mode lecture)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Cette fonction n’est disponible que quand un service de création de PDF correspondant
(par exemple Adobe LiveCycle Server) est installé et configuré avec OneGov GEVER.

Cliquez dans la liste sur l’icône du document que vous aimeriez consulter
et choisissez Aperçu PDF dans le Tooltip. De façon optionnelle, on peut ouvrir
le PDF sans quitter le browser de la page actuelle (niveau du dossier) avec la commande
Clic droit – Ouvrir un lien dans une nouvelle fenêtre. A partir des documents,
GEVER produit des fichiers PDF en arrière-plan. De cette façon on peut éviter que
des documents dont le check-out n’aurait pas été fait ne soient édités par inadvertance.

|img-document-36|

Le fichier peut maintenant être ouvert directement ou être enregistré dans le système de fichiers.
Le service de création demande un certain temps. Si on clique sur le fichier tout de suite
après l’enregistrement, l’aperçu PDF peut éventuellement ne pas être encore prêt.
Le message *PDF pas encore disponible, doit encore être constitué apparaît*.

Dans ce cas, en cliquant sur le fichier, le fichier original est affiché.
Si le fichier doit être édité, le check-out doit de nouveau être fait, sinon
les modifications ne seront pas sauvegardées !

Aperçu des formats de fichier qui peuvent être convertis en PDF (est cependant
dépendant de l’installation spécifique du service de création de PDF):

-  Standard: rtf, txt, jpg, htm, html

-  Bild: jpg, jpeg, bmp, gif, tif, tiff, png, jpf, jpx, jp2, j2k, j2c,
   jpc

-  Flash-Videos: swf, flv

-  Microsoft Word: doc, docx

-  Microsoft Excel: xls, xlsx

-  Microsoft Powerpoint: ppt, pptx

-  Microsoft Visio: vsd

-  Microsoft Project: mpp

-  Microsoft Publisher: pub

-  OpenOffice Writer: odt, ott, sxw, stw

-  OpenOffice Calc: ods, ots, sxc stc

-  OpenOffice Draw: odg, otg, sxd, std

-  OpenOffice Impress: odf, otp, sxi, sti

-  Adobe Framemaker: fm

-  Adobe Photoshop: psd

Déplacer un document dans la corbeille
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Les documents sur OneGov GEVER ne peuvent pas être supprimés par un utilisateur
normal mais seulement déplacés vers la corbeille. De là, les documents peuvent
être réactivés. L’administrateur a la possibilité supplémentaire de faire
un `Soft-Delete <https://docs.onegovgever.ch/admin-manual/soft-delete/#label-soft-delete>`_
(disponible uniquement en allemand).
Pour déplacer un document dans la corbeille, procédez de la façon suivante:

1. Cliquez dans la liste de documents sur le document à supprimer.

2. Choisissez sous *Action supplémentaires* l‘action *Déplacer dans la corbeille*.

|img-document-37|

3. Avec cette action, OneGov GEVER passe à l’onglet *Corbeille* et y transfert le document.
   Au besoin, le document peut être réactivé.

|img-document-38|

Copier un document
~~~~~~~~~~~~~~~~~~

Dans la liste des documents, cliquez sur le document à copier et choisissez
Action *supplémentaires → Copier*.

|img-document-39|

Ouvrez finalement le dossier-destination et choisissez *Actions → Coller*. Le document
copié sera alors automatiquement classé sous l’onglet *Document*.

|img-document-40|

Le document copié apparaît dans la liste des documents comme *Copie de ….*

|img-document-41|

Envoyer un document par e-mail
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dans la liste des documents, choisissez le document que vous aimeriez envoyer
et cliquez sur Actions *supplémentaires → Envoyer par e-mail*.

|img-document-42|

Un formulaire d’e-mail s’ouvre alors. Les champs obligatoires sont indiqués par un carré rouge.
Les documents choisis peuvent être envoyés soit comme fichier joint d’un e-mail
soit comme un lien direct vers le document GEVER intégré dans le mail (option cliquer).
L’e-mail contient dans le deuxième cas seulement le lien du document GEVER
et n’a aucun fichier en annexe (voir exemple ci-dessous).

|img-document-43|

Il suffit au destinataire de cliquer sur le lien du document. La condition est
cependant que le destinataire soit autorisé par le mandant concerné à avoir
accès au dossier correspondant!

L’envoi de l’e-mail est mentionné dans le journal. Le document envoyé est
référencé dans la colonne *Commentaires*; le destinataire, l’objet et le message y
sont également indiqués (aperçu complet avec le curseur de la souris).

|img-document-44|

Export/Import ZIP
~~~~~~~~~~~~~~~~~

.. _label-export-zip-documents:

Export ZIP
----------

Un document unique ou plusieurs documents peuvent être empaquetés
dans un fichier ZIP puis exportés.

- Dans l’aperçu des documents, sélectionnez les documents que vous devez exporter
  (plusieurs documents peuvent être sélectionnés avec :kbd:`Ctrl` clic droit de la souris)

- En dessous de la liste des documents, ouvrez le menu Actions supplémentaires
  et cliquez sur Exporter comme fichier ZIP.  De cette façon, tous les documents
  d’un dossier seront exportés.

  |img-document-45|

- Choisissez l’emplacement de sauvegarde pour le fichier ZIP.

.. note::
   Avec un téléchargement ZIP, le chemin d’accès du fichier permet au maximum 260 signes.
   Faites attention que le titre ne dépasse pas cette restriction. Dès Windows 10 (version 1607),
   il existe la possibilité de permettre des chemins d’accès de fichiers plus longs.
   En alternative, `le programme ZIP <https://www.7-zip.org>`_ peut être installé, il permet de traiter
   des noms ZIP plus longs.

Import ZIP
----------

Les fichiers ZIP peuvent être téléversés dans OneGov GEVER. Ces derniers ne
seront cependant pas automatiquement décompactés par le système mais plutôt directement
classés dans les documents. Le contenu des archives ZIP ne sera pas indexé et par
conséquent ne pourra pas être recherché. Une recherche n’est possible qu’au niveau
des métadonnées. Un service de création PDF (aperçu PDF) n’est également pas disponible.

.. note::
   Le téléversement de fichiers ZIP n’est en principe pas conseillé. Cependant, si
   des fichiers ZIP sont tout de même téléversés, ils devront alors être empaquetés
   avec l’Explorer Windows (clic droit de la souris > Envoyer > Classeur comprimé ZIP)

.. |img-document-36| image:: ../_static/img/img-document-36.png
.. |img-document-37| image:: ../_static/img/img-document-37.png
.. |img-document-38| image:: ../_static/img/img-document-38.png
.. |img-document-39| image:: ../_static/img/img-document-39.png
.. |img-document-40| image:: ../_static/img/img-document-40.png
.. |img-document-41| image:: ../_static/img/img-document-41.png
.. |img-document-42| image:: ../_static/img/img-document-42.png
.. |img-document-43| image:: ../_static/img/img-document-43.png
.. |img-document-44| image:: ../_static/img/img-document-44.png
.. |img-document-45| image:: ../_static/img/img-document-45.png
