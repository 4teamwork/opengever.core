from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import IntegrationTestCase
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.utils import safe_unicode
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


class TestProposalTemplatesVocabulary(IntegrationTestCase):

    def test_contains_proposal_templates(self):
        self.login(self.regular_user)
        factory = getUtility(IVocabularyFactory,
                             name='opengever.meeting.ProposalTemplatesVocabulary')
        self.assertItemsEqual(
            [self.proposal_template.Title(),
             self.ad_hoc_agenda_item_template.Title(),
             self.recurring_agenda_item_template.Title()],
            [term.title for term in factory(context=None)])

        self.assertItemsEqual(
            [IUUID(self.proposal_template),
             IUUID(self.ad_hoc_agenda_item_template),
             IUUID(self.recurring_agenda_item_template)],
            [term.value for term in factory(context=None)])


class TestProposalTemplatesForCommitteeVocabulary(IntegrationTestCase):
    features = ('meeting',)

    def test_consists_of_all_templates_by_default(self):
        self.login(self.committee_responsible)
        baubewilligungen = create(
            Builder('proposaltemplate')
            .titled(u'Baubewilligung')
            .within(self.templates))

        factory = getUtility(
            IVocabularyFactory,
            name='opengever.meeting.ProposalTemplatesForCommitteeVocabulary')
        self.assertItemsEqual(
            [self.proposal_template,
             baubewilligungen,
             self.ad_hoc_agenda_item_template,
             self.recurring_agenda_item_template],
            [term.value for term in factory(context=self.dossier)])

    def test_reduce_allowed_templates_with_committee_settings(self):
        self.login(self.committee_responsible)
        baubewilligungen = create(
            Builder('proposaltemplate')
            .titled(u'Baubewilligung')
            .within(self.templates))

        factory = getUtility(
            IVocabularyFactory,
            name='opengever.meeting.ProposalTemplatesForCommitteeVocabulary')
        self.assertItemsEqual(
            [self.proposal_template,
             baubewilligungen,
             self.ad_hoc_agenda_item_template,
             self.recurring_agenda_item_template],
            [term.value for term in factory(context=self.dossier)])

        self.committee.allowed_proposal_templates = [IUUID(baubewilligungen)]
        self.request.form['form.widgets.committee'] = [
            unicode(self.committee.load_model().committee_id)]
        self.assertItemsEqual(
            [baubewilligungen],
            [term.value for term in factory(context=self.dossier)])

    def test_offer_predecessor_proposal_document(self):
        self.login(self.committee_responsible)
        factory = getUtility(
            IVocabularyFactory,
            name='opengever.meeting.ProposalTemplatesForCommitteeVocabulary')
        self.assertItemsEqual(
            [self.proposal_template,
             self.ad_hoc_agenda_item_template,
             self.recurring_agenda_item_template],
            [term.value for term in factory(context=self.dossier)])

        self.request.form['form.widgets.predecessor_proposal'] = '/'.join(
            self.word_proposal.getPhysicalPath()).replace('/plone', '')
        self.assertItemsEqual(
            [self.word_proposal.get_proposal_document(),
             self.proposal_template,
             self.ad_hoc_agenda_item_template,
             self.recurring_agenda_item_template],
            [term.value for term in factory(context=self.dossier)])
