Introduction
============

The `opengever.ogds.base` package provides basic functionality for the global
opengever directory service.


Configuration
-------------

Each client is configured via the p.a.registry interface
`opengever.ogds.base.interfaces.IClientConfiguration`.

In the configuration the client_id have to be set. It should later corespond
with the client objects.


SQL-Configuration
-----------------

For enabling SQL we need to configure a SQLAlchemy connection and a named session.
The package `z3c.saconfig` allows to do that with simple ZCML entries. The
package `opengever.ogds.mysql` configures such a connection and a named session for
use in development environment, where no Oracle installation is available:

..
    <configure xmlns:db="http://namespaces.zope.org/db">
        <db:engine name="opengever.db" url="mysql://opengever:opengever@localhost/opengever?charset=utf8" />
        <db:session name="opengever" engine="opengever.db" />
    </configure>

`opengever.ogds.base` just tries to use the named session with the name
"opengever". It also possible to create sqlite memory stored databases for
testing purposes.


Clients
-------

For each client in the OGDS system we need to configure a client object,
which is stored with the SQL model `Client`.

A client object has currently following attributes:

:client_id: The ID of the client, which is used for referencing it. The client
    ID should not change when choosen once since we would have to update every place
    it occurs (catalog etc). It have to correspond with the `IClientConfiguration`
    `client_id` configuration.

:title: The title of the client which will be shown in the GUI for indicating on
    which client the user is.

:enabled: Possiblity to disable a client. It will not be selectable any more and
    the client cannot make authorisation on other clients anymore when doing internal
    requests.

:ip_address: IP-Address which the client will use to connect to other clients. This
    may be "127.0.0.1" when you are only using one machine, but it has to be the machine
    IP as soon as the client may connect to a client which is not on the same machine,
    since authentication and authorisation for internal requests validates the IP.

:site_url: The site URL is used for internal requests. Clients are able to do
    requests (e.g. list of dossiers) to another client. The site_url should not pass
    any proxy stuff since it may cause problems and is not necessary. The site_url should
    correspond with the ip_address, since the IP address will change when doing requests
    to other clients (such as localhost). The URL points to the Plone-Site.

:public_url: The public URL is used for user redirection. If a user needs to be
    redirected to another client this URL will be used as base. It should point to the
    Plone-Site from the user perspective and it may go through proxies and authentication
    machineries.

:group: The group is used for assigning users to a client. Every user which is member
    of this group is automatically assigned to this client. The user may be assigned to
    multiple clients.

:inbox_group: Tasks which are assigned to the Inbox of a client will be assigned to
    this group. This makes it easy to generate lists of tasks but it also is used for
    granting access to the inbox group for a specific task on a forign client which is
    assign to this inbox group.


Users
-----

A user is a person who is / was able to log into the system in tha past, present or
in the future. Tasks can be assigned to a user and it's expected that this user is
able to log in and work on his tasks. Users which do no longer have a valid login
can be disabled.

The users are imported from a LDAP from time to time with their relevant properties.
Users have following properties:

:userid: Userid which is used as primary key but also as login name and for managing
    the security of Plone. The userid is defined by the LDAP. It is not allowed to
    reuse a once used userid since the new user would succeed with the permissions and
    tasks of the old user - which would generate a security leak. Usually the userid
    consists of four characters, which are usually uppercase, but the system does not
    rely on this definition.

:active: Indicates if the user is currently active or not. When setting the activity
    to `False` the user will not be selectable e.g. as responsible of a task but it's
    name and other properties can still be queried.

:firstname: First name of the user.

:lastname: Last name of the user.

:directorate: Fulltext title of the directorate.

:directorate_abbr: The abbreviation of the directorate.

:department: Fulltext ttitle of the department.

:department_abbr: The abbreviation of the department.

:email: Users primary e-mail address.

:email2: Users secundary e-mail address.

:url: URL to a website of the user.

:phone_office: Users office phone number.

:phone_fax: Users fax number.

:phone_mobile: Users mobile phone number.

:salutation: Users salutation.

:description: Users description.

:address1: Users primary address line.

:address2: Users secundary address line.

:zip_code: ZIP-Code of the address.

:city: City of the address.

:country: Country of the address.


Contacts
--------

Contacts are persons which do not participate actively and do not have a possiblity
to log into the system. Contacts are third party persons which may take a role in
a business case but are passive. They are stored directly in the client and are
only on this client available for selection in some certain fields / types. See
the package `opengever.contact` for further details.


Committee
---------

Committees are not yet implemented. They are a heap of users and contacts on a
informationaly basis. They are not relevant for security issues.


Group
-----

Groups are provided by the LDAP and my contain users as members. Currently they
are only used in certain use cases such as for assigning users to clients or
for determining inbox users.


Contact information system
--------------------------

The contact information system provides information about users, contacts and
inboxes. There is a global utility which provides various informations:

    >>> from zope.component import getUtility
    >>> from opengever.ogds.base.interfaces import IContactInformation
    >>> info = getUtility(IContactInformation)

With the contact information utility you are able to get various informations. Below
is a subset of the most important features.

The ID of users, contacts and inboxes are generalized with the term `principal`.

Checking the type of a principal:

    >>> info.is_user('hugo.boss')
    True
    >>> info.is_contact('contact:peter-muster')
    True
    >>> info.is_inbox('inbox:client1')
    True

Other methods:

    >>> info.get_user('hugo.boss')
    <User hugo.boss>
    >>> info.get_contact('contact:peter-muster')
    <Brain ...>

Getting lists of users (which returns plone user objects):

    >>> info.list_users()

Listing all users assigned to the current client:

    >>> info.list_assigned_users()

List contacts:

    >>> info.list_contacts()

List inboxes:

    >>> info.list_inboxes()

List of clients:

    >>> info.get_clients()
    >>> info.get_client_by_id('client3')
    >>> info.get_assigned_clients('hugo.boss')

Markup methods:

    >>> info.describe('hugo.boss', with_email=True)
    "Boss Hugo (hugo.boss@local.ch)"
    >>> info.get_email('hugo.boss')
    hugo.boss@local.ch
    >>> info.get_email2('hugo.boss')
    hugo.boss@private.ch
    >>> info.render_link('hugo.boss')
    "<a href="...">Boss Hugo</a>'


Vocabularies
------------

There are various vocabularies used for many different forms / types in opengever.
The OGDS-relevant vocabularies are storied in `opengever.ogds.base.vocabularies`.

:opengever.ogds.base.UsersVocabulary: Contains all users listed in OGDS.

:opengever.ogds.base.UsersAndInboxesVocabulary: Contains the inbox and the
    users assigned to a specific client. The client is defined in the
    request either with key "client" or with key
    "form.widgets.responsible_client".

:opengever.ogds.base.AssignedUsersVocabulary: Contains all users assigned
    to the current client.

:opengever.ogds.base.ContactsVocabulary: Contains all local contacts.

:opengever.ogds.base.ContactsAndUsersVocabulary: Contains all local contacts
    and all users listed in OGDS but also each inbox group for each active
    client (the vocabulary should be renamed and include "inbox" in the name).

:opengever.ogds.base.EmailContactsAndUsersVocabulary: Contains all
    users listed in OGDS and local contacts for every e-mail address they have.

:opengever.ogds.base.ClientsVocabulary: Contains all enabled clients (including
    the current one).

:opengever.ogds.base.AssignedClientsVocabulary: Contains all assigned
    clients (=home clients) of the current user, including the current client.

:opengever.ogds.base.OtherAssignedClientsVocabulary: Contains all assigned
    clients (=home clients) of the current user except the current client.

:opengever.ogds.base.HomeDossiersVocabulary: Contains all open dossiers on the
    users home client. Key is the path of dossier relative to its plone site on
    the remote client. The client is defined in the request either with key
    "client" or with key "form.widgets.client".

:opengever.ogds.base.DocumentInSelectedDossierVocabulary: Contains all
    documents within the previously selected dossier. The client is defined in
    the request either with key "client" or with key "form.widgets.client", the
    dossier is defined either with the key "dossier_path" or with the key
    "form.widgets.source_dossier" containing the absolute path to the dossier
    on the remote client.


Transporting system
-------------------

The OGDS transporting system allows to transport objects from one client to another.
It is possible to pull a object from another client but it's also possible to push
a object to another client.

The transporting system is implemented in `opengever.ogds.base.transport`.

Main Usage:

    >>> from zope.component import getUtility
    >>> from opengever.ogds.base.interfaces import ITransporter
    >>> transporter = getUtility(ITransporter)

Pushing a object to another client:

    >>> transporter.transport_to(obj, target_cid, container_path)

:obj: The object which should be copied to the target client.

:target_cid: The target client id which has to correspond with the client
    configuration.

:container_path: The path of the target container, relative to the target plone
    site root (that means it does not begin with a slash).

Pulling objects from foreign clients:

    >>> transporter.transport_from(container, source_cid, path)

:container: Container object on this client.

:source_cid: Client ID of the source client.

:path: Path to the object which should be copied to this client. The path is
    relative to the Plone site root on the remote client.

There are various adapters for creating object, extracting and setting object
attributes etc. which can be easely customized on per type basis.
