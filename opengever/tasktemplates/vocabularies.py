from five import grok
from zope.globalrequest import getRequest
from opengever.ogds.base.vocabularies import ClientsVocabularyFactory
from opengever.ogds.base.vocabularies import ContactsAndUsersVocabularyFactory
from opengever.ogds.base.vocabularies import UsersAndInboxesVocabularyFactory
from opengever.tasktemplates import _
from zope.i18n import translate
from zope.schema.interfaces import IVocabularyFactory


def interactive_users(context):
    yield ('responsible',
           translate(_(u'interactive_user_responsible',
                       default=u'Responsible'),
                     context=getRequest()))
    yield ('current_user',
           translate(_(u'interactive_user_current_user',
                       default=u'Current user'),
                     context=getRequest()))


class IssuerVocabularyFactory(ContactsAndUsersVocabularyFactory):
    """Vocabulary of all users. Thats the
    opengever.ogds.base.ContactsAndUsersVocabulary
    extended by the interactive users.
    """

    grok.provides(IVocabularyFactory)
    grok.name('opengever.tasktemplates.IssuerVocabulary')

    def key_value_provider(self):
        for e in interactive_users(self.context):
            yield e
        for e in ContactsAndUsersVocabularyFactory.key_value_provider(self):
            yield e


class ResponsibleClientVocabularyFactory(ClientsVocabularyFactory):
    """Vocabulary of all clients extend by the "interactive users"
    client.
    """

    grok.provides(IVocabularyFactory)
    grok.name('opengever.tasktemplates.ResponsibleClientVocabulary')

    def key_value_provider(self):
        yield ('interactive_users',
               translate(_(u'client_interactive_users',
                           default=u'Interactive users'),
                         context=getRequest()))
        for e in ClientsVocabularyFactory.key_value_provider(self):
            yield e


class ResponsibleVocabularyFactory(UsersAndInboxesVocabularyFactory):
    """Vocabulary with the default users and clients extended with the
    interactive users.
    """

    grok.provides(IVocabularyFactory)
    grok.name('opengever.tasktemplates.ResponsibleVocabulary')

    def key_value_provider(self):
        request = self.context.REQUEST
        items = list(self._get_items())
        keys = dict(items).keys()

        if '/@@edit' in request.getURL():
            current_value = self.context.responsible
            if current_value and current_value not in keys:
                self.hidden_terms.append(current_value)
                items.append((current_value, current_value))

        return items

    def _get_items(self):
        if self.get_client() == u'interactive_users':
            for e in interactive_users(self.context):
                yield e
        else:
            for e in UsersAndInboxesVocabularyFactory.key_value_provider(self):
                yield e
