from opengever.ogds.base.utils import create_session
from opengever.ogds.base.model.user import User
from opengever.ogds.base.model.client import Client
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

    # USERS

    def is_user(self, principal):
        """Returns true, if `principal` is a userid.
        """

        return ':' not in principal

    def list_users(self):
        """Returns a sql-alchemy query set containing all users.
        """

        return self._users_query().all()

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

        return principal.startswith('contact:')

    # INBOXES

    def is_inbox(self, principal):
        """Returns true, if `principal` is a inbox.
        """

        return principal.startswith('inbox:')

    def list_inboxes(self):
        clients = self._clients_query()
        active_clients = clients.filter_by(enabled=True)
        for client in active_clients:
            yield (u'inbox:%s' % client.client_id,
                   u'Inbox: %s' % client.title)

    # internal methods

    def _users_query(self):
        session = create_session()
        return session.query(User)

    def _clients_query(self):
        session = create_session()
        return session.query(Client)
