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
from opengever.ogds.models.group import groups_users
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

    return '%s.%s.%s:%s' % (
        self.__class__.__module__,
        self.__class__.__name__,
        method.__name__,
        getUtility(ISyncStamp).get_sync_stamp())


def ogds_class_language_cachekey(method, self):
    """A cache key including the class' name, the preffered language
    and the actual ogds sync stamp.
    """

    return '%s.%s.%s:%s:%s' % (
        self.__class__.__module__,
        self.__class__.__name__,
        method.__name__,
        getToolByName(getSite(), 'portal_languages').getPreferredLanguage()[0],
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

    def list_inactive_users(self):
        session = create_session()
        users = session.query(User).filter_by(active=False)
        return users

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
            group = session.query(Group).get(groupid)
            if group:
                return group.users
        return []

    def list_user_groups(self, userid):
        if userid:
            session = create_session()
            groups = session.query(User).get(userid).group_users
            return groups
        return []

    def get_user(self, userid):
        """Returns the user with the userid `principal`.
        """

        if not self.is_user(userid):
            raise ValueError('principal %s is not a userid' % str(userid))

        return self._users_query().get(userid)

    def is_user_in_inbox_group(self, userid=None, client_id=None):
        if not client_id:
            client_id = get_client_id()

        if not userid:
            member = getToolByName(
                getSite(), 'portal_membership').getAuthenticatedMember()
            userid = member.getId()

        client = self.get_client_by_id(client_id)
        if client:
            return self.is_group_member(client.inbox_group_id, userid)
        else:
            return False

    def is_group_member(self, groupid, userid):
        in_group = create_session().query(Group.groupid).join(groups_users).filter(
            Group.groupid == groupid,
            groups_users.columns.userid == userid).first()

        return in_group != None

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

        return self._clients_query().get(client_id)

    @ram.cache(ogds_principal_cachekey)
    def get_group_of_inbox(self, principal):
        """Returns the group principal of the inbox `principal`.
        """

        client = self.get_client_of_inbox(principal)

        if client is None:
            raise ValueError('Client not found for: %s' % principal)

        return client.inbox_group

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
        client = self._clients_query().filter_by(enabled=True,
                                                 client_id=client_id).first()
        return client

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

    def is_one_client_setup(self):
        """Return True if only one client is available"""

        clients = self.get_clients()

        return len(clients) == 1

    # general principal methods
    def describe(self, principal, with_email=False, with_email2=False,
                 with_principal=True):
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
                return '%s (%s)' % (name, contact.email2)
            elif with_principal and contact.email:
                return '%s (%s)' % (name, contact.email)
            else:
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

            infos = []
            if with_principal:
                infos.append(user.userid)

            if with_email and user.email:
                infos.append(user.email)

            elif with_email2 and user.email2:
                infos.append(user.email2)

            if infos:
                return '%s (%s)' % (name, ', '.join(infos))
            else:
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

            infos = []
            if with_principal:
                infos.append(principal)

            if with_email and email:
                infos.append(email)

            if infos:
                return '%s (%s)' % (name, ', '.join(infos))
            else:
                return name

        else:
            raise ValueError('Unknown principal type: %s' % str(principal))

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

    @ram.cache(ogds_class_language_cachekey)
    def get_user_sort_dict(self):
        """Returns a dict presenting userid and the fullname,
        that allows correct sorting on the fullname.
        Including also every client inbox.
        """

        session = create_session()
        query = session.query(User.userid, User.lastname, User.firstname)
        query = query.order_by(User.lastname, User.firstname)
        ids = query.all()

        sort_dict = {}
        for userid, lastname, firstname in ids:
            sort_dict[userid] = u'%s %s' % (lastname, firstname)

        #includes every client inbox
        active_clients = self._clients_query().filter_by(enabled=True)
        for client in active_clients:
            principal = u'inbox:%s' % client.client_id
            sort_dict[principal] = translate(self.describe(principal))
        return sort_dict

    def get_user_contact_sort_dict(self):
        sort_dict = self.get_user_sort_dict()
        for contact in self.list_contacts():
            sort_dict['contact:%s' % (contact.id)] = u'%s %s' % (
                contact.lastname, contact.firstname)
        return sort_dict

    # internal methods
    def _users_query(self):
        session = create_session()
        return session.query(User)

    def _clients_query(self):
        session = create_session()
        return session.query(Client)
