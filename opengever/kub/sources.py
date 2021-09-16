from opengever.kub.client import KuBClient
from z3c.formwidget.query.interfaces import IQuerySource
from zope.interface import implementer
from zope.interface import implements
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm


@implementer(IQuerySource)
class KuBContactsSource(object):

    def __init__(self, context):
        self.context = context
        self.terms = []
        self.client = KuBClient()

    def getTermByToken(self, token):
        if not token:
            raise LookupError

        item = self.client.get_by_id(token)
        return SimpleTerm(value=item['id'], title=item['fullName'])

    def search(self, query_string):
        items = self.client.query_contacts(query_string)
        self.terms = [
            SimpleTerm(value=item['id'], title=item['fullName'])
            for item in items]

        return self.terms


@implementer(IContextSourceBinder)
class KuBContactsSourceBinder(object):

    implements(IVocabularyFactory)

    def __call__(self, context):
        return KuBContactsSource(context)
