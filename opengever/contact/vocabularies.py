from opengever.contact.models import Contact
from opengever.contact.models import Organization
from opengever.contact.models import Person
from zope.interface import implementer
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.interfaces import IVocabularyTokenized
from zope.schema.vocabulary import SimpleTerm


@implementer(IVocabularyTokenized)
class ContactsVocabulary(object):
    """A vocabulary of all contacts (all persons and organizations).

    Providing a search method, which allows using the vocabulary in an
    autocomplete field.
    """

    @property
    def queries(self):
        return [Person.query, Organization.query]

    def __contains__(self, value):
        """Return whether the value is available in this source
        """
        return bool(Contact.query.get(value))

    def createTerm(self, obj):
        return SimpleTerm(value=obj.contact_id, title=obj.get_title())

    def getTerm(self, value):
        contact = Contact.query.get(value)
        if not contact:
            raise LookupError

        return self.createTerm(contact)

    def getTermByToken(self, token):
        return self.getTerm(token)

    def search(self, query_string):
        text_filters = query_string.split()
        for query in self.queries:
            query = query.by_searchable_text(text_filters=text_filters)
            for obj in query.all():
                yield self.createTerm(obj)


class ContactsVocabularyFactory(object):
    """A vocabulary factory for the ContactsVocabulary.
    """

    implements(IVocabularyFactory)

    def __call__(self, context):
        return ContactsVocabulary()
