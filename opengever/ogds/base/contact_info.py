from five import grok
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.interfaces import ISyncStamp
from opengever.ogds.base.utils import create_session
from opengever.ogds.models.user import User
from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite
from zope.component import getUtility
import logging

logger = logging.getLogger('opengever.ogds.base')


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
