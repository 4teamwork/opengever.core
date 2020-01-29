Modèle de rôles
===============

Nachstehend werden die in OneGov GEVER enthaltenen Rollen erläutert.

Rôles globaux
~~~~~~~~~~~~~
Les rôles globaux sont valables pour un client physique. Le rôle est configuré dans le système par 4teamwork. Chaque rôle peut être attribué à un groupe Active Directory (AD).
Voici les rôles globaux et leurs caractéristiques:

-   *administrateur*: voit tous les dossiers, peut définir des droits aux niveaux du plan de classement ou de dossiers, peut adapter / compléter le plan de classement, peut gérer des modèles de documents, peut exécuter des «Force Check-In».

-   *responsable des rôles*: peut attribuer (limiter ou élargir) des droits dans les dossiers auxquels il a au moins des droits de lecture.

-   *records manager*: Ce rôle est normalement attribué à un cercle d’utilisateurs restreint, en charge du triage de dossiers au sein du client correspondant. Le rôle permet également d’établir des offres d’archivage au service d’archives responsable, Le rôle de records manager n’implique pas de droits supplémentaires aux dossiers; par conséquent seul les dossiers qu’un utilisateur est permis de regarder peuvent être sélectionnés pour en faire des offres d’archivage.

-   *archiviste*: Le rôle d’archiviste est en règle générale attribué aux collaborateurs d’un service d’archives, qui sont autorisés d’évaluer des offres d’archivage et de les transférer dans un dépôt d’archives à long-terme. Des utilisateurs du rôle d’archiviste peuvent accéder à tous les dossiers offerts et transférés, même s’ils ne sont pas attribués au client concerné. Cela facilite le contrôle des dossiers par les collaborateurs du service des archives pendant la période d’évaluation. Ce rôle remplit donc exclusivement la tâche de recevoir des dossiers pour l’archivage et d’évaluer des offres d’archivage.

-   *rôle spécial*:  boîte de réception par client physique ou virtuel: Ce rôle est configuré par 4teamwork. Il sert aussi comme destinataire impersonnel de tâches transmises à un client physique ou virtuel. Des personnes dans ce rôle peuvent saisir les courriers entrants, transmettre des documents depuis la boîte de réception, gérer des tâches impersonnelles adressées à celle-ci ainsi qu’agir comme suppléants en remplissant de telles tâches. En outre ils sont automatiquement autorisés de participer à toutes les actions exécutables sur les tâches adressées au client concerné.

En principe on peut dire que les rôles globaux de responsable des rôles et de records manager peuvent donner un droit fondamental à d’autres rôles, mais n’ont pas de droits pour consulter des dossiers eux-mêmes.

De plus il est défini que les rôles de responsable des rôles et de records manager ne peuvent être assignés qu’à condition que l’utilisateur concerné dispose déjà d’un droit de lecture au minimum.

Droits au sein du système de classement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Au sein d’une structure de classement, les droits d’utilisation peuvent être attribués comme suit:  lire dossier

–   Ajouter dossier
–   Modifier dossier
–   Clore dossier
–   Réactiver dossier.

Ces droits sont attribués aux groupes AD correspondants. En réalité cela signifie qu’en attribuant des rôles, des groupes d’utilisateurs spécifiques sont définis.

En règle générale, il est recommandé de former un groupe d’utilisateurs par organisation et possédant tous les droits susmentionnés sauf «réactiver». Autrement dit: ce groupe englobe les responsables respectifs de dossiers.

Le droit «réactiver dossier» est usuellement attribué à un groupe séparé, tenu compte du fait que la réactivation touche la période de retenue fixée. Ce droit n’est d’ordinaire qu’attribué au responsable GEVER de l’organisation respective ou alternativement au rôle d’administrateur.

Des rôles correspondants sont (best practice):


-   responsable de dossier: attribution d’utilisateurs à un (des) mandant(s); autorisations de lire, d’ajouter , de modifier et de clore des dossiers
-   responsable GEVER:  attribution d’utilisateurs à un (des) mandant(s); toutes autorisations (lire, ajouter , modifier, clore de dossiers)


Affichage des droits au niveau dossier
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Sans l’onglet « Info », dans la vue détaillée d’un dossier, ainsi que sous Actions > Déblocage, se trouve un aperçu des rôles et les droits d’utilisateurs pour ce dossier. L’aide contextuelle (clic sur «?» bleu) affiche plus de détails concernant les droits du groupe ou l’utilisateur donné. En plus d’une autorisation initiale obtenue par l’intermédiaire de LDAP, il est aussi possible d’accorder une autorisation temporaire pour la durée d’une tâche à accomplir. Pour en savoir plus consultez :ref:`label-taches-flux-travail`.

|img-rollenmodell-1|

.. |img-rollenmodell-1| image:: img/media/img-rollenmodell-1.png


.. disqus::
