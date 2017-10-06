from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.testing import IntegrationTestCase
from zope.component import getMultiAdapter
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


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
            filename=u'example.docx',
            content_type='text/plain',
            data='foo bar')
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
            filename=u'example.docx',
            content_type='text/plain',
            data='foo bar')
        manager.checkin()

        manager.revert_to_version(0)
        self.assertEqual(2, self.document_in_proposal.get_current_version_id())
        self.assertEqual(2, self.document_in_dossier.get_current_version_id())

    def test_updates_excerpt_in_dossier_after_modification(self):
        self.assertEqual(None, self.document_in_dossier.get_current_version_id())
        self.document_in_proposal.update_file(
            filename=u'example.docx',
            content_type='text/plain',
            data='foo bar')
        notify(ObjectModifiedEvent(self.document_in_proposal))

        self.assertEqual(1, self.document_in_dossier.get_current_version_id())


class TestExcerpt(IntegrationTestCase):

    features = ('meeting',)

    @browsing
    def test_manual_excerpt_pre_fills_fields(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.meeting.model.get_url())
        browser.css('.generate-manual-excerpt').first.click()

        title_field = browser.find('Title')

        self.assertEqual(
            u'Protocol Excerpt-9. Sitzung der Rechnungspr\xfcfungskommission',
            title_field.value)

        dossier_field = browser.find('form.widgets.dossier')
        self.assertEqual('/'.join(self.meeting_dossier.getPhysicalPath()),
                         dossier_field.value)

    @browsing
    def test_manual_excerpt_can_be_generated(self, browser):
        self.login(self.committee_responsible, browser)
        self.schedule_proposal(self.meeting,
                               self.submitted_word_proposal)
        browser.open(self.meeting.model.get_url())

        browser.css('.generate-manual-excerpt').first.click()
        browser.fill({'agenda_item-2.include:record': True,
                      'Target dossier': self.dossier})
        browser.find('Save').click()

        statusmessages.assert_message(
            u'Excerpt for meeting 9. Sitzung der '
            u'Rechnungspr\xfcfungskommission has been generated successfully')

        self.assertEqual(1, len(self.meeting.model.excerpt_documents))
        document = self.meeting.model.excerpt_documents[0]
        self.assertEqual(0, document.generated_version)

        self.assertEqual(
            self.meeting.model.get_url(), browser.url,
            'should be on meeting view')
        self.assertEqual(
            1, len(browser.css('.excerpts li a.document_link')),
            'generated document should be linked')
        self.assertEqual(
            [u'Protocol Excerpt-9. Sitzung der Rechnungspr\xfcfungskommission'],
            browser.css('.excerpts li a.document_link').text)

    @browsing
    def test_manual_excerpt_form_redirects_to_meeting_on_abort(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.meeting.model.get_url())

        browser.css('.generate-manual-excerpt').first.click()
        browser.find('form.buttons.cancel').click()

        self.assertEqual(self.meeting.model.get_url(), browser.url)

    @browsing
    def test_validator_excerpt_requires_at_least_one_field(self, browser):
        self.login(self.committee_responsible, browser)
        self.schedule_proposal(self.meeting,
                               self.submitted_word_proposal)
        browser.open(self.meeting.model.get_url())

        browser.css('.generate-manual-excerpt').first.click()
        # de-select pre-selected field-checkboxes
        browser.fill({'form.widgets.include_initial_position:list': False,
                      'form.widgets.include_decision:list': False,
                      'agenda_item-2.include:record': True,
                      'Target dossier': self.dossier})
        browser.find('Save').click()

        self.assertEqual(
            'Please select at least one field for the excerpt.',
            browser.css('#opengever_meeting_excerpt div.error').first.text)

    @browsing
    def test_validator_excerpt_requires_at_least_one_agenda_item(self, browser):
        self.login(self.committee_responsible, browser)
        self.schedule_proposal(self.meeting,
                               self.submitted_word_proposal)
        browser.open(self.meeting.model.get_url())

        browser.css('.generate-manual-excerpt').first.click()
        browser.fill({'Target dossier': self.dossier})
        browser.find('Save').click()

        self.assertEqual(
            'Please select at least one agenda item.',
            browser.css('#opengever_meeting_excerpt div.error').first.text)
