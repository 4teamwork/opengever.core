from opengever.kub import is_kub_feature_enabled
from opengever.kub.sources import KuBContactsSourceBinder
from opengever.ogds.base.sources import UsersContactsInboxesSourceBinder
from zope.interface import implementer
from zope.interface import implements
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IVocabularyFactory


@implementer(IContextSourceBinder)
class PloneSqlOrKubContactSourceBinder(object):
    """A vocabulary factory for currently active contact type.
    """

    implements(IVocabularyFactory)

    def __init__(self, only_active=False):
        self.only_active = only_active

    def __call__(self, context):
        if is_kub_feature_enabled():
            return KuBContactsSourceBinder(only_active=self.only_active)(context)

        return UsersContactsInboxesSourceBinder()(context)
