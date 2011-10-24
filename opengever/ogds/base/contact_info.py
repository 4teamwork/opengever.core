from Products.CMFCore.utils import getToolByName
from Products.ZCatalog.ZCatalog import ZCatalog
from Products.ZCatalog.interfaces import ICatalogBrain
from five import grok
from opengever.ogds.base import _
from opengever.ogds.base.interfaces import IContactInformation, IUser
from opengever.ogds.base.interfaces import ISyncStamp
from opengever.ogds.base.utils import brain_is_contact, get_client_id
from opengever.ogds.base.utils import create_session
from opengever.ogds.base.utils import get_current_client
from opengever.ogds.models.client import Client
from opengever.ogds.models.group import Group
from opengever.ogds.models.user import User
from plone.memoize import ram
from zope.app.component.hooks import getSite
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.i18n import translate
import logging
import types


logger = logging.getLogger('opengever.ogds.base')


def ogds_principal_cachekey(method, self, principal):
    """A chache_key including which is, explicit for the
    method, ogds_sync_stamp and principal."""


    return '%s.%s:%s:%s' % (
        self.__class__.__module__,
        self.__class__.__name__,
        getUtility(ISyncStamp).get_sync_stamp(),
        principal)


def ogds_user_client_cachekey(method, self, user, client):
    """A chache_key including which is, explicit for the
    method, ogds_sync_stamp and principal."""

    return '%s.%s:%s:%s:%s' % (
        self.__class__.__module__,
        self.__class__.__name__,
        getUtility(ISyncStamp).get_sync_stamp(),
        user,
        client)


def ogds_class_cachekey(method, self):
    """A cache key including the class' name.
    and the actual ogds sync stamp.
    """

    return '%s.%s:%s' % (
        self.__class__.__module__,
        self.__class__.__name__,
        getUtility(ISyncStamp).get_sync_stamp())


class UserDict(object):
    """A dictionary representing a user.
    """

    def __init__(self, **kw):
        self.__dict__.update(kw)


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

    :group: Groups is a sql reprensantation of a LDAP Group.
    """

    grok.provides(IContactInformation)

    # USERS
    def is_user(self, principal):
        """Returns true, if `principal` is a userid.
        """

        return principal and ':' not in principal

    @ram.cache(ogds_class_cachekey)
    def list_users(self):
        """A list of dicts.
        """
        session = create_session()
        userdata_keys = User.__table__.columns.keys()
        result = session.execute(User.__table__.select())
        return [UserDict(**dict(zip(userdata_keys, row))) for row in result]

    def list_assigned_users(self, client_id=None):
        """Lists all users assigned to a client.
        """
        if not client_id:
            client_id = get_client_id()

        if not client_id:
            logger.warn("can't list assigned users, without a client_id")
            return []

        session = create_session()
        users = session.query(Group).join(Client.users_group).filter(
            Client.client_id == client_id).first().users

        return users

    def list_group_users(self, groupid):
        """Return all users of a group"""

        if groupid:
            session = create_session()
            groups = session.query(Group).filter(
                Group.groupid == groupid).all()
            if len(groups) > 0:
                return groups[0].users
        return []

    def list_user_groups(self, userid):
        if userid:
            session = create_session()
            groups = session.query(User).filter(
                        User.userid == userid).first().group_users
            return groups
        return []

    def get_user(self, principal):
        """Returns the user with the userid `principal`.
        """

        if not self.is_user(principal):
            raise ValueError('principal %s is not a user' % str(principal))

        # if isinstance(principal, unicode):
        #     # Encode before using in an SQLAlchemy query
        #     principal = principal.encode('utf-8')

        users = self._users_query().filter_by(userid=principal).all()
        if len(users) == 0:
            return None
        elif len(users) > 1:
            raise ValueError('Found %i users with principal, %s ' % (
                    len(users), principal) + 'expected only one')
        else:
            return users[0]

    def is_user_in_inbox_group(self, userid=None, client_id=None):
        if not client_id:
            client_id = get_client_id()

        if not userid:
            member = getToolByName(
                getSite(), 'portal_membership').getAuthenticatedMember()
            userid = member.getId()

        if self.get_user(userid) in self.get_client_by_id(
                client_id).inbox_group.users:
            return True

        return False

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
            # usually foreign users may not have access to the contacts,
            # but we want to be able to print the name etc. in this case too.
            # So we need to use ZCatalog for ignoring the allowedRolesAndUsers
            # index.
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
                    len(clients), client_id) + 'expected only one')
        else:
            return clients[0]

    @ram.cache(ogds_principal_cachekey)
    def get_group_of_inbox(self, principal):
        """Returns the group principal of the inbox `principal`.
        """

        client = self.get_client_of_inbox(principal)

        if client == None:
            raise ValueError('Client not found for: %s' % principal)

        return client.inbox_group.groupid

    # CLIENTS
    def get_clients(self):
        """Returns a list of all enabled clients.
        """

        # If the current client is not enabled, we should not be able to
        # assign something to another client or interact in any way with
        # another client. This client is completely isolated.
        if not get_current_client().enabled:
            return []

        return self._clients_query().filter_by(enabled=True).order_by(
            Client.title).all()

    def get_client_by_id(self, client_id):
        """Returns a client identified by `client_id`.
        """
        clients = self._clients_query().filter_by(client_id=client_id,
                                                  enabled=True).all()
        # Depending on the collation, filter_by matches are
        # case-insensitive, which can potentially lead to
        # several clients being returned with their client_id
        # only differing in case.
        # In that case we only return the exact match, if there
        # is one, and log the incident.
        exact_matches = [c for c in clients if c.client_id == client_id]

        if len(clients) > 1:
            logger.warn('Found %i clients with client_id %s, ' % (
                    len(clients), client_id) + 'expected only one')

        return exact_matches and exact_matches[0] or None

    def get_assigned_clients(self, userid=None):
        """Returns all assigned clients (home clients).
        """

        if not userid:
            member = getToolByName(
                getSite(), 'portal_membership').getAuthenticatedMember()
            userid = member.getId()

        session = create_session()

        # select all clients with the user in the user group
        clients = session.query(Client).join(Client.users_group).join(
            Group.users).filter(User.userid == userid).all()

        return clients

    @ram.cache(ogds_user_client_cachekey)
    def _is_client_assigned(self, userid, client_id):
        session = create_session()

        # check if the specified user is in the user_group of the specified
        # client
        if session.query(Client).join(Client.users_group).join(
            Group.users).filter(User.userid == userid).filter(
                    Client.client_id == client_id).count() > 0:
                return True

        return False

    def is_client_assigned(self, userid=None, client_id=None):
        """Return True if the specified user is in the user_group
        of the specified client"""

        if not client_id:
            client_id = get_client_id()

        if not userid:
            member = getToolByName(
                getSite(), 'portal_membership').getAuthenticatedMember()
            userid = member.getId()

        return self._is_client_assigned(userid, client_id)

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
            # we need to instantly translate, because otherwise
            # stuff like the autocomplete widget will not work
            # properly.
            label = _(u'inbox_label',
                     default=u'Inbox: ${client}',
                     mapping=dict(client=client.title))

            return translate(label, context=getRequest())

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
        elif IUser.providedBy(principal) or isinstance(principal, UserDict):
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
            elif 'userid' in contact:
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
        elif IUser.providedBy(principal) or isinstance(principal, UserDict):
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
        elif IUser.providedBy(principal) or isinstance(principal, UserDict):
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

    @ram.cache(ogds_principal_cachekey)
    def get_profile_url(self, principal):
        """Returns the profile url of this `principal`.
        """
        if isinstance(principal, User):
            portal = getSite()
            return '/'.join((portal.portal_url(), '@@user-details',
                                 principal.userid))

        elif self.is_inbox(principal):
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
                    return portal_membership.getMemberById(
                        principal).getHomeUrl()
            return None

    @ram.cache(ogds_principal_cachekey)
    def render_link(self, principal):
        """Render a link to the `principal`
        """

        if not principal or principal == '':
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
