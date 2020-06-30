from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.security import elevated_privileges
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.meeting.model import Excerpt
from opengever.testing import IntegrationTestCase
from opengever.trash.remover import Remover
from opengever.trash.trash import ITrashable
from opengever.trash.trash import TrashError
from z3c.relationfield.event import _relations
from zope.component import getMultiAdapter
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


def meeting_fields(browser):
    result = {}
    for row in browser.css('tr.meetinglink'):
        label = row.css('th')[0].text
        node = row.css('td')[0]
        result[label] = node
    return result


class TestTrashReturnedExcerpt(IntegrationTestCase):

    @browsing
    def test_trash_excerpt_is_forbidden_when_it_has_been_returned_to_proposal(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(self.meeting, self.submitted_proposal)
        agenda_item.decide()
        excerpt1 = agenda_item.generate_excerpt('excerpt 1')

        ITrashable(excerpt1).trash()

        ITrashable(excerpt1).untrash()
        agenda_item.return_excerpt(excerpt1)

        with self.assertRaises(TrashError):
            ITrashable(excerpt1).trash()


class TestRemoveTrashedExcerpt(IntegrationTestCase):

    @browsing
    def test_remove_excerpt_for_adhoc_agendaitem_removes_entry_from_sql_database(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_ad_hoc(self.meeting, 'Foo')
        agenda_item.decide()
        excerpt1 = agenda_item.generate_excerpt('excerpt 1')
        agenda_item.generate_excerpt('excerpt 2')

        self.assertEqual(2, len(agenda_item.get_excerpt_documents(include_trashed=True)))
        excerpts = Excerpt.query.filter(Excerpt.agenda_item_id == agenda_item.agenda_item_id).all()
        self.assertEqual(2, len(excerpts))

        ITrashable(excerpt1).trash()
        with elevated_privileges():
            Remover([excerpt1]).remove()

        self.assertEqual(1, len(agenda_item.get_excerpt_documents(include_trashed=True)))
        excerpts = Excerpt.query.filter(Excerpt.agenda_item_id == agenda_item.agenda_item_id).all()
        self.assertEqual(1, len(excerpts))

    @browsing
    def test_remove_excerpt_for_agendaitem_removes_relation_in_submitted_proposal(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(self.meeting, self.submitted_proposal)
        agenda_item.decide()
        excerpt1 = agenda_item.generate_excerpt('excerpt 1')
        agenda_item.generate_excerpt('excerpt 2')

        self.assertEqual(2, len(self.submitted_proposal.excerpts))
        self.assertEqual(2, len(self.submitted_proposal.get_excerpts(include_trashed=True)))
        self.assertEqual(2, len(agenda_item.get_excerpt_documents(include_trashed=True)))
        self.assertEqual(2, len(list(_relations(self.submitted_proposal))))

        ITrashable(excerpt1).trash()
        with elevated_privileges():
            Remover([excerpt1]).remove()

        self.assertEqual(1, len(self.submitted_proposal.excerpts))
        self.assertEqual(1, len(self.submitted_proposal.get_excerpts(include_trashed=True)))
        self.assertEqual(1, len(agenda_item.get_excerpt_documents(include_trashed=True)))
        self.assertEqual(1, len(list(_relations(self.submitted_proposal))))


class TestSyncExcerpt(IntegrationTestCase):

    features = ('meeting',)

    def setUp(self):
        super(TestSyncExcerpt, self).setUp()

        # XXX OMG - this should be in the fixture somehow, or at least be
        # build-able in fewer lines.
        self.login(self.committee_responsible)

        self.document_in_dossier = self.document
        self.excerpt_in_dossier = create(
            Builder('generated_excerpt')
            .for_document(self.document_in_dossier))
        self.submitted_proposal.load_model().excerpt_document = self.excerpt_in_dossier

        self.document_in_proposal = create(
            Builder('document')
            .with_dummy_content()
            .within(self.submitted_proposal))
        self.excerpt_in_proposal = create(
            Builder('generated_excerpt')
            .for_document(self.document_in_proposal))
        self.submitted_proposal.load_model().submitted_excerpt_document = self.excerpt_in_proposal

    def test_updates_excerpt_in_dossier_after_checkin(self):
        self.assertEqual(None, self.document_in_proposal.get_current_version_id())
        self.assertEqual(None, self.document_in_dossier.get_current_version_id())
        manager = getMultiAdapter((self.document_in_proposal,
                                   self.portal.REQUEST),
                                  ICheckinCheckoutManager)
        manager.checkout()
        self.document_in_proposal.update_file(
            'foo bar',
            content_type='text/plain',
            filename=u'example.docx')
        manager.checkin()

        self.assertEqual(1, self.document_in_proposal.get_current_version_id())
        self.assertEqual(1, self.document_in_dossier.get_current_version_id())

    def test_updates_excerpt_in_dossier_after_revert(self):
        self.assertEqual(None, self.document_in_proposal.get_current_version_id())
        self.assertEqual(None, self.document_in_dossier.get_current_version_id())
        manager = getMultiAdapter((self.document_in_proposal,
                                   self.portal.REQUEST),
                                  ICheckinCheckoutManager)
        manager.checkout()
        self.document_in_proposal.update_file(
            'foo bar',
            content_type='text/plain',
            filename=u'example.docx')
        manager.checkin()

        manager.revert_to_version(0)
        self.assertEqual(2, self.document_in_proposal.get_current_version_id())
        self.assertEqual(2, self.document_in_dossier.get_current_version_id())

    def test_updates_excerpt_in_dossier_after_modification(self):
        self.assertEqual(None, self.document_in_dossier.get_current_version_id())
        self.document_in_proposal.update_file(
            'foo bar',
            filename=u'example.docx',
            content_type='text/plain')
        notify(ObjectModifiedEvent(self.document_in_proposal))

        self.assertEqual(1, self.document_in_dossier.get_current_version_id())


class TestExcerptOverview(IntegrationTestCase):

    features = ('meeting',)
    maxDiff = None

    @browsing
    def test_excerpt_overview_displays_link_to_proposal_and_submitted_proposal(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(self.meeting, self.submitted_proposal)
        agenda_item.decide()
        excerpt1 = agenda_item.generate_excerpt('excerpt 1')
        agenda_item.return_excerpt(excerpt1)

        expected_fields = [
            'Submitted Proposal',
            'Proposal',
            'Meeting'
        ]
        browser.open(excerpt1, view='tabbedview_view-overview')
        fields = meeting_fields(browser)
        self.assertItemsEqual(expected_fields, fields.keys(),
            msg='The committee responsible can view the meeting and the case '
                'dossier thus all links should appear')

        self.assertEqual(u'Vertr\xe4ge', fields['Submitted Proposal'].text)
        self.assertEqual(
            self.submitted_proposal.absolute_url(),
            fields['Submitted Proposal'].css('a').first.get('href'))

        self.assertEqual(
            u'9. Sitzung der Rechnungspr\xfcfungskommission',
            fields['Meeting'].text)
        self.assertEqual(
            self.meeting.model.get_url(),
            fields['Meeting'].css('a').first.get('href'))

        self.assertEqual(u'Vertr\xe4ge', fields['Proposal'].text)
        self.assertEqual(
            self.proposal.absolute_url(),
            fields['Proposal'].css('a').first.get('href'))

    @browsing
    def test_no_link_to_proposal_visible_if_no_access_to_dossier(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(self.meeting, self.submitted_proposal)
        agenda_item.decide()
        excerpt1 = agenda_item.generate_excerpt('excerpt 1')
        agenda_item.return_excerpt(excerpt1)

        # block access to `proposal` for `committee_responsible`
        self.dossier.__ac_local_roles_block__ = True

        expected_fields = [
            'Submitted Proposal',
            'Meeting'
        ]
        browser.open(excerpt1, view='tabbedview_view-overview')
        fields = meeting_fields(browser)

        self.assertItemsEqual(expected_fields, fields.keys(),
            msg='The user we test with should see a link to submitted '
                'proposal and meeting, but not to the proposal')

        self.assertEqual(u'Vertr\xe4ge', fields['Submitted Proposal'].text)
        self.assertEqual(
            self.submitted_proposal.absolute_url(),
            fields['Submitted Proposal'].css('a').first.get('href'))

        self.assertEqual(
            u'9. Sitzung der Rechnungspr\xfcfungskommission',
            fields['Meeting'].text)
        self.assertEqual(
            self.meeting.model.get_url(),
            fields['Meeting'].css('a').first.get('href'))

    @browsing
    def test_no_link_to_submitted_proposal_visible_if_no_access_to_committee(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(self.meeting, self.submitted_proposal)
        agenda_item.decide()
        excerpt1 = agenda_item.generate_excerpt('excerpt 1')
        agenda_item.return_excerpt(excerpt1)

        self.login(self.regular_user, browser)

        expected_fields = [
            'Proposal',
            'Meeting'
        ]
        browser.open(excerpt1, view='tabbedview_view-overview')
        fields = meeting_fields(browser)
        self.assertItemsEqual(expected_fields, fields.keys(),
            msg='The dossier responsible cannot view the submitted proposal')

        self.assertEqual(u'Vertr\xe4ge', fields['Proposal'].text)
        self.assertEqual(
            self.proposal.absolute_url(),
            fields['Proposal'].css('a').first.get('href'))

        self.assertEqual(
            u'9. Sitzung der Rechnungspr\xfcfungskommission',
            fields['Meeting'].text)
        self.assertEqual([], fields['Meeting'].css('a'),
            'The meeting is not visible to regular_user and thus should not '
            'be linked')

    @browsing
    def test_excerpt_overview_hides_link_to_proposal_when_insufficient_privileges(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(self.meeting, self.submitted_proposal)
        agenda_item.decide()
        excerpt1 = agenda_item.generate_excerpt('excerpt 1')
        agenda_item.return_excerpt(excerpt1)

        # block access to `proposal` for `regular_user`
        self.dossier.__ac_local_roles_block__ = True

        expected_fields = []
        self.login(self.regular_user, browser)
        browser.open(excerpt1, view='tabbedview_view-overview')
        fields = meeting_fields(browser)
        self.assertItemsEqual(expected_fields, fields.keys())
