from five import grok
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.model.client import Client
from opengever.ogds.base.model.user import User
from opengever.ogds.base.utils import create_session, get_current_client
from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName


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

    def list_assigned_users(self):
        """Lists all users assigned to this client.
        """

        groupid = get_current_client().group
        acl_users = getToolByName(getSite(), 'acl_users')
        group = acl_users.getGroupById(groupid.encode('utf-8'))

        for member in group.getAllGroupMembers():
            yield self.get_user(member.getId())

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

    def list_contacts(self):
        # XXX NotImplemented
        raise NotImplemented

    def get_contact(self, principal):
        """Returns the contact object of this principal.
        """

        if not self.is_contact(principal):
            raise ValueError('Principal %s is not a contact' % str(principal))

        # XXX NotImplemented
        raise NotImplemented


    # INBOXES

    def is_inbox(self, principal):
        """Returns true, if `principal` is a inbox.
        """

        return principal.startswith('inbox:')

    def list_inboxes(self):
        """Returns a set of inboxes.
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


    # general principal methods

    def describe(self, principal, with_email=False):
        """Represent a user / contact / inbox / ... as string. This usually
        returns the fullname or another label / title.
        """

        if self.is_inbox(principal):
            client = self.get_client_of_inbox(principal)
            return u'Inbox: %s' % client.title

        elif self.is_contact(principal):
            contact = self.get_contact(principal)
            name = ' '.join((contact.lastname, contact.firstname))
            if with_email and contact.email:
                name = '%s (%s)' % (name, contact.email)
            return name

        elif self.is_user(principal):
            user = self.get_user(principal)
            name = ' '.join((user.lastname, user.firstname))
            if with_email and user.email:
                name = '%s (%s)' % (name, user.email)
            return name

        else:
            raise ValueError('Unknown principal type: %s' % str(principal))

    def get_profile_url(self, principal):
        """Returns the profile url of this `principal`.
        """

        if self.is_inbox(principal):
            client = self.get_client_of_inbox(principal)
            return '/'.join((client.public_url, 'inbox'))

        elif self.is_contact(principal):
            contact = self.get_contact(principal)
            return contact.absolute_url()

        elif self.is_user(principal):
            user = self.get_user(principal)
            portal = getSite()
            return '/'.join(portal.portal_url(), '@@user_details',
                            user.userid)

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
