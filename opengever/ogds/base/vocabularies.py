from collective.elephantvocabulary import wrap_vocabulary
from five import grok
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.interfaces import IClientCommunicator
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.interfaces import ISyncStamp
from opengever.ogds.base.utils import get_client_id
from opengever.ogds.base.utils import get_current_client
from opengever.ogds.base.utils import get_current_org_unit
from opengever.ogds.base.utils import ogds_service
from opengever.ogds.base.vocabulary import ContactsVocabulary
from plone.memoize import ram
from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite, setSite
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.schema.interfaces import IVocabularyFactory
import AccessControl


def voc_cachekey(method, self):
    """A cache key for vocabularies which are implemented as grok utilities
       and which do not depend on other parameters."""

    return '%s:%s' % (getattr(self, 'grokcore.component.directive.name'),
                          getUtility(ISyncStamp).get_sync_stamp())


def client_voc_cachekey(method, self):
    """A cache key depending on the vocabulary name and the current client id.
    """
    return '%s:%s:%s' % (getattr(self, 'grokcore.component.directive.name'),
                      get_client_id(), getUtility(ISyncStamp).get_sync_stamp())


def reqclient_voc_cachekey(method, self):
    """A cache key depending on the vocabulary name and the client id in the
       request.
    """
    return '%s:%s:%s' % (
        getattr(self, 'grokcore.component.directive.name'),
        self.get_client(),
        getUtility(ISyncStamp).get_sync_stamp())


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

    @ram.cache(voc_cachekey)
    @generator_to_list
    def key_value_provider(self):
        # Reset hidden_terms every time cache key changed
        self.hidden_terms = []

        for user in ogds_service().all_users():
            if not user.active:
                self.hidden_terms.append(user.userid)
            yield (user.userid, user.label())


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

    @ram.cache(reqclient_voc_cachekey)
    @generator_to_list
    def key_value_provider(self):
        # Reset hidden_terms every time cache key changed
        self.hidden_terms = []

        client_id = self.get_client() or ''
        unit = ogds_service().fetch_org_unit(client_id)
        if unit:
            for user in unit.assigned_users():
                yield (user.userid, user.label())

            # client inbox
            yield (unit.inbox().id(),
                   Actor.inbox(unit.inbox().id(), unit).get_label())

            # add the inactive users to the vocabulary
            # and mark them as hidden terms
            for user in ogds_service().inactive_users():
                if user.userid not in self.hidden_terms:
                    self.hidden_terms.append(user.userid)
                    yield (user.userid, user.label())

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


class AllUsersAndInboxesVocabularyFactory(grok.GlobalUtility):
    """Vocabulary of all users and all inbexes, but client unspecific.
    The client is added as prefix to each user.
    Users assigned to multiple clients are once per client in the vocabulary.
    """

    grok.provides(IVocabularyFactory)
    grok.name('opengever.ogds.base.AllUsersAndInboxesVocabulary')

    hidden_terms = []

    def __call__(self, context):
        self.context = context
        vocab = wrap_vocabulary(
            ContactsVocabulary.create_with_provider(
                self.key_value_provider))(context)
        vocab.hidden_terms = self.hidden_terms
        return vocab

    @ram.cache(voc_cachekey)
    @generator_to_list
    def key_value_provider(self):
        # Reset hidden_terms every time cache key changed
        self.hidden_terms = []

        for unit in ogds_service().all_org_units():
            for user in unit.assigned_users():
                yield (u'{}:{}'.format(unit.id(), user.userid),
                       unit.prefix_label(user.label()))

            # add the inactive users to the vocabulary
            # and mark them as hidden terms
            for user in ogds_service().inactive_users():
                if user.userid not in self.hidden_terms:
                    self.hidden_terms.append(user.userid)
                    yield (user.userid, user.label())

            # client inbox
            inbox_actor = Actor.inbox(unit.inbox().id(), unit)
            yield (u'{}:{}'.format(unit.id(), unit.inbox().id()),
                   inbox_actor.get_label())


class InboxesVocabularyFactory(UsersAndInboxesVocabularyFactory):
    """Similar like the UsersAndInboxesVocabularyFactory, but return just the
    inboxes if is not the actual client. The client is defined in the request
    either with key "client" or with key "form.widgets.responsible_client"."""

    grok.provides(IVocabularyFactory)
    grok.name('opengever.ogds.base.InboxesVocabulary')

    hidden_terms = []

    def __call__(self, context):
        self.context = context
        vocab = wrap_vocabulary(
            ContactsVocabulary.create_with_provider(
                self.key_value_provider))(context)
        vocab.hidden_terms = self.hidden_terms
        return vocab

    @ram.cache(reqclient_voc_cachekey)
    @generator_to_list
    def key_value_provider(self):
        # Reset hidden_terms every time cache key changed
        self.hidden_terms = []

        info = getUtility(IContactInformation)

        selected_unit = ogds_service().fetch_org_unit(self.get_client())
        if selected_unit:
            # check if it the current client is selected then add all users
            if selected_unit.id() == get_current_org_unit().id():
                for user in selected_unit.assigned_users():
                    if not user.active:
                        self.hidden_terms.append(user.userid)
                    yield (user.userid, user.label())

            # add all inactive users to the hidden terms
            for user in ogds_service().inactive_users():
                if user.userid not in self.hidden_terms:
                    self.hidden_terms.append(user.userid)

            # client inbox
            inbox_actor = Actor.inbox(selected_unit.inbox().id(),
                                      org_unit=selected_unit)
            yield (selected_unit.inbox().id(), inbox_actor.get_label())


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

    @ram.cache(client_voc_cachekey)
    @generator_to_list
    def key_value_provider(self):
        # Reset hidden_terms every time cache key changed
        self.hidden_terms = []

        unit = get_current_org_unit()
        for user in unit.assigned_users():
            if not user.active:
                self.hidden_terms.append(user.userid)
            yield (user.userid, user.label())

        # add the inactive users to the vocabulary and marked as hidden terms
        for user in ogds_service().inactive_users():
            if user.userid not in self.hidden_terms:
                self.hidden_terms.append(user.userid)
                yield (user.userid, user.label())


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
                   Actor.contact(contact.contactid,
                                 contact=contact).get_label())

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
        # Reset hidden_terms every time cache key changed
        self.hidden_terms = []

        info = getUtility(IContactInformation)
        items, hidden_terms = self._get_users()
        # copy lists to prevent cache modification
        items = items[:]
        self.hidden_terms = hidden_terms[:]
        for contact in info.list_contacts():
            actor = Actor.contact(contact.contactid, contact=contact)
            items.append((contact.contactid, actor.get_label()))

        return items

    @ram.cache(voc_cachekey)
    def _get_users(self):
        info = getUtility(IContactInformation)
        items = []
        hidden_terms = []

        # users
        for user in ogds_service().all_users():
            if not user.active:
                hidden_terms.append(user.userid)
            items.append((user.userid, user.label()))

        # inboxes
        for unit in ogds_service().all_org_units():
            items.append((
                unit.inbox().id(),
                Actor.inbox(unit.inbox().id(), unit).get_label()))

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
        key = mail-address:id eg. hugo@boss.ch:hugo.boss
        value = Fullname [address], eg. Hugo Boss [hugo@boss.ch]
        """

        for item in self._user_data():
            yield item

    @ram.cache(voc_cachekey)
    def _user_data(self):
        """Create a list containing all user data which can be memoized.
        key = mail-address:id eg. hugo@boss.ch:hugo.boss
        value for users = Fullname (userid, address), eg. Hugo Boss (hugo.boss, hugo@boss.ch)
        value for contacts Fullname (id, address), eg. James Bond (007@bond.ch)
        """
        user_data = []

        # users
        for user in ogds_service().all_users():
            if user.email:
                key = '{}:{}'.format(user.email, user.userid)
                value = '{} ({}, {})'.format(user.fullname(),
                                             user.userid, user.email)
                user_data.append((key, value))

            if user.email2:
                key = '{}:{}'.format(user.email2, user.userid)
                value = '{} ({}, {})'.format(user.fullname(),
                                             user.userid, user.email2)
                user_data.append((key, value))

        # contacts
        info = getUtility(IContactInformation)
        for contact in info.list_contacts():
            if contact.email:
                user_data.append(
                    ('{}:{}'.format(contact.email, contact.id),
                     '{} ({})'.format(contact.Title, contact.email)))

            if contact.email2:
                user_data.append(
                    ('{}:{}'.format(contact.email2, contact.id),
                     '{} ({})'.format(contact.Title, contact.email2)))

        return user_data


class OrgUnitsVocabularyFactory(grok.GlobalUtility):
    """Vocabulary of all enabled clients (including the current one).
    """

    grok.provides(IVocabularyFactory)
    grok.name('opengever.ogds.base.OrgUnitsVocabularyFactory')

    def __call__(self, context):
        self.context = context
        vocab = ContactsVocabulary.create_with_provider(
            self.key_value_provider)
        return vocab

    def key_value_provider(self):
        service = ogds_service()
        for unit in ogds_service().all_org_units():
            yield (unit.id(), unit.label())


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

        client_id = request.get(
            'client', request.get('form.widgets.client'))
        if type(client_id) in (list, tuple, set):
            client_id = client_id[0]
        client = info.get_client_by_id(client_id)

        if client and not info.is_client_assigned(client_id=client_id):
            raise ValueError(
                'Expected %s to be a assigned client of the current user.' %
                    client_id)

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

        # get client
        client_id = request.get(
            'client', request.get('form.widgets.client'))
        if type(client_id) in (list, tuple, set):
            client_id = client_id[0]

        if not info.is_client_assigned(client_id=client_id):
            raise ValueError(
                'Expected %s to be a assigned client of the current user.' %
                client_id)

        # get dossier path
        dossier_path = request.get(
            'dossier_path', request.get('form.widgets.source_dossier'))
        if type(dossier_path) in (list, tuple, set):
            dossier_path = dossier_path[0]

        if dossier_path:
            cid = client_id
            if cid:
                for doc in comm.get_documents_of_dossier(cid, dossier_path):
                    key = doc.get('path')
                    value = doc.get('title')
                    yield (key, value)
