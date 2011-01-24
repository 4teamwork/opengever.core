from Products.CMFCore.utils import getToolByName
from Products.ZCatalog.ZCatalog import ZCatalog
from Products.ZCatalog.interfaces import ICatalogBrain
from five import grok
from opengever.ogds.base import _
from opengever.ogds.base.interfaces import IContactInformation, IUser
from opengever.ogds.base.model.client import Client
from opengever.ogds.base.model.user import User
from opengever.ogds.base.utils import brain_is_contact
from opengever.ogds.base.utils import create_session, get_current_client
from zope.app.component.hooks import getSite
import types


class ContactInformation(grok.GlobalUtility):
    """The principal information utility provides useful functions for
    building vocabularies with users, contacts, in-boxes groups and
    committees.

    Terminology:

    :client: A client is a installation of opengever, which may be connected
    to other similar installations (clients).

    :user: A user is a person who can log into the system and is available
    for any client. Users are stored in the SQL database using the sql-alchemy
    model provided by this package.

    :contact: A contact is a person who does not have acces to the system and
    do not participate directly, but he may be involved in the topic of a
    dossier or parts of it.

    :committee: A committee is a heap of users and contacts. They are not
    relevant for the security.

    :group: Groups are defined in the LDAP and used with PAS.
    """

    grok.provides(IContactInformation)

    # USERS

    def is_user(self, principal):
        """Returns true, if `principal` is a userid.
        """

        return principal and ':' not in principal

    def list_users(self):
        """Returns a sql-alchemy query set containing all users.
        """

        return self._users_query().all()

    def list_assigned_users(self, client_id=None):
        """Lists all users assigned to a client.
        """

        if not client_id:
            client = get_current_client()
        else:
            client = self.get_client_by_id(client_id)

        if not client:
            raise ValueError('Could not find client "%s"' % str(client_id))

        groupid = client.group
        acl_users = getToolByName(getSite(), 'acl_users')
        group = acl_users.getGroupById(groupid.encode('utf-8'))

        ids = group.getGroupMemberIds()
        for user in self._users_query().filter(User.userid.in_(ids)):
            yield user

    def get_user(self, principal):
        """Returns the user with the userid `principal`.
        """

        if not self.is_user(principal):
            raise ValueError('principal %s is not a user' % str(principal))

        users = self._users_query().filter_by(userid=principal).all()
        if len(users) == 0:
            return None
        elif len(users) > 1:
            raise ValueError('Found %i users with principal, %s ' % (
                    len(users), principal) + 'expected only one' )
        else:
            return users[0]


    # CONTACTS

    def is_contact(self, principal):
        """Return true, if `principal` is a contact.
        """

        return principal and principal.startswith('contact:')

    def list_contacts(self):
        """Returns a catalog result set of contact brains.
        """
        catalog = getToolByName(getSite(), 'portal_catalog')
        query = {'portal_type': 'opengever.contact.contact'}
        # make catalog query without checking security (allowedRolesAndUsers)
        # since the contacts are not visible for foreign users but should be
        # in the vocabulary anyway...
        brains = ZCatalog.searchResults(catalog, **query)
        return brains

    def get_contact(self, principal, check_permissions=False):
        """Returns the contact object of this principal.
        """

        if not self.is_contact(principal):
            raise ValueError('Principal %s is not a contact' % str(principal))

        catalog = getToolByName(getSite(), 'portal_catalog')
        query = {'portal_type': 'opengever.contact.contact',
                 'contactid': principal}

        if not check_permissions:
            # usually foreign users may not have access to the contacts, but we
            # want to be able to print the name etc. in this case too. So we need
            # to use ZCatalog for ignoring the allowedRolesAndUsers index.
            contacts = ZCatalog.searchResults(catalog, **query)
        else:
            contacts = catalog.searchResults(**query)

        if len(contacts) == 0:
            return None
        elif len(contacts) > 1:
            raise ValueError('Found %i contacts with principal %s' % (
                    len(contacts), principal))
        else:
            return contacts[0]


    # INBOXES

    def is_inbox(self, principal):
        """Returns true, if `principal` is a inbox.
        """

        return principal and principal.startswith('inbox:')

    def list_inboxes(self):
        """Returns a set of inboxes of all enabled clients.
        """

        clients = self._clients_query()
        active_clients = clients.filter_by(enabled=True)
        for client in active_clients:
            principal = u'inbox:%s' % client.client_id
            yield (principal,
                   self.describe(principal))

    def get_client_of_inbox(self, principal):
        """Returns the client object of the `principal`.
        """

        if not self.is_inbox(principal):
            raise ValueError('Principal %s is not a inbox' % (str(principal)))

        client_id = principal.split(':', 1)[1]

        clients = self._clients_query().filter_by(client_id=client_id).all()
        if len(clients) == 0:
            return None
        elif len(clients) > 1:
            raise ValueError('Found %i clients with client_id, %s ' % (
                    len(clients), client_id) + 'expected only one' )
        else:
            return clients[0]

    def get_group_of_inbox(self, principal):
        """Returns the group principal of the inbox `principal`.
        """

        client = self.get_client_of_inbox(principal)

        if client == None:
            raise ValueError('Client not found for: %s' % principal)

        return client.inbox_group


    # CLIENTS

    def get_clients(self):
        """Returns a list of all enabled clients.
        """

        return self._clients_query().filter_by(enabled=True).all()

    def get_client_by_id(self, client_id):
        """Returns a client identified by `client_id`.
        """

        clients = self._clients_query().filter_by(client_id=client_id,
                                                  enabled=True).all()
        if len(clients) == 0:
            return None
        elif len(clients) > 1:
            raise ValueError('Found %i clients with client_id, %s ' % (
                    len(clients), client_id) + 'expected only one' )
        else:
            return clients[0]

    def get_assigned_clients(self, userid=None):
        """Returns all assigned clients (home clients).
        """

        acl_users = getToolByName(getSite(), 'acl_users')

        if not userid:
            member = getToolByName(
                getSite(),
                'portal_membership').getAuthenticatedMember()
            userid = member.getId()

        clients = self.get_clients()
        for client in clients:
            groupid = client.group.encode('utf-8')
            group = acl_users.getGroupById(groupid)
            if group and userid in group.getMemberIds():
                yield client


    # general principal methods

    def describe(self, principal, with_email=False, with_email2=False):
        """Represent a user / contact / inbox / ... as string. This usually
        returns the fullname or another label / title.
        `principal` could also be a user object or a contact brain.
        """

        if not principal:
            return ''

        is_string = isinstance(principal, types.StringTypes)
        brain = None
        contact = None
        user = None

        # is principal a brain?
        if not is_string and ICatalogBrain.providedBy(principal):
            brain = principal

        # ok, lets check what we have...

        # string inbox
        if is_string and self.is_inbox(principal):
            # just do it
            client = self.get_client_of_inbox(principal)
            # some times the site is the z3c validaton, so get
            # the real site a little bit hacky
            site = getToolByName(getSite(), 'portal_url').getPortalObject()
            # we need to instantly translate, because otherwise
            # stuff like the autocomplete widget will not work
            # properly.
            label = _(u'inbox_label',
                     default=u'Inbox: ${client}',
                     mapping=dict(client=client.title))
            return site.translate(label)

        # string contact
        elif is_string and self.is_contact(principal):
            contact = self.get_contact(principal)

        # string user
        elif is_string and self.is_user(principal):
            user = self.get_user(principal)

        # contact brain
        elif brain and brain_is_contact(brain):
            contact = brain
            principal = contact.contactid

        # user object
        elif IUser.providedBy(principal):
            user = principal
            principal = user.userid

        # ok, now lookup the stuff
        if contact:
            if not contact:
                return principal
            elif contact.lastname and contact.firstname:
                name = ' '.join((contact.lastname, contact.firstname))
            elif contact.lastname:
                name = contact.lastname
            elif contact.firstname:
                name = contact.firstname
            elif contact.has_key('userid'):
                name = contact.userid
            else:
                name = contact.id

            if with_email2 and contact.email2:
                name = '%s (%s)' % (name, contact.email2)
            elif contact.email:
                name = '%s (%s)' % (name, contact.email)
            return name

        elif user:
            if user.lastname and user.firstname:
                name = ' '.join((user.lastname, user.firstname))
            elif user.lastname:
                name = user.lastname
            elif user.firstname:
                name = user.firstname
            else:
                name = user.userid

            if with_email and user.email:
                name = '%s (%s, %s)' % (name, user.userid, user.email)
            elif with_email2 and user.email2:
                name = '%s (%s, %s)' % (name, user.userid, user.email2)
            else:
                name = '%s (%s)' % (name, user.userid)
            return name

        elif is_string:
            # fallback for acl_users
            portal = getSite()
            portal_membership = getToolByName(portal, 'portal_membership')
            member = portal_membership.getMemberById(principal)
            if not member:
                if isinstance(principal, str):
                    return principal.decode('utf-8')
                else:
                    return principal
            name = member.getProperty('fullname', principal)
            email = member.getProperty('email', None)
            if with_email and email:
                name = '%s (%s, %s)' % (name, principal, email)
            else:
                name = '%s (%s)' % (name, principal)
            return name

        else:
            raise ValueError('Unknown principal type: %s' % str(principal))

    def get_email(self, principal):
        """Returns the email address of a `principal`.
        """
        # inbox does not have a email
        if isinstance(principal, types.StringTypes) and \
                self.is_inbox(principal):
            return None

        # principal may be a contact brain
        elif ICatalogBrain.providedBy(principal) and \
                brain_is_contact(principal):
            return principal.email

        # principal may be a user object
        elif IUser.providedBy(principal):
            return principal.email

        # principal may ba a string contact principal
        elif self.is_contact(principal):
            return self.get_contact(principal).email

        # principal may be a string user principal
        elif self.is_user(principal):
            if not self.get_user(principal):
                return None
            return self.get_user(principal).email

        else:
            raise ValueError('Unknown principal type: %s' %
                             str(principal))

    def get_email2(self, principal):
        """Returns the second email address of a `principal`.
        """

        # inbox does not have a email
        if isinstance(principal, types.StringTypes) and \
                self.is_inbox(principal):
            return None

        # principal may be a contact brain
        elif ICatalogBrain.providedBy(principal) and \
                brain_is_contact(principal):
            return principal.email2

        # principal may be a user object
        elif IUser.providedBy(principal):
            return principal.email2

        # principal may ba a string contact principal
        elif self.is_contact(principal):
            return self.get_contact(principal).email2

        # principal may be a string user principal
        elif self.is_user(principal):
            return self.get_user(principal).email2

        else:
            raise ValueError('Unknown principal type: %s' %
                             str(principal))

    def get_profile_url(self, principal):
        """Returns the profile url of this `principal`.
        """

        if self.is_inbox(principal):
            return None

        elif self.is_contact(principal):
            contact = self.get_contact(principal, check_permissions=True)
            if contact:
                return contact.getURL()
            else:
                return None

        elif self.is_user(principal):
            portal = getSite()
            user = self.get_user(principal)
            if user:
                return '/'.join((portal.portal_url(), '@@user-details',
                                 user.userid))
            else:
                # fallback with acl_users folder
                portal_membership = getToolByName(portal, 'portal_membership')
                member = portal_membership.getMemberById(principal)
                if member:
                    return portal_membership.getMemberById(principal).getHomeUrl()
            return None

    def render_link(self, principal):
        """Render a link to the `principal`
        """

        if not principal or len(principal) == 0:
            return None

        url = self.get_profile_url(principal)
        if not url:
            return self.describe(principal)

        return '<a href="%s">%s</a>' % (
            url,
            self.describe(principal))

    # internal methods

    def _users_query(self):
        session = create_session()
        return session.query(User)

    def _clients_query(self):
        session = create_session()
        return session.query(Client)
