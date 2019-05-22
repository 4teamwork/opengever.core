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

Backend authentication
^^^^^^^^^^^^^^^^^^^^^^

The per cluster authentication credentials are stored on the filesystem in
``"$HOME"/.opengever/oneoffixx/oneoffixx.json``. ::

  {
    "client_secret": "<password-esque>",
    "client_id": "<UUIDv4>",
    "preshared_key": "<password-esque>"
  }

.. _authenticate: https://docs.oneoffixx.com/concepts/de/authorization/

This gets consumed in a three step process:

1) |find_credentials|_
2) |read_credentials|_
3) |validate_credentials|_

.. _find_credentials: https://github.com/4teamwork/opengever.core/blob/2019.2.1/opengever/oneoffixx/api_client.py#L86-L91
.. |find_credentials| replace:: Find the credentials file

.. _read_credentials: https://github.com/4teamwork/opengever.core/blob/2019.2.1/opengever/oneoffixx/api_client.py#L93-L107
.. |read_credentials| replace:: Parse the credentials file

.. _validate_credentials: https://github.com/4teamwork/opengever.core/blob/2019.2.1/opengever/oneoffixx/api_client.py#L204-L210
.. |validate_credentials| replace:: Validate the credentials file

As the process of consuming the file is gone through every time we need to
authenticate a user, the contents may be modified at runtime without incurring
any downtime.

Once we have processed the credentials, we fetch the SID of the current user
from AD and proceed to |acquire_grant|_ and |cache_grant|_ an impersonation
grant with a per user key in a per user per instance ``plone.memoize.ram`` time
invalidated cache. We |sign_grant_request|_ and |post_grant_request|_ it as
``application/x-www-form-urlencoded``.

.. _acquire_grant: https://github.com/4teamwork/opengever.core/blob/2019.2.1/opengever/oneoffixx/api_client.py#L195-L264
.. |acquire_grant| replace:: acquire

.. _cache_grant: https://github.com/4teamwork/opengever.core/blob/2019.2.1/opengever/oneoffixx/api_client.py#L15-L17
.. |cache_grant| replace:: cache

.. _sign_grant_request: https://github.com/4teamwork/opengever.core/blob/2019.2.1/opengever/oneoffixx/api_client.py#L229-L234
.. |sign_grant_request| replace:: sign the grant request

.. _post_grant_request: https://github.com/4teamwork/opengever.core/blob/2019.2.1/opengever/oneoffixx/api_client.py#L254-L260
.. |post_grant_request| replace:: post

GEVER Wizard
^^^^^^^^^^^^

The template selection form is implemented via a ``TableChoice`` field
depending on a ``Choice`` field. The ``Choice`` field allows the user to select
a template group to filter the list of templates by and the ``TableChoice``
field allows the user to select the template to use.

The default template group value of ``--NOVALUE--`` shows all templates. In
case the user has favorites defined, the default factory injects the favorites
group as the default choice, which unfortunately provides for some moderately
clunky UX, as the default from the factory only gets selected over AJAX after
the form rendering completes.

The ``TableChoice`` template selector also has an ``ftw.keywordwidget`` based
filter-as-you-type filter for quickly filtering the currently visible set of
templates. This field gets the focus per default.

Both the list of all templates and the list of template groups are implemented
as vocabularies built at form render time. The template listing vocabulary
first builds a list of all templates the Oneoffixx API client returns for the
current user, and then checks if we need to filter_ them by the chosen template
group: either by a normal group or by the favorites group.

.. _filter: https://github.com/4teamwork/opengever.core/blob/2019.2.1/opengever/oneoffixx/browser/form.py#L66-L94

The template groups vocabulary first grabs all the template groups from the
Oneoffixx API for the user and then grabs the list of favorites, if any, for
the current user, and injects_ those as an another template group.

.. _injects: https://github.com/4teamwork/opengever.core/blob/2019.2.1/opengever/oneoffixx/browser/form.py#L30-L41

All three fetches from the Oneoffixx backend are cached per user:

1) The list of template groups
2) The list of templates
3) The list of favorites

The user is also required to provide a name for the new document.

Upon passing form validation, a document creation command_ kicks in. It sets
all the required metadata into the object annotations of the freshly created
document and creates the document in the shadow_ state.

.. _command: https://github.com/4teamwork/opengever.core/blob/2019.2.1/opengever/oneoffixx/command.py
.. _shadow: https://github.com/4teamwork/opengever.core/blob/2019.2.1/opengever/document/document.py#L257-L275

It also sets up a redirection_ via the document redirector, which will fire up
after the user has been redirected to the newly created shadow document. The
URL being redirected to is an Office Connector URL, so it is passed onto the OS
and the user will stay on the document overview page. If Office Connector has
successfully registered as the default application handling an ``oc:`` URL, the
OS will pass the URL as a parameter to Office Connector.

.. _redirection: https://github.com/4teamwork/opengever.core/blob/2019.2.1/opengever/document/document.py#L381-L400

There is a fallback button on shadow documents to try again in case of
transient OS or Office Connector failures.

GEVER-side XML generation
^^^^^^^^^^^^^^^^^^^^^^^^^

A view_ to generate a |oneoffixx-instruction-xml|_ is registered_ for users
with ``cmf.ModifyPortalContent`` on all
``opengever.document.behaviors.IBaseDocument``. For documents not in a shadow
state, we return a ``404`` response with view level logic.

.. _view: https://github.com/4teamwork/opengever.core/blob/2019.2.1/opengever/oneoffixx/browser/connect_xml.py
.. _registered: https://github.com/4teamwork/opengever.core/blob/2019.2.1/opengever/oneoffixx/browser/configure.zcml#L20-L25

We generate a batch with one entry in it. This batch is instructed to keep its
XML file, create a result file on success and also create a result file on
error.

The singular batch entry is a ``OneOffixxConnect`` instruction. This
instruction takes the template ID and the language ID as arguments.

We add the DocProperties of the document as ``MetaData``. We also add the
DocProperties as a named ``CustomInterfaceConnector`` ``OneGovGEVER``. For
these to end up on the resulting document, the template would need to use them.
As far as we are aware of, the template editor does not support either.
Technically it should be possible to produce a template XML, which takes the
metadata, but we've not experimented with injecting this directly into the
backend as this'd not be a realistic use scenario.

The ``OneOffixxConnect`` instruction consists of a series of commands_,
executed in the order they are present in the XML.

.. _commands: https://docs.oneoffixx.com/docfunc/de/overview/

We always do the following:

* ``DefaultProcess``
   * ``Start: False``
* ``ConvertToDocument``
* ``SaveAs``
   * ``Overwrite: True``
   * ``CreateFolder: True``
   * ``AllowUpdateDocumentPart: False``
   * ``Filename: ''``
* ``InvokeProcess``
   * ``Name: 'OfficeConnector'``
   * ``Arguments: <oc-checkout-url>``

We want it to just save the document to disk and ping Office Connector back
with a callback when done. Office Connector modifies the XML with the desired
path and file name.

A UI wizard for filling in any missing values will pop up for the user before
the commands get executed.

Office Connector early cycle
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After the OS passes the URL to Office Connector, it proceeds to fetch the
Oneoffixx payload from the Plone site root by posting the document UUID to the
Oneoffixx payload endpoint_. This payload contains the instructions on how to
fetch the Oneoffixx Connect XML instructions for the document.

.. _endpoint: https://github.com/4teamwork/opengever.core/blob/2019.2.1/opengever/officeconnector/service.py#L261-L298

The XML instruction is fetched and an appropriate output path is inserted as a
``SaveAs`` argument and we 'execute' the XML file with ``os.startfile`` via an
URL like ``oneoffixx:connector=<path-to-xml>``. We also store the checkout URL
JWT in Office Connector and replace the JWT in the XML with a random hash so we
can piece it back together once the callback completes.

Oneoffixx
^^^^^^^^^

Oneoffixx flushes the file out onto the filesystem, produces a result XML file
for any post mortem debugging purposes and sends the callback back to Office
Connector.
