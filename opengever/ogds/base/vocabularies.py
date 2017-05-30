from five import grok
from opengever.ogds.base.utils import ogds_service
from opengever.ogds.base.vocabulary import ContactsVocabulary
from zope.schema.interfaces import IVocabularyFactory


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
        key = orgunit id
        value = orgunit label
        """
        for org_unit in ogds_service().assigned_org_units():
            yield (org_unit.id(), org_unit.label())


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
        """
        key = org_unit id
        value = org_unit title
        """

        for org_unit in ogds_service().assigned_org_units(omit_current=True):
            yield (org_unit.id(), org_unit.label())
