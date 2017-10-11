from opengever.testing import IntegrationTestCase
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory


class TestCommitteeVocabularies(IntegrationTestCase):

    def test_committeee_vocabulary_list_all_committees(self):
        self.login(self.committee_responsible)
        factory = getUtility(IVocabularyFactory,
                             name='opengever.meeting.CommitteeVocabulary')
        self.assertItemsEqual(
            [self.empty_committee.load_model(),
             self.committee.load_model()],
            [term.value for term in factory(context=None)])

    def test_active_committeee_vocabulary_list_only_active_committees(self):
        self.login(self.committee_responsible)
        factory = getUtility(IVocabularyFactory,
                             name='opengever.meeting.ActiveCommitteeVocabulary')
        self.assertItemsEqual(
            [self.empty_committee.load_model(),
             self.committee.load_model()],
            [term.value for term in factory(context=None)])

        self.empty_committee.load_model().deactivate()
        self.assertItemsEqual(
            [self.committee.load_model()],
            [term.value for term in factory(context=None)])
