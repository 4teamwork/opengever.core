"""
Provides access to the ftw.directoryservice installed on the OGDS side (which
has a opengever.octopus.cortex installed).
"""

from five import grok
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.vocabulary import ContactsVocabulary
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory


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
