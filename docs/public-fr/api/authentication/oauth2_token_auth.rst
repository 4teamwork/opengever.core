Authentification OAuth2 avec clés de service et Tokens
------------------------------------------------------

Cette méthode d'authentification permet une authentification de machine à machine par l'utilisation de clés de service, de demandes signées de et des Tokens d'accès de courte durée.

Cette méthode est adaptée à l'authentification des applications de service (p. ex. applications spécialisées), qui peuvent gérer l'authentification de manière indépendante et
sans interaction humaine.

Vue d'ensemble
^^^^^^^^^^^^^^
Cette authentification des Requests s'effectue par l'intermédiaire d'**Access-Tokens** de courte durée de vie, qui doivent être régulièrement renouvelés par l'application de service.

La procuration d'un Access-Tokens se fait par un soi-disant **"JWT Authorization Grant"** - une requête signée, par laquelle l'application de service demande un nouvel Access-Token.

Cet Authorization Grant doit être signé à l'aide d'une **clé privée**, liée à un utilisateur spécifique et qui a été créée dans GEVER via l'interface utilisateur.


Flux d'authentification
^^^^^^^^^^^^^^^^^^^^^^^

Le processus comprend quatre étapes:

1. Émission d'une :ref:`Clé de service <manage-service-keys>` pour un utilisateur dans GEVER, et dépôt de cette clé dans l'application de service.
2. L'application de service génère un :ref:`JWT Authorization Grant <create-jwt-authorization-grant>`, afin de demander un Access-Token, signant ce Grant avec la clé privée.
3. L'application de service utilise ce JWT Grant pour récupérer un :ref:`Access Token <obtain-access-token>` dans GEVER.
4. L'application de service utilise ensuite cet Access-Token pour :ref:`authentifier <authenticate-using-token>` ses Requests sur GEVER (Jusqu'à son expiration, où un nouveau JWT Grant doit être crée pour à nouveau récupérer un Token).

Si une clé de service a déjà été créée pour l'utilisateur et a été déposée dans l'application de service, le flux d'authentification se déroule comme suit:

|tokenauth-auth-flow|

..
   Image Source: https://drive.google.com/open?id=1F8C4QB57ALF705vx9xkTDIX8AqMCJ30v


.. _manage-service-keys:

Gestion de clés de service
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: ../../_static/img/tokenauth-manage-keys-action.png
   :align: right

Les clés de service d'un compte peuvent être administrées via l'interface utilisateurs de OneGov GEVER. Pour les comptes, pour lesquels l'émission de clés a été autorisée, l'interface de gestion est accessible via l'action :guilabel:`Gérer les clés de service` est accessible dans le menu des réglages personnels.

|tokenauth-manage-keys|

------------


Via l'action :guilabel :`Émettre une nouvelle clé de service` une nouvelle clé peut être généré. Au minimum un titre doit être attribué à la clé et devrait décrire l'utilisation prévue.

optionnellement, il est possible de définir une plage IP, à partir de laquelle les jetons d'accès liés à la clé peuvent être utilisés pour l'authentification.

|tokenauth-issue-key|

------------

Après sa génération, la clé privée est affichée exactement une fois et doit être enregistrée. La clé publique reste sur le serveur et la clé privée est à stocker dans un système de fichiers de manière à ce qu'uniquement l'application de service puisse y accéder.

|tokenauth-download-key|

------------

Dans le formulaire de modification, il est possible d'éditer le titre et l'IP-Range de clés existantes. Les modifications de l'IP-Range autorisée sont immédiatement pris en compte et sont valables également pour les Access Tokens qui ont déjà été générés à l'aide de cette clé.

|tokenauth-edit-key|

------------

L'heure et la date de la dernière fois que la clé a été utilisée pour récupérer un Access-Token est affichée dans la vue d'ensemble de l'interface de gestion

En cliquant sur cette date, il est possible de visualiser des logs détaillés des dernières utilisations de la clé.- Une utilisation est enregistrée dans l'historique lorsque la clé respective utilise le JWT Authorization Grant qui y correspond pour récupérer un Access-Token.

|tokenauth-usage-logs|

.. _create-jwt-authorization-grant:

Créer un JWT Authorization Grant
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Pour obtenir un Access Token, l'application de service génère un JWT Authorization Grant, et signe ce dernier à l'aide de sa clé privée.

Un Authorization Grant est un JWT (JSON Web Token) avec lequel un lot de Claims prédéfinis qui, hormis leur timestamp, peuvent toutes être dérivées de la clé de service.

Le JWT doit contenir les Claims suivants:

==== ========================================================================
Nom  Description
==== ========================================================================
iss  Issuer - la ``client_id`` provenant de la Service-Key
aud  Audience - la ``token_uri`` provenant de la Service-Key
sub  Subject - la ``user_id`` provenant de la Service-Key
iat  La date et heure à laquelle le Grant a été émis, indiqué au format
     Unix-Timestamp [#f1]_
exp  la date d'éxpiration du JWTs, au format Unix-Timestamp [#f1]_.
     Maximum: 1 jour, recommandé: 1 heure
==== ========================================================================

.. [#f1] secondes depuis epoch (00:00:00 UTC, 1er Janvier, 1970).


Le JWT doit être signé par la clé privée. ``RS256`` (Signature RSA avec SHA256) est le seul algorithme de signature supporté.

Pour les applications .NET, il existe une librairie du nom de `Jwt.Net <https://github.com/jwt-dotnet/jwt>`_, qui peut être utilisée pour la signature de JWTs.

Exemple en Python:

.. code:: python

    import json
    import jwt
    import time

    # Load saved key from filesystem
    service_key = json.load(open('my_saved_key.json', 'rb'))

    private_key = service_key['private_key'].encode('utf-8')

    claim_set = {
        "iss": service_key['client_id'],
        "sub": service_key['user_id'],
        "aud": service_key['token_uri'],
        "iat": int(time.time()),
        "exp": int(time.time() + (60 * 60)),
    }
    grant = jwt.encode(claim_set, private_key, algorithm='RS256')


.. _obtain-access-token:

Obtenir un Access-Token
^^^^^^^^^^^^^^^^^^^^^^^

Pour obtenir un Access-Token, l'application client effectue une Token-Request, pour échanger le JWT créé et signé précédemment  contre un Token.

La Token-Request doit être effectuée sur la ``token_uri`` définie dans la Service-Key. Cette Request doit être du type ``POST``, ayant pour ``Content-Type: application/x-www-form-urlencoded`` et, dans le body, les paramètres form-encoded.

Deux paramètres sont requis:

=========== ==================================================================
Nom         Description
=========== ==================================================================
grant_type  Doit toujours être ``urn:ietf:params:oauth:grant-type:jwt-bearer``
assertion   Le JWT Authorization Grant
=========== ==================================================================

L'Endpoint Token répond ensuite avec une Token Response, contenant l'Access-Token:

.. code:: json

    {
      "access_token": "<token>",
      "expires_in": 3600,
      "token_type": "Bearer"
    }

Cette Response est du type ``Content-Type: application/json`` et contient un
JSON Body encodé.

Exemple en Python:

.. code:: python

    import requests

    GRANT_TYPE = 'urn:ietf:params:oauth:grant-type:jwt-bearer'

    payload = {'grant_type': GRANT_TYPE, 'assertion': grant}
    response = requests.post(service_key['token_uri'], data=payload)
    token = response.json()['access_token']


En cas d'erreur, le Token Endpoint répond avec un JSON-Dictionary, contenant les détails de l'erreur:

.. code:: json

    {
      "error": "invalid_grant",
      "error_description": "<Description de l'erreur>"
    }


.. _authenticate-using-token:

Utiliser l'Access Token pour l'autentification
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

L'application client peut ensuite utiliser l'Access-Token pour authentifier ses Requests. Le Token doit être envoyée en tant que ``Bearer`` pour son header HTTP ``Authorization``.

Une fois que le Token a expiré, l'application client doit créer et signer un nouveau JWT
Grant et l'utiliser pour obtenir un nouveau Token.

Exemple en Python:

.. code:: python

    with requests.Session() as session:
        session.headers.update({'Authorization': 'Bearer %s' % token})
        response = session.get('http://localhost:8080/Plone/')
        # ...

Lorsque le Token envoyé par l'application client est expiré, le serveur retourne l'erreur suivante:

.. code:: json

    {
      "error": "invalid_token",
      "error_description": "Access token expired"
    }

Le client doit, dans ce cas, créer et signer un nouveau JWT, et réitérer la Request précédemment  échouée avec le nouveau Token.


Implémentation client recommandée
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Les étapes décrites ci-dessus présentent un cas simple, où un client ne doit que s'authentifier une seule et unique fois.

Pour un client qui doit effectuer des Requests continuellement, il est nécessaire d'implémenter une certaine logique pour renouveler le Token de manière récurrente.

Cette logique devrait être à peu près implémentée comme suit:

|tokenauth-client-flow|

..
   Image Source: https://drive.google.com/open?id=1wVua7R5VQUxJKGL8dq1kGV4AjLgjGSXZ


Au lieu d'essayer de prédire la date d'expiration du jeton, le client doit s'attendre à ce que chaque requête puisse échouer à cause d'un jeton expiré. Dans ce cas, il peut obtenir un nouveau jeton et répéter la demande avec ce dernier.

Pour l'implémentation, nous recommandons donc de déléguer l'exécution de Requests à une classe contenant toute la logique de retry et d'éviter de soumettre des requêtes directement depuis la logique business de l'application client.

Lors de l'exécution de requêtes dans le but d'obtenir de nouveaux Tokens, 2 choses sont à considérer:

- Ces requêtes ne doivent pas contenir de Header ´´Authorization´´ au risque d'échouer, entre autres, lorsque celles-ci envoient un Token expiré.
- Ces requêtes doivent, comme décrit ci-dessus, être exécutées avec
  ``Content-Type: application/x-www-form-urlencoded`` alors que les requêtes sur l'API GEVER doivent contenir ``Content-Type: application/json``.

Pour ces raisons, il est recommandé d'utilser des sessions distinctes (connexions http persistantes) pour les requêtes normales et le renouvellement de Tokens.

Exemple d'implémentation en Python pour un client à authentification continue.

.. container:: collapsible

    .. container:: header

       **Exemple de client (Python)**

    .. literalinclude:: examples/oauth2-client-example.py


.. |tokenauth-manage-keys-action| image:: ../../_static/img/tokenauth-manage-keys-action.png
.. |tokenauth-manage-keys| image:: ../../_static/img/tokenauth-manage-keys.png
.. |tokenauth-issue-key| image:: ../../_static/img/tokenauth-issue-key.png
.. |tokenauth-download-key| image:: ../../_static/img/tokenauth-download-key.png
.. |tokenauth-edit-key| image:: ../../_static/img/tokenauth-edit-key.png
.. |tokenauth-usage-logs| image:: ../../_static/img/tokenauth-usage-logs.png
.. |tokenauth-auth-flow| image:: ../../_static/img/tokenauth-auth-flow.png
.. |tokenauth-client-flow| image:: ../../_static/img/tokenauth-client-flow.png


.. disqus::
