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

OpenGEVER
^^^^^^^^^

OpenGEVER has service credentials with which it authenticates to the Oneoffixx
backend and we trust the LDAP / AD to provide the required per user data in
order to be able to impersonate each user.

We have a wizard for creating a new document from a Oneoffixx template. This
wizard impersonates and authenticates the user with the Oneoffixx backend,
fetches the correct template library for the user, fetches the template groups
and templates the user has access to and finally fetches the user favorites.
All of the templates fetched are filtered in regards to the ability to use them
through OpenGEVER, so we avoid offering the users options they could not
successfully use. All of the requests to the Oneoffixx backend are cached per
user. Changing the cache timeout registry setting immediately invalidates all
existing Oneoffixx caches.

The wizard produces a new document in the shadow state, with the template data
stored as object annotations. The checkout URL for such a shdow document is
Oneoffixx specific. There is also a view to render the Oneoffixx instruction
XML based on the annotations of the document object. Uploading a file to the
document will make the document exit the shadow state and become just a normal
document.

The XML currently produces the document metadata and injects the DocProperties_
into the template by two means. The templates do not use DocProperties and
these do not end up in the produced file.

.. _DocProperties: https://docs.microsoft.com/en-us/dotnet/api/documentformat.openxml.drawing.wordprocessing.docproperties

We do not currently inject ContentControls_ into the instruction XML. These
could get used by a template and could end up in the final document.

.. _ContentControls: https://docs.microsoft.com/en-us/visualstudio/vsto/content-controls

Template editor
^^^^^^^^^^^^^^^

Oneoffixx ships a separate |template-editor|_ software, with which organisation
admins can create and edit templates for their organisation.

.. _template-editor: https://docs.oneoffixx.com/docengine/de/subtemplates/
.. |template-editor| replace:: template editor

Flow
----

Herein we describe a happy path example data flow starting from OpenGEVER,
going through Office Connector and Oneoffixx and ending up back in OpenGEVER.

The Oneoffixx API client implemented in OpenGEVER is a per instance / ZEO
client singleton_. We use a singleton in order to share the same HTTP session
between all the requests. This, together with aggressive caching, ensures we do
not end up spamming the Oneoffixx backend or tripping up web application
firewalls.

.. _singleton: https://github.com/4teamwork/opengever.core/blob/2019.2.1/opengever/oneoffixx/api_client.py#L59-L74

If we receive a ``401`` response from any of the requests in the api client, we
refresh_ the access token and try once again. We do not directly authenticate
users: we only ever do so as a side effect of having failed to fetch something
from the Oneoffixx backend.

.. _refresh: https://github.com/4teamwork/opengever.core/blob/2019.2.1/opengever/oneoffixx/api_client.py#L266-L269
