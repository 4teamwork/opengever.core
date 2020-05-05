from ftw.builder import Builder
from ftw.builder import create
from opengever.base.oguid import Oguid
from opengever.meeting.vocabulary import get_committee_member_vocabulary
from opengever.meeting.vocabulary import get_proposal_transitions_vocabulary
from opengever.testing import IntegrationTestCase
from plone.uuid.interfaces import IUUID
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory


class TestProposalTransitionsVocabulary(IntegrationTestCase):

    def test_get_proposal_transitions_vocabulary_draft_proposal(self):
        self.login(self.regular_user)
        terms = get_proposal_transitions_vocabulary(self.draft_proposal)
        self.assertItemsEqual(
            ['proposal-transition-cancel', 'proposal-transition-submit'],
            [term.value for term in terms])

    def test_get_proposal_transitions_vocabulary_submitted_proposal(self):
        self.login(self.regular_user)
        terms = get_proposal_transitions_vocabulary(self.proposal)
        self.assertItemsEqual([], [term.value for term in terms])


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
            [Oguid.for_object(self.empty_committee).id,
             Oguid.for_object(self.committee).id],
            [term.value for term in factory(context=None)])

        self.empty_committee.load_model().deactivate()
        self.assertItemsEqual(
            [Oguid.for_object(self.committee).id],
            [term.value for term in factory(context=None)])


class TestCommitteeMemberVocabulary(IntegrationTestCase):

    def test_return_fullname_with_email_as_title(self):
        self.login(self.meeting_user)
        vocabulary = get_committee_member_vocabulary(self.meeting)

        self.assertEqual(
            [u'Sch\xf6ller Heidrun (h.schoeller@example.org)',
             u'W\xf6lfl Gerda (g.woelfl@example.com)',
             u'Wendler Jens (jens-wendler@example.com)'],
            [term.title for term in vocabulary])

    def test_returns_member_as_value(self):
        self.login(self.meeting_user)
        vocabulary = get_committee_member_vocabulary(self.meeting)

        self.assertEqual(
            [self.committee_president.model,
             self.committee_participant_1.model,
             self.committee_participant_2.model],
            [term.value for term in vocabulary])

    def test_omits_braces_when_no_email_is_available(self):
        self.login(self.meeting_user)
        self.committee_president.model.email = None

        vocabulary = get_committee_member_vocabulary(self.meeting)
        self.assertEqual(u'Sch\xf6ller Heidrun', vocabulary._terms[0].title)


class TestProposalTemplatesVocabulary(IntegrationTestCase):

    def test_contains_proposal_templates(self):
        self.login(self.regular_user)
        factory = getUtility(IVocabularyFactory,
                             name='opengever.meeting.ProposalTemplatesVocabulary')
        self.assertItemsEqual(
            [self.proposal_template.Title(),
             self.ad_hoc_agenda_item_template.Title(),
             self.recurring_agenda_item_template.Title()],
            [term.title.encode('utf-8') for term in factory(context=None)])

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
        self.request.form['form.widgets.committee_oguid'] = [
            unicode(self.committee.load_model().oguid)]
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
            self.proposal.getPhysicalPath()).replace('/plone', '')
        self.assertItemsEqual(
            [self.proposal.get_proposal_document(),
             self.proposal_template,
             self.ad_hoc_agenda_item_template,
             self.recurring_agenda_item_template],
            [term.value for term in factory(context=self.dossier)])
