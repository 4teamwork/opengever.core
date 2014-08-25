from five import grok
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.interfaces import ISyncStamp
from opengever.ogds.base.utils import create_session
from opengever.ogds.base.utils import get_current_org_unit
from opengever.ogds.base.utils import ogds_service
from opengever.ogds.models.client import Client
from opengever.ogds.models.group import Group
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
