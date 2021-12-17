from opengever.kub.client import KuBClient
from opengever.ogds.base.actor import ActorLookup
from opengever.ogds.models.exceptions import RecordNotFound
from opengever.ogds.models.service import ogds_service
from z3c.formwidget.query.interfaces import IQuerySource
from zope.interface import implementer
from zope.interface import implements
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm


@implementer(IQuerySource)
class KuBContactsSource(object):
    """This source supports KuB contacts and OGDS Users.
    """

    def __init__(self, context):
        self.context = context
        self.terms = []
        self.client = KuBClient()

    @staticmethod
    def _kub_term(item):
        return SimpleTerm(value=item['typedId'], title=item['text'])

    @staticmethod
    def _ogds_user_term(user):
        return SimpleTerm(value=user,
                          token=user.userid,
                          title=user.label(with_principal=True))

    def getTermByToken(self, token):
        if not token:
            raise LookupError()

        if ActorLookup(token).is_kub_contact():
            item = self.client.get_by_id(token)
            return self._kub_term(item)

        # it's an ogds user
        try:
            user = ogds_service().find_user(token)
        except RecordNotFound:
            raise LookupError()
        return self._ogds_user_term(user)

    def search(self, query_string):
        items = self.client.query(query_string)
        self.terms = [self._kub_term(item) for item in items]

        text_filters = query_string.split()
        for ogds_user in ogds_service().filter_users(text_filters):
            self.terms.append(self._ogds_user_term(ogds_user))

        return self.terms


@implementer(IContextSourceBinder)
class KuBContactsSourceBinder(object):

    implements(IVocabularyFactory)

    def __call__(self, context):
        return KuBContactsSource(context)
