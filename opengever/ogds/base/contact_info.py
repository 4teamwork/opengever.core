from five import grok
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.interfaces import ISyncStamp
from opengever.ogds.base.utils import create_session
from opengever.ogds.base.utils import get_current_org_unit
from opengever.ogds.base.utils import ogds_service
from opengever.ogds.models.client import Client
from opengever.ogds.models.group import Group
from opengever.ogds.models.group import groups_users
from opengever.ogds.models.user import User
from plone.memoize import ram
from Products.CMFCore.utils import getToolByName
from Products.ZCatalog.ZCatalog import ZCatalog
from zope.app.component.hooks import getSite
from zope.component import getUtility
import logging
import warnings


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

    def get_client_of_inbox(self, principal):
        """Returns the client object of the `principal`.
        """
        if not self.is_inbox(principal):
            raise ValueError('Principal %s is not a inbox' % (str(principal)))

        client_id = principal.split(':', 1)[1]

        return self._clients_query().get(client_id)

    @ram.cache(ogds_principal_cachekey)
    def get_groupid_of_inbox(self, principal):
        """Returns the groupid of the inbox `principal`.
        """

        client = self.get_client_of_inbox(principal)

        if client is None:
            raise ValueError('Client not found for: %s' % principal)

        return client.inbox_group.groupid

    # CLIENTS
    def get_clients(self):
        """Returns a list of all enabled clients.
        """

        # If the current client is not enabled, we should not be able to
        # assign something to another client or interact in any way with
        # another client. This client is completely isolated.
        warnings.warn(
            "This function is deprecated. Use ogds_service()"
            ".get_current_admin_unit()/get_current_org_unit() instead.",
            DeprecationWarning)

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
            client_id = get_current_org_unit().id()

        if not userid:
            member = getToolByName(
                getSite(), 'portal_membership').getAuthenticatedMember()
            userid = member.getId()

        return self._is_client_assigned(userid, client_id)

    def is_one_client_setup(self):
        """Return True if only one client is available"""

        clients = self.get_clients()

        return len(clients) == 1

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
            user = ogds_service().fetch_user(principal)
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

        #includes every org-unit-inbox
        for unit in ogds_service().all_org_units():
            inbox_id = unit.inbox().id()
            sort_dict[inbox_id] = Actor.lookup(inbox_id).get_label()
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
