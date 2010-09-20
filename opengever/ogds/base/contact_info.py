from opengever.ogds.base.utils import create_session
from opengever.ogds.base.model.user import User
from five import grok
from opengever.ogds.base.interfaces import IContactInformation


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

    def list_users(self):
        """Returns a sql-alchemy query set containing all users.
        """

        session = create_session()
        return session.query(User)
