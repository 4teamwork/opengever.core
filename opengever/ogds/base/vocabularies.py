from Products.CMFCore.utils import getToolByName
from collective.elephantvocabulary import wrap_vocabulary
from five import grok
from opengever.ogds.base import caching
from opengever.ogds.base.interfaces import IClientCommunicator
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.utils import get_current_client, get_client_id
from opengever.ogds.base.vocabulary import ContactsVocabulary
from plone.memoize import volatile
from zope.app.component.hooks import getSite, setSite
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.schema.interfaces import IVocabularyFactory
import AccessControl


def generator_to_list(func):
    """Casts a generator object into a tuple. This decorator
    is necessary when memoizing methods which return generator objects.
    """
    def caster(*args, **kwargs):
        return list(func(*args, **kwargs))
    return caster


class UsersVocabularyFactory(grok.GlobalUtility):
    """ Vocabulary of all users with a valid login.
    """

    grok.provides(IVocabularyFactory)
    grok.name('opengever.ogds.base.UsersVocabulary')

    hidden_terms = []

    def __call__(self, context):
        self.context = context
        vocab = wrap_vocabulary(
            ContactsVocabulary.create_with_provider(
                self.key_value_provider))(context)
        vocab.hidden_terms = self.hidden_terms
        return vocab

    @volatile.cache(lambda method, self: True)
    @generator_to_list
    def key_value_provider(self):
        info = getUtility(IContactInformation)
        for user in info.list_users():
            if not user.active:
                self.hidden_terms.append(user.userid)
            yield (user.userid,
                   info.describe(user))


class UsersAndInboxesVocabularyFactory(grok.GlobalUtility):
    """Vocabulary of all users and all inboxes of a specific client. The client
    is defined in the request either with key "client" or with key
    "form.widgets.responsible_client".
    """

    grok.provides(IVocabularyFactory)
    grok.name('opengever.ogds.base.UsersAndInboxesVocabulary')

    hidden_terms = []

    def __call__(self, context):
        self.context = context
        vocab = wrap_vocabulary(
            ContactsVocabulary.create_with_provider(
                self.key_value_provider))(context)
        vocab.hidden_terms = self.hidden_terms
        return vocab

    @volatile.cache(lambda method, self: self.get_client())
    @generator_to_list
    def key_value_provider(self):
        client_id = self.get_client()
        info = getUtility(IContactInformation)
        if client_id and info.get_client_by_id(client_id):
            # all users
            for user in info.list_assigned_users(client_id=client_id):
                if not user.active:
                    self.hidden_terms.append(user.userid)
                yield (user.userid,
                       info.describe(user))
            # client inbox
            principal = u'inbox:%s' % client_id
            yield (principal, info.describe(principal))

    def get_client(self):
        """Tries to get the client from the request. If no client is found None
        is returned.
        """

        request = getRequest()
        client_id = request.get('client',
                                request.get('form.widgets.responsible_client',
                                            getattr(self.context,
                                                    'responsible_client',
                                                    None)))

        if not client_id:
            return None
        elif type(client_id) in (list, tuple, set):
            return client_id[0]
        else:
            return client_id


class AssignedUsersVocabularyFactory(grok.GlobalUtility):
    """Vocabulary of all users assigned to the current client.
    """

    grok.provides(IVocabularyFactory)
    grok.name('opengever.ogds.base.AssignedUsersVocabulary')

    hidden_terms = []

    def __call__(self, context):
        self.context = context
        vocab = wrap_vocabulary(
            ContactsVocabulary.create_with_provider(
                self.key_value_provider))(context)
        vocab.hidden_terms = self.hidden_terms
        return vocab

    @volatile.cache(caching.client_cache_key)
    @generator_to_list
    def key_value_provider(self):
        info = getUtility(IContactInformation)
        for user in info.list_assigned_users():
            if not user.active:
                self.hidden_terms.append(user.userid)
            yield (user.userid,
                   info.describe(user))


class ContactsVocabularyFactory(grok.GlobalUtility):
    """Vocabulary of contacts.
    """

    grok.provides(IVocabularyFactory)
    grok.name('opengever.ogds.base.ContactsVocabulary')

    def __call__(self, context):
        self.context = context
        return ContactsVocabulary.create_with_provider(self.key_value_provider)

    def key_value_provider(self):
        info = getUtility(IContactInformation)
        for contact in info.list_contacts():
            yield (contact.contactid,
                   info.describe(contact))


# TODO: should be renamed to something like
# ContactsUsersAndInboxesVocabularyFactory
class ContactsAndUsersVocabularyFactory(grok.GlobalUtility):
    """Vocabulary of contacts, users and the inbox of each client.
    """

    grok.provides(IVocabularyFactory)
    grok.name('opengever.ogds.base.ContactsAndUsersVocabulary')

    hidden_terms = []

    def __call__(self, context):
        self.context = context
        vocab = wrap_vocabulary(
            ContactsVocabulary.create_with_provider(
                self.key_value_provider))(context)
        vocab.hidden_terms = self.hidden_terms
        return vocab

    def key_value_provider(self):
        info = getUtility(IContactInformation)
        items, hidden_terms = self._get_users()
        items = items[:]
        self.hidden_terms = hidden_terms[:]
        for contact in info.list_contacts():
            items.append((contact.contactid,
                          info.describe(contact)))
        return items

    @volatile.cache(lambda method, self: True)
    def _get_users(self):
        info = getUtility(IContactInformation)
        items = []
        hidden_terms = []

        for user in info.list_users():
            if not user.active:
                hidden_terms.append(user.userid)
            items.append((user.userid,
                          info.describe(user)))

        # add also the client inboxes
        for client in info.get_clients():
            principal = u'inbox:%s' % client.client_id
            items.append((principal, info.describe(principal)))

        return (items, hidden_terms)


class EmailContactsAndUsersVocabularyFactory(grok.GlobalUtility):
    """Vocabulary containing all users and contacts with each e-mail
    address they have.
    """

    grok.provides(IVocabularyFactory)
    grok.name('opengever.ogds.base.EmailContactsAndUsersVocabulary')

    hidden_terms = []

    def __call__(self, context):
        self.context = context
        vocab = wrap_vocabulary(
            ContactsVocabulary.create_with_provider(
                self.key_value_provider))(context)
        vocab.hidden_terms = self.hidden_terms
        return vocab

    def key_value_provider(self):
        """yield the items

        key = mail-address
        value = Fullname [address], eg. Hugo Boss [hugo@boss.ch]
        """

        info = getUtility(IContactInformation)
        ids = [(user, user.active) for user in info.list_users()]
        ids.extend([(contact, True) for contact
                    in info.list_contacts()])

        for contact_or_user, active in ids:
            email = info.get_email(contact_or_user)
            if email != None:
                if not active:
                    self.hidden_terms.append(email)
                yield(email,
                      info.describe(contact_or_user,
                                    with_email=True))

                email2 = info.get_email2(contact_or_user)
                if email2 != None:
                    if not active:
                        self.hidden_terms.append(email2)
                    yield(email2,
                          info.describe(contact_or_user,
                                        with_email2=True))


class ClientsVocabularyFactory(grok.GlobalUtility):
    """Vocabulary of all enabled clients (including the current one).
    """

    grok.provides(IVocabularyFactory)
    grok.name('opengever.ogds.base.ClientsVocabulary')

    def __call__(self, context):
        self.context = context
        vocab = ContactsVocabulary.create_with_provider(
            self.key_value_provider)
        return vocab

    def key_value_provider(self):
        """yield the items

        key = client id
        value = client title
        """

        info = getUtility(IContactInformation)

        for client in info.get_clients():
            yield (client.client_id,
                   client.title)


class AssignedClientsVocabularyFactory(grok.GlobalUtility):
    """Vocabulary of all assigned clients (=home clients) of the
    current user, including the current client.
    """

    grok.provides(IVocabularyFactory)
    grok.name('opengever.ogds.base.AssignedClientsVocabulary')

    def __call__(self, context):
        self.context = context
        vocab = ContactsVocabulary.create_with_provider(
            self.key_value_provider)
        return vocab

    def key_value_provider(self):
        """yield the items

        key = client id
        value = client title
        """

        info = getUtility(IContactInformation)

        for client in info.get_assigned_clients():
            yield (client.client_id,
                   client.title)


class OtherAssignedClientsVocabularyFactory(grok.GlobalUtility):
    """Vocabulary of all assigned clients (=home clients) of the
    current user. The current client is not included!
    """

    grok.provides(IVocabularyFactory)
    grok.name('opengever.ogds.base.OtherAssignedClientsVocabulary')

    def __call__(self, context):
        self.context = context
        vocab = ContactsVocabulary.create_with_provider(
            self.key_value_provider)
        return vocab

    def key_value_provider(self):
        """yield the items

        key = client id
        value = client title
        """

        info = getUtility(IContactInformation)
        current_client_id = get_current_client().client_id

        for client in info.get_assigned_clients():
            if current_client_id != client.client_id:
                yield (client.client_id,
                       client.title)



class HomeDossiersVocabularyFactory(grok.GlobalUtility):
    """Vocabulary of all open dossiers on users home client.
    Key is the path of dossier relative to its plone site on the remote client.
    """

    grok.provides(IVocabularyFactory)
    grok.name('opengever.ogds.base.HomeDossiersVocabulary')

    def __call__(self, context):
        self.context = context
        vocab = ContactsVocabulary.create_with_provider(
            self.key_value_provider)
        return vocab

    def key_value_provider(self):
        """yield home dossiers
        key: relative path on home client
        value: "%(reference_number): %(title)"
        """

        # if we are not logged in we are in the traversal and should not
        # do anything...
        user = AccessControl.getSecurityManager().getUser()
        if user == AccessControl.SpecialUsers.nobody:
            return

        request = getRequest()

        info = getUtility(IContactInformation)
        comm = getUtility(IClientCommunicator)
        home_clients = tuple(info.get_assigned_clients())

        client_id = request.get(
            'client', request.get('form.widgets.client'))
        if type(client_id) in (list, tuple, set):
            client_id = client_id[0]
        client = info.get_client_by_id(client_id)

        if client and client not in home_clients:
            raise ValueError('Expected %s to be a ' % client_id + \
                                 'assigned client of the current user.')

        elif client:
            # kss validation overrides getSite() hook with a bad object
            # but we need getSite to work properly, so we fix it.
            site = getSite()
            if site.__class__.__name__ == 'Z3CFormValidation':
                fixed_site = getToolByName(self.context,
                                           'portal_url').getPortalObject()
                setSite(fixed_site)
                dossiers = comm.get_open_dossiers(client.client_id)
                setSite(site)
            else:
                dossiers = comm.get_open_dossiers(client.client_id)

            for dossier in dossiers:
                yield (dossier['path'],
                       '%s: %s' % (dossier['reference_number'],
                                   dossier['title']))


class DocumentInSelectedDossierVocabularyFactory(grok.GlobalUtility):
    """ Provides a vocabulary containing all documents within the previously
    selected dossier. Expects the context to be a dict containing the path
    to the dossier under the key 'source_dossier'
    """
    grok.provides(IVocabularyFactory)
    grok.name('opengever.ogds.base.DocumentInSelectedDossierVocabulary')

    def __call__(self, context):
        self.context = context
        vocab = ContactsVocabulary.create_with_provider(
            self.key_value_provider)
        return vocab

    def key_value_provider(self):
        request = getRequest()

        # if we are not logged in we are in the traversal and should not
        # do anything...
        user = AccessControl.getSecurityManager().getUser()
        if user == AccessControl.SpecialUsers.nobody:
            return


        info = getUtility(IContactInformation)
        comm = getUtility(IClientCommunicator)
        home_clients = info.get_assigned_clients()

        # get client
        client_id = request.get(
            'client', request.get('form.widgets.client'))
        if type(client_id) in (list, tuple, set):
            client_id = client_id[0]
        client = info.get_client_by_id(client_id)

        if client not in home_clients:
            raise ValueError('Expected %s to be a ' % client_id + \
                                 'assigned client of the current user.')

        # get dossier path
        dossier_path = request.get(
            'dossier_path', request.get('form.widgets.source_dossier'))
        if type(dossier_path) in (list, tuple, set):
            dossier_path = dossier_path[0]

        if dossier_path:
            cid = client.client_id
            if cid:
                for doc in comm.get_documents_of_dossier(cid, dossier_path):
                    key = doc.get('path')
                    value = doc.get('title')
                    yield (key, value)
