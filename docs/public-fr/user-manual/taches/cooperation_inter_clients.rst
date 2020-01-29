
.. _label-cooperation_ic:

Coopération inter-clients
--------------------------

Créer une tâche inter-clients
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

La création d’une tâche inter-clients ne change que très peu de celle d’une tâche à être complétée par quelqu’un du même client.

L’icône suivante identifie une tâche inter-clients :

|img-cooperation_inter_mandants-01|

L’exemple suivant traite de la vérification d’une commande de matériel.
Créez une tâche et joignez-y tous les documents dont le mandataire aura besoin pour la compléter. Tous les autres documents du dossier resteront invisibles pour lui.

Dans le champ *Mandataire*, sélectionnez le destinataire de la tâche. En règle générale, c’est la boîte de réception du client responsable qui est choisie. Il est toutefois aussi possible de directement sélectionner le chargé d’affaires pertinent.

   |img-cooperation_inter_mandants-02|

Une fois la boite réception du client pertinent définie en tant que Mandataire, et la tâche sauvegardée, celle-ci apparaîtra dans la boite de réception de celui-ci (Onglet *tâches reçues*). Les personnes disposant des droits « boite de réception » peuvent donc assigner la tâche à la bonne personne.

Si un utilisateur spécifique a été choisi, la tâche apparaîtra chez lui dans les onglets *Sommaire* et *Mes tâches reçues*.

   |img-cooperation_inter_mandants-03|

Modifier une tâche inter-clients
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Les dossiers ne sont pas copiés pour les tâches inter-clients dans OneGov GEVER, ce sont les autres services qui viennent participer au dossier d’affaire courant. Cela signifie que les services participants ont des droits de lecture et modification directement dans le dossier du mandant. Pour le mandataire, seule une tâche est créée, pas de dossier. Pour cette raison, la tâche apparaît uniquement dans *vue d’ensemble personnelle*/*Mes tâches reçues*, ou dans la boîte de réception du client, si elle n’a pas encore été assignée à un utilisateur spécifique. Pour le traitement de la tâche, OneGov GEVER offre la possibilité de travailler sur des documents directement dans le dossier du mandant d’où ils proviennent ou dans le client de l’utilisateur courant.

Ouvrir, assigner et accepter une tâche inter-clients
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Selon besoin, la tâche est réattribuée à un chargé d’affaires via *Actions → Ré-attribuer*. Cela n’est possible que si l’utilisateur dispose de droits appropriés (Boite de réception, Admin).

1.	Cliquer le bouton « Ré-attribuer ».

  |img-cooperation_inter_mandants-04|

2.	Sélectionner l’utilisateur chargé de traiter la tâche.

  |img-cooperation_inter_mandants-05|

3.	Sommaire avec le nouvel utilisateur en charge de la tâche.

  |img-cooperation_inter_mandants-06|

A ce moment, on est automatiquement envoyé dans le client d’origine de la tâche dans un nouvel onglet de navigateur. Le mandataire ne voit que les documents du dossier qui ont été référencés dans la tâche. Même le système de classement n’est visible que dans une forme réduite. Afin de maintenir une vue d’ensemble, le « Client hôte » est affiché en grisé.

Sélectionnez *Actions → Accepter*.

OneGov GEVER propose maintenant 3 options pour traiter la tâche :

  |img-cooperation_inter_mandants-07|

1.	Directement dans le dossier du client d’origine

2.	En sauvegardant dans un dossier existant de son propre client

3.	En sauvegardant dans un nouveau dossier dans son propre client


Travailler directement dans le dossier du client d’origine
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

En acceptant la tâche, sélectionnez l’option *Travailler directement dans le dossier du client*.

|img-cooperation_inter_mandants-08|

Un nouvel onglet s’ouvre dans le navigateur et vous mène directement dans le client depuis lequel la tâche a été envoyée. Seuls les documents auxquels la tâche fait référence sont visibles. Le système de classement est affiché de façon restreinte et en grisé.

La tâche peut maintenant être traitée de la même manière qu’au sein de votre propre client. Il est possible d’effectuer un check-out/check-in pour modifier un document ou encore le mettre à jour par un téléchargement depuis votre système de fichiers.

Les tâches accomplies et leurs contenus restent visibles pour le mandataire et les utilisateurs disposant des droits d’admin ou de boîte de réception jusqu’à l’archivage du dossier chez le client d’origine.


Traiter une tâche dans un dossier existant de son propre client
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Lors de l’acceptation de la tâche, sélectionnez l’option *Traiter dans un dossier existant de [votre client]* et cliquez sur *suivant*.

|img-cooperation_inter_mandants-09|

Sélectionnez le dossier cible en saisissant son nom ou en parcourant le système de classement par l’intermédiaire du bouton *Ajouter*. Seuls les dossiers actuellement ouverts sont affichés dans cette vue.

|img-cooperation_inter_mandants-10|

En cliquant sur *sauvegarder*, la tâche et tous les documents qui y sont liés sont recopiés dans le dossier choisi. Les documents recopiés avec la tâche sont pourvus du commentaire « Document copié d’une tâche (Tâche acceptée) ». Une référence à la tâche d’origine et son dossier est également ajoutée.

|img-cooperation_inter_mandants-11|

Dans le dossier du client d’origine, on trouvera aussi une référence à la tâche copiée par le mandataire. L’état des 2 tâches est automatiquement synchronisé.

|img-cooperation_inter_mandants-12|

La tâche peut maintenant être traitée dans son propre dossier, en y ajoutant, par example, de nouveaux documents ou en travaillant sur ceux auxquels la tâche fait référence.

.. note::
   Lorsque le mandataire modifie des documents référencés par le mandant, il fait cela sur des **copies** qui devront être retransmises au mandant à la conclusion de la tâche.

Lors de l’accomplissement de la tâche, il est possible de sélectionner dans un listing de documents, lesquels seront retournés au client d’origine. Les fichiers sélectionnés seront joints à la tâche sous forme de copies et ajoutés au dossier. Tous les documents retournés par le mandataire apparaissent chez le mandant avec le préfixe **RE : (Réponse)**. Au niveau de la Version, ces documents sont également pourvus d’un commentaire « Document copié d’une tâche (Tâche accomplie) ».

  |img-cooperation_inter_mandants-13|

Traiter une tâche dans un nouveau dossier de son propre client
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sélectionnez *Traiter dans un nouveau dossier de [votre client]* et cliquez sur *continuer*.

  |img-cooperation_inter_mandants-14|

Sélectionnez un numéro de classement sous lequel le nouveau dossier sera créé, soit en saisissant son nom, soit en parcourant le système de classement à l’aide du bouton *Ajouter*. Note : Si plusieurs types de dossiers sont utilisés dans le système (p. ex. dossiers d’affaires et dossiers de cas), une étape intermédiaire vous permettra de choisir le bon type.

|img-cooperation_inter_mandants-15|

En cliquant sur *sauvegarder*, un nouveau dossier est créé sous le numéro de classement sélectionné, en reprenant le nom de dossier du client d’origine. Il est possible de changer le nom du dossier à tout moment.

La tâche et tous les documents qui y sont liés sont recopiés dans le nouveau dossier. Les documents recopiés avec la tâche sont pourvus du commentaire « Document copié d’une tâche (Tâche acceptée) ». Une référence à la tâche d’origine et son dossier est également ajoutée.

Une référence à la tâche copiée par le mandataire est ajoutée à la tâche du dossier d’origine. L’état des 2 tâches est automatiquement synchronisé.

|img-cooperation_inter_mandants-16|

La tâche peut maintenant être traitée dans son propre dossier. Il est donc possible d’y ajouter des documents et de modifier les documents qui y étaient liés.

|img-cooperation_inter_mandants-17|

Dans le dossier du client d’origine, on retrouve également une référence à la tâche copiée par le mandataire. L’état de la tâche dans le client d’origine et de sa copie sont synchronisés automatiquement.

|img-cooperation_inter_mandants-18|

Lors de l’accomplissement de la tâche, il est possible de sélectionner dans un listing de documents, lesquels seront retournés au client d’origine. Les fichiers sélectionnés seront joints à la tâche sous forme de copies et ajoutés au dossier. Tous les documents retournés par le mandataire apparaissent chez le mandant avec le préfixe **RE : (Réponse)**. Au niveau de la Version, ces documents sont également pourvus d’un commentaire « Document copié d’une tâche (Tâche accomplie) ».


|img-cooperation_inter_mandants-19|

.. note::
   Si le mandataire travaille sur des documents transmis avec la tâche, il s’agit là de **copies** qui devront être retransmises au mandant lors de la complétion de la tâche.

Cas spécial: Tâche inter-clients « Pour prise de connaissance »
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Avec une tâche de type « Pour prise de connaissance », il est possible de procéder comme suit :

Le mandant crée une tâche de type « Pour prise de connaissance » pour un document donné à destination d’un autre client.

   |img-cooperation_inter_mandants-20|

Le mandataire ouvre la tâche depuis la boite de réception (et la réassigne, si nécessaire, au chargé d’affaire pertinent). Avec l'action *Clôturer*, la tâche est automatiquement clôturée dans le client d’origine.

   |img-cooperation_inter_mandants-21|

À l’étape suivante, le mandataire a la possibilité de sélectionner des documents qui seront copiés dans un de ses propres dossiers.

   |img-cooperation_inter_mandants-22|

En cliquant sur *Suivant*, il est ensuite possible de sélectionner le dossier de destination (soit par saisie directe, soit en parcourant le système de classement à l’aide de *Ajouter*).

   |img-cooperation_inter_mandants-23|

Après avoir cliqué sur *Sauvegarder*, les documents sélectionnés sont copiés dans le dossier cible. La tâche « Pour prise de connaissance » n’est pas copiée.

   |img-cooperation_inter_mandants-24|

Cas spécial: Déléguer
^^^^^^^^^^^^^^^^^^^^^

Avec la fonction *déléguer*, une tâche peut facilement être transmise à plusieurs intéressés, aussi bien internes qu’externes au client courant. Un exemple typique serait la procédure de consultation.

Créez tout d’abord une tâche avec les documents à être transmis aux autres services. Acceptez cette tâche pour voir apparaître l’option de délégation.

   |img-cooperation_inter_mandants-25|

   |img-cooperation_inter_mandants-26|

   |img-cooperation_inter_mandants-27|

La tâche peut maintenant être déléguée. Saisissez tous les destinataires de la tâche via le champ de saisie et sélectionnez les documents à être transmis avec la tâche.

Cliquez sur *Suivant*.

   |img-cooperation_inter_mandants-28|

   |img-cooperation_inter_mandants-29|

.. note::
   Attention : les documents joints ne sont pas copiés, il s’agit là d’un lien vers le document original.

Ajustez selon besoin de nom de la tâche et la date, puis sauvegardez.

   |img-cooperation_inter_mandants-30|

Après la sauvegarde, un nombre de sous-tâches correspondant au nombre de destinataires est généré. Les sous-tâches sont visibles depuis la tâche principale et vice-versa. Si des destinataires additionnels doivent être ajoutés après-coup, il est toujours possible d’utiliser la fonction *déléguer*, et ce un nombre illimité de fois.

   |img-cooperation_inter_mandants-24|

.. note::
   Si une délégation inter-clients a été créée, le destinataire a la possibilité de traiter la tâche directement dans le dossier du mandant, ou, alternativement, de travailler dans son propre dossier (Similairement à une tâche inter-clients).

   Si la tâche est traitée directement dans le dossier du client d’origine, il est à noter que le document devra probablement être téléchargé pour éviter que tout le monde travaille sur le même document (p.ex. pour des prises de position par différents services).

   La tâche principale ne peut être complétée et fermée seulement une fois que toutes les sous-tâches ont été accomplies.


   .. |img-cooperation_inter_mandants-01| image:: ../../_static/img/img-cooperation_inter_mandants-01.png
   .. |img-cooperation_inter_mandants-02| image:: ../../_static/img/img-cooperation_inter_mandants-02.png
   .. |img-cooperation_inter_mandants-03| image:: ../../_static/img/img-cooperation_inter_mandants-03.png
   .. |img-cooperation_inter_mandants-04| image:: ../../_static/img/img-cooperation_inter_mandants-04.png
   .. |img-cooperation_inter_mandants-05| image:: ../../_static/img/img-cooperation_inter_mandants-05.png
   .. |img-cooperation_inter_mandants-06| image:: ../../_static/img/img-cooperation_inter_mandants-06.png
   .. |img-cooperation_inter_mandants-07| image:: ../../_static/img/img-cooperation_inter_mandants-07.png
   .. |img-cooperation_inter_mandants-08| image:: ../../_static/img/img-cooperation_inter_mandants-08.png
   .. |img-cooperation_inter_mandants-09| image:: ../../_static/img/img-cooperation_inter_mandants-09.png
   .. |img-cooperation_inter_mandants-10| image:: ../../_static/img/img-cooperation_inter_mandants-10.png
   .. |img-cooperation_inter_mandants-11| image:: ../../_static/img/img-cooperation_inter_mandants-11.png
   .. |img-cooperation_inter_mandants-12| image:: ../../_static/img/img-cooperation_inter_mandants-12.png
   .. |img-cooperation_inter_mandants-13| image:: ../../_static/img/img-cooperation_inter_mandants-13.png
   .. |img-cooperation_inter_mandants-14| image:: ../../_static/img/img-cooperation_inter_mandants-14.png
   .. |img-cooperation_inter_mandants-15| image:: ../../_static/img/img-cooperation_inter_mandants-15.png
   .. |img-cooperation_inter_mandants-16| image:: ../../_static/img/img-cooperation_inter_mandants-16.png
   .. |img-cooperation_inter_mandants-17| image:: ../../_static/img/img-cooperation_inter_mandants-17.png
   .. |img-cooperation_inter_mandants-18| image:: ../../_static/img/img-cooperation_inter_mandants-18.png
   .. |img-cooperation_inter_mandants-19| image:: ../../_static/img/img-cooperation_inter_mandants-19.png
   .. |img-cooperation_inter_mandants-20| image:: ../../_static/img/img-cooperation_inter_mandants-20.png
   .. |img-cooperation_inter_mandants-21| image:: ../../_static/img/img-cooperation_inter_mandants-21.png
   .. |img-cooperation_inter_mandants-22| image:: ../../_static/img/img-cooperation_inter_mandants-22.png
   .. |img-cooperation_inter_mandants-23| image:: ../../_static/img/img-cooperation_inter_mandants-23.png
   .. |img-cooperation_inter_mandants-24| image:: ../../_static/img/img-cooperation_inter_mandants-24.png
   .. |img-cooperation_inter_mandants-25| image:: ../../_static/img/img-cooperation_inter_mandants-25.png
   .. |img-cooperation_inter_mandants-26| image:: ../../_static/img/img-cooperation_inter_mandants-26.png
   .. |img-cooperation_inter_mandants-27| image:: ../../_static/img/img-cooperation_inter_mandants-27.png
   .. |img-cooperation_inter_mandants-28| image:: ../../_static/img/img-cooperation_inter_mandants-28.png
   .. |img-cooperation_inter_mandants-29| image:: ../../_static/img/img-cooperation_inter_mandants-29.png
   .. |img-cooperation_inter_mandants-30| image:: ../../_static/img/img-cooperation_inter_mandants-30.png
   .. |img-cooperation_inter_mandants-31| image:: ../../_static/img/img-cooperation_inter_mandants-31.png
