Oneoffixx
=========

Oneoffixx_ is a |microsoft-office|_ template management solution from Sevitec_.
It needs its own client, but the ``opengever.core`` integration relies on
|office-connector|_ also being installed.

It can use |content-controls|_ for injecting values into the documents.

.. _microsoft-office: https://www.office.com/
.. |microsoft-office| replace:: Microsoft Office

.. _Oneoffixx: https://oneoffixx.com/en/
.. _Sevitec: https://www.sevitec.ch/

.. _office-connector: https://www.4teamwork.ch/loesungen/office-connector/
.. |office-connector| replace:: Office Connector

.. _content-controls: https://docs.microsoft.com/en-us/visualstudio/vsto/content-controls
.. |content-controls| replace:: content controls

Architecture
------------

The system, as we use it, has 6 moving parts which concern us.

Oneoffixx backend
^^^^^^^^^^^^^^^^^

From the point of view of the Oneoffixx backend, both OpenGEVER and Office
Connector are LOB-Apps.

.. image:: ../_static/img/oneoffixx-system-overview-onpremise.png

We need to have whitelisted Office Connector in the backend as a callback
target for the InvokeProcess_ mechanism.

.. _InvokeProcess: https://docs.oneoffixx.com/connect/de/connect-commands/#invokeprocess

We also need to have created a backend to backend account for the OpenGEVER
installation. This means we will have a client id, client secret and a
preshared key we need to use in order to authenticate_ to the backend in order
to obtain a per user impersonation grant ``urn:oneoffixx:oauth2:impersonate``.

Customer AD
^^^^^^^^^^^

The users in OpenGEVER are identified by a SID_ provided by the customer AD_.
We have built support into our fork of Products.LDAPUserFolder_ for this. This
also means that a pure Zope user, such as a Zope admin user, will not have a
SID.

We provide a site-wide |fake_sid_registry_flag|_ for setting a fake SID for
development and debugging purposes.

.. _SID: https://docs.microsoft.com/en-us/windows/desktop/secauthz/security-identifiers
.. _AD: https://docs.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview

.. _fake_sid_registry_flag: https://github.com/4teamwork/opengever.core/blob/2019.2.1/opengever/oneoffixx/interfaces.py#L51-L57
.. |fake_sid_registry_flag| replace:: registry flag

.. _Products.LDAPUserFolder: https://github.com/4teamwork/Products.LDAPUserFolder

Oneoffixx client
^^^^^^^^^^^^^^^^

The client needs a configuration file, which points it to the correct backend
instance. This configuration file will also have a preshared key and a license
key embedded into it. The user will additionally need to auth into the client
over an SSO provider.

The client provides access to the per user and per group templates, some of
which we do not support through OpenGEVER, and additionally offers the
possibility to flag some of the templates as user favorites.

Office Connector
^^^^^^^^^^^^^^^^

Office Connector, starting from version 1.8.0, has supported Oneoffixx URLs and
payloads. Office Connector obtains a |oneoffixx-instruction-xml|_ from the
freshly created shadow document in OpenGEVER, flushes the file to disk and
proceeds to do a normal reauth / checkout cycle with the freshly created file
in place. We originally decided to abuse the redownload prevention logic of the
reauth cycle in order to have minimised the amount of new logic to have been
introduced into the implementation.

.. _oneoffixx-instruction-xml: https://docs.oneoffixx.com/connect/de/xml-schema/
.. |oneoffixx-instruction-xml| replace:: Oneoffixx instruction XML

As we've uncovered and fixed issues over time, a version lower than 1.9.2
should not be used.
