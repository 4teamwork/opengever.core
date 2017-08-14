from opengever.ogds.base.utils import ogds_service
from opengever.ogds.base.vocabulary import ContactsVocabulary
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory


@implementer(IVocabularyFactory)
class OrgUnitsVocabularyFactory(object):
    """Vocabulary of all enabled clients (including the current one).
    """

    def __call__(self, context):
        self.context = context
        vocab = ContactsVocabulary.create_with_provider(
            self.key_value_provider)
        return vocab

    def key_value_provider(self):
        for unit in ogds_service().all_org_units():
            yield (unit.id(), unit.label())


@implementer(IVocabularyFactory)
class AssignedClientsVocabularyFactory(object):
    """Vocabulary of all assigned clients (=home clients) of the
    current user, including the current client.
    """

    def __call__(self, context):
        self.context = context
        vocab = ContactsVocabulary.create_with_provider(
            self.key_value_provider)
        return vocab

    def key_value_provider(self):
        for org_unit in ogds_service().assigned_org_units():
            yield (org_unit.id(), org_unit.label())


@implementer(IVocabularyFactory)
class OtherAssignedClientsVocabularyFactory(object):
    """Vocabulary of all assigned clients (=home clients) of the
    current user. The current client is not included!
    """

    def __call__(self, context):
        self.context = context
        vocab = ContactsVocabulary.create_with_provider(
            self.key_value_provider)
        return vocab

    def key_value_provider(self):
        for org_unit in ogds_service().assigned_org_units(omit_current=True):
            yield (org_unit.id(), org_unit.label())
