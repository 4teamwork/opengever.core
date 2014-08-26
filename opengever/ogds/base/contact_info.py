from five import grok
from opengever.contact.service import ContactService
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.interfaces import ISyncStamp
from opengever.ogds.base.utils import create_session
from opengever.ogds.base.utils import ogds_service
from opengever.ogds.models.user import User
from plone.memoize import ram
from Products.CMFCore.utils import getToolByName
from Products.ZCatalog.ZCatalog import ZCatalog
from zope.app.component.hooks import getSite
from zope.component import getUtility
import logging

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
