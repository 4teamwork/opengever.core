from Products.statusmessages.interfaces import IStatusMessage
from five import grok
from opengever.ogds.base.interfaces import IClientCommunicator
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.vocabulary import ContactsVocabulary
from zope.app.component.hooks import getSite
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary


class UsersVocabularyFactory(grok.GlobalUtility):
    """ Vocabulary of all users with a valid login.
    """

    grok.provides(IVocabularyFactory)
    grok.name('opengever.ogds.base.UsersVocabulary')

    def __call__(self, context):
        return ContactsVocabulary.create_with_provider(self.key_value_provider)

    def key_value_provider(self):
        info = getUtility(IContactInformation)
        for user in info.list_users():
            yield (user.userid,
                   info.describe(user.userid))


class UsersAndInboxesVocabularyFactory(grok.GlobalUtility):
    """Vocabulary of all users and all inboxes of enabled clients.
    """

    grok.provides(IVocabularyFactory)
    grok.name('opengever.ogds.base.UsersAndInboxesVocabulary')

    def __call__(self, context):
        return ContactsVocabulary.create_with_provider(self.key_value_provider)

    def key_value_provider(self):
        info = getUtility(IContactInformation)
        # all users
        for user in info.list_users():
            yield (user.userid,
                   info.describe(user.userid))
        # all inboxes
        for key, label in info.list_inboxes():
            yield (key, label)


class AssignedUsersVocabularyFactory(grok.GlobalUtility):
    """Vocabulary of all users assigned to the current client.
    """

    grok.provides(IVocabularyFactory)
    grok.name('opengever.ogds.base.AssignedUsersVocabulary')

    def __call__(self, context):
        return ContactsVocabulary.create_with_provider(self.key_value_provider)

    def key_value_provider(self):
        info = getUtility(IContactInformation)
        for user in info.list_assigned_users():
            yield (user.userid,
                   info.describe(user.userid))


class ContactsVocabularyFactory(grok.GlobalUtility):
    """Vocabulary of contacts.
    """

    grok.provides(IVocabularyFactory)
    grok.name('opengever.ogds.base.ContactsVocabulary')

    def __call__(self, context):
        return ContactsVocabulary.create_with_provider(self.key_value_provider)

    def key_value_provider(self):
        info = getUtility(IContactInformation)
        for contact in info.list_contacts():
            yield (contact.getPrincipal(),
                   info.describe(contact.getPrincipal()))


class ContactsAndUsersVocabularyFactory(grok.GlobalUtility):
    """Vocabulary of contacts and users.
    """

    grok.provides(IVocabularyFactory)
    grok.name('opengever.ogds.base.ContactsAndUsersVocabulary')

    def __call__(self, context):
        return ContactsVocabulary.create_with_provider(self.key_value_provider)

    def key_value_provider(self):
        info = getUtility(IContactInformation)
        # users
        for user in info.list_users():
            yield (user.userid,
                   info.describe(user.userid))
        for contact in info.list_contacts():
            yield (contact.getPrincipal(),
                   info.describe(contact.getPrincipal()))


class EmailContactsAndUsersVocabularyFactory(grok.GlobalUtility):
    """Vocabulary containing all users and contacts with each e-mail
    address they have.
    """

    grok.provides(IVocabularyFactory)
    grok.name('opengever.ogds.base.EmailContactsAndUsersVocabulary')

    def __call__(self, context):
        vocab = ContactsVocabulary.create_with_provider(
            self.key_value_provider)
        return vocab

    def key_value_provider(self):
        """yield the items

        key = mail-address
        value = Fullname [address], eg. Hugo Boss [hugo@boss.ch]
        """

        info = getUtility(IContactInformation)
        ids = [user.userid for user in self.list_users()]
        ids.extend([contact.getPrincipal() for contact
                    in self.list_contacts()])

        for userid in ids:
            yield(info.get_email(userid),
                  info.describe(userid, with_email=True))
            if info.get_email2(userid) != None:
                yield(info.get_email2(userid),
                      info.describe(userid, with_email2=True))


class HomeDossiersVocabularyFactory(grok.GlobalUtility):
    """Vocabulary of all open dossiers on users home client.
    """

    grok.provides(IVocabularyFactory)
    grok.name('opengever.ogds.base.HomeDossiersVocabulary')

    def __call__(self, context):
        if isinstance(context, dict):
            # collective.z3cform.wizard support
            context = getSite()
        terms = []

        info = getUtility(IContactInformation)
        comm = getUtility(IClientCommunicator)
        home_clients = info.get_assigned_clients()

        # XXX: implement multiple clients support with additional
        # wizard view
        IStatusMessage(context.REQUEST).addStatusMessage(
            'DEBUG NOTICE: No multiple clients support implemented yet!',
            type='warning')
        client = home_clients[0]

        if client:
            for dossier in comm.get_open_dossiers(client.client_id):
                key = dossier['path']
                value = '%s: %s' % (dossier['reference_number'],
                                    dossier['title'])
                terms.append(SimpleVocabulary.createTerm(key,
                                                         key,
                                                         value))
        # XXX: remove sorting as soon as autocomplete widget is used
        terms.sort(lambda a,b:cmp(a.title, b.title))
        return SimpleVocabulary(terms)


class DocumentInSelectedDossierVocabularyFactory(grok.GlobalUtility):
    """ Provides a vocabulary containing all documents within the previously
    selected dossier. Expects the context to be a dict containing the path
    to the dossier under the key 'source_dossier'
    see collective.z3cform.wizard for more details
    """
    grok.provides(IVocabularyFactory)
    grok.name('opengever.ogds.base.DocumentInSelectedDossierVocabulary')
    dossier_request_key = 'dossier_path'

    def __call__(self, context):
        dossier_path = context.REQUEST.get(self.dossier_request_key, None)
        terms = []

        info = getUtility(IContactInformation)
        comm = getUtility(IClientCommunicator)
        home_clients = info.get_assigned_clients()

        # XXX: implement multiple clients support with additional
        # wizard view
        IStatusMessage(context.REQUEST).addStatusMessage(
            'DEBUG NOTICE: No multiple clients support implemented yet!',
            type='warning')
        client = home_clients[0]

        if dossier_path:
            cid = client.client_id
            if cid:
                for doc in comm.get_documents_of_dossier(cid, dossier_path):
                    key = doc.get('path')
                    value = doc.get('title')
                    terms.append(SimpleVocabulary.createTerm(key, key, value))
        # XXX: remove sorting as soon as autocomplete widget is used
        terms.sort(lambda a,b:cmp(a.title, b.title))
        return SimpleVocabulary(terms)
