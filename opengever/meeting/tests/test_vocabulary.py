from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
import transaction


class TestCommitteeVocabularies(FunctionalTestCase):

    def setUp(self):
        super(TestCommitteeVocabularies, self).setUp()
        container = create(Builder('committee_container'))
        self.committee_a = create(Builder('committee')
                             .within(container)
                             .titled(u'Gemeinderat'))
        self.committee_b = create(Builder('committee')
                             .within(container)
                             .titled(u'Wasserkommission'))

        model = self.committee_b.load_model()
        model.workflow.execute_transition(
            self.committee_b, model, 'active-inactive')
        transaction.commit()

    def test_committeee_vocabulary_list_all_committees(self):
        factory = getUtility(IVocabularyFactory,
                             name='opengever.meeting.CommitteeVocabulary')
        vocabulary = factory(context=None)
        self.assertTermKeys(
            [self.committee_a.load_model(), self.committee_b.load_model()],
            vocabulary)

    def test_active_committeee_vocabulary_list_only_active_committees(self):
        factory = getUtility(IVocabularyFactory,
                             name='opengever.meeting.ActiveCommitteeVocabulary')
        vocabulary = factory(context=None)
        self.assertTermKeys(
            [self.committee_a.load_model()], vocabulary)
