Découvrir l'API avec Postman
============================

L'extension de chrome Postman_ permet de facilement découvrir l'API de manière interactive.


Configuration
-------------

Il convient d'activer l'option **"Retain headers on clicking on links"** dans les configurations de Postman pour que les liens que renvoies l'API puissent être suivis facilement.

|postman-retain-headers|


Cette option garantit que les HTTP-Header configurés pour un requête sont également employés pour une requêtes emises en cliquant sur un lien dans la réponse de celle-ci. Cela facilite la navigation de la structure au moyen de l'API.

Nous conseillons de désactiver l'option **"Send anonymous usage data to Postman"**.

Utilisation
-----------

Pour commencer, il faut déterminer le **HTTP Verb** utilisé pour la requête. Il peut être séléctionné à l'aide du menu déroulant correspondant. A droite du verbe HTTP, il faut ensuite indiquer l'**URL de l'objet** sur lequel l'on veut faire une requête:

|postman-request|


Il faut ensuite ajouter les les HTTP Headers nécessaires. Il s'agit d'une part de l'``Authorization`` Header, pour l'authentication avec le bon utilisateur, et d'autre part de l'``Accept`` Header qui assure que la requête sera traitée par l'API.

----------

Il y a un onglet séparé qui permet de générer l'``Authorization`` Header approprié pour une methode d'authentication donnée ainsi qu'un utilisateur et un mot de passe.

Il faut selectionner **"Basic Auth"** comme méthode d'authentication, ainsi qu'un utilisateur existant et ayant les authorisations nécessaires. Une fois ces paramètres indiqués, l'``Authorization`` Header peut être généré et inclus dans la requête en cliquant sur **"Update Request"**.

|postman-basic-auth|

----------

Il faut encore ajouter le ``Accept: application/json`` Header sous l'onglet **"Headers"**:

|postman-headers|


La requête est maintenant prête et peut être envoyée en cliquant sur **"Send"**.

La réponse du serveur apparaît alors sous la requête. Le lien de l'attribut ``@id`` peut-être suivi d'un simple clique. Postman prépare alors une nouvelle requête, utilisant les mêmes Headers, qui peut être envoyée avec un clique supplémentaire sur **"Send"**.

On peut ainsi facilement naviguer la structure d'un client GEVER au moyen de ``GET`` Requests.



.. _Postman: http://www.getpostman.com/

.. |postman-retain-headers| image:: ../../_static/img/postman_retain_headers.png
.. |postman-request| image:: ../../_static/img/postman_request.png
.. |postman-basic-auth| image:: ../../_static/img/postman_basic_auth.png
.. |postman-headers| image:: ../../_static/img/postman_headers.png

.. disqus::
