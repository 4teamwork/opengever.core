from five import grok
from opengever.contact.models import Contact
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class SQLSimpleVocabulary(SimpleVocabulary):

    def search(self, query_string):
        """search method for `z3c.formwidget.autocomplete` support. Returns
        all matching contacts.
        """

        if isinstance(query_string, str):
            query_string = query_string.decode('utf8')
        query = query_string.lower().split(' ')

        for term in self:
            if self._compare(query, term.title):
                yield term

    def _compare(self, query, value):
        if not value:
            return False

        for word in query:
            if len(word) > 0 and word not in value.lower():
                return False
        return True


class ContactsAndUsersVocabularyFactory(grok.GlobalUtility):
    """Vocabulary of contacts, users and the inbox of each client.
    """

    grok.provides(IVocabularyFactory)
    grok.name('opengever.contact.ContactsVocabulary')

    def __call__(self, context):
        terms = []
        for contact in Contact.query.all():
            terms.append(SimpleTerm(
                value=contact.contact_id, title=contact.get_title()))

        return SQLSimpleVocabulary(terms)
