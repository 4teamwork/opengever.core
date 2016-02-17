from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.meeting.model import Meeting
from opengever.testing import FunctionalTestCase


class TestExcerpt(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestExcerpt, self).setUp()
        self.admin_unit.public_url = 'http://nohost/plone'

        self.repository_root, self.repository_folder = create(
            Builder('repository_tree'))
        self.dossier = create(
            Builder('dossier').within(self.repository_folder))
        self.meeting_dossier = create(
            Builder('meeting_dossier').within(self.repository_folder))

        self.templates = create(Builder('templatedossier'))
        self.sablon_template = create(
            Builder('sablontemplate')
            .within(self.templates)
            .with_asset_file('sablon_template.docx'))
        container = create(
            Builder('committee_container').having(
                protocol_template=self.sablon_template,
                excerpt_template=self.sablon_template))

        self.committee = create(Builder('committee').within(container).having(
            repository_folder=self.repository_folder))
        self.proposal = create(Builder('proposal')
                               .within(self.dossier)
                               .having(title='Mach doch',
                                       committee=self.committee.load_model(),
                                       legal_basis=u'We may do it',
                                       initial_position=u'We should do it.',
                                       proposed_action=u'Do it.',
                                       considerations=u'Uhm....',
                                       )
                               .as_submitted())

        self.committee_model = self.committee.load_model()
        self.meeting = create(Builder('meeting')
                              .having(committee=self.committee_model)
                              .link_with(self.meeting_dossier))
        self.proposal_model = self.proposal.load_model()

        self.agenda_item = create(
            Builder('agenda_item')
            .having(meeting=self.meeting,
                    proposal=self.proposal_model,
                    discussion=u'I say Nay!',
                    decision=u'We say yay.',
                    number=u'1'))

    def test_default_excerpt_is_configured_on_commitee_container(self):
        self.assertEqual(self.sablon_template,
                         self.committee.get_excerpt_template())

    @browsing
    def test_excerpt_template_can_be_configured_per_commitee(self, browser):
        self.grant("Administrator")
        custom_template = create(
            Builder('sablontemplate')
            .within(self.templates)
            .with_asset_file('sablon_template.docx'))

        browser.login().open(self.committee, view='edit')
        browser.fill({'Excerpt template': custom_template})
        browser.css('#form-buttons-save').first.click()
        self.assertEqual([], error_messages())

        self.assertEqual(custom_template,
                         self.committee.get_excerpt_template())

    @browsing
    def test_manual_excerpt_pre_fills_fields(self, browser):
        browser.login().open(self.meeting.get_url())
        browser.css('.generate-excerpt').first.click()

        title_field = browser.find('Title')
        self.assertEqual(u'Protocol Excerpt-B\xe4rn, Dec 13, 2011',
                         title_field.value)

        dossier_field = browser.find('form.widgets.dossier')
        self.assertEqual('/'.join(self.meeting_dossier.getPhysicalPath()),
                         dossier_field.value)

    @browsing
    def test_manual_excerpt_can_be_generated(self, browser):
        browser.login().open(self.meeting.get_url())

        browser.css('.generate-excerpt').first.click()
        browser.fill({'agenda_item-1.include:record': True,
                      'Target dossier': self.dossier})
        browser.find('Save').click()

        self.assertEqual([u'Excerpt for meeting B\xe4rn, Dec 13, 2011 has '
                          'been generated successfully'],
                         info_messages())
        # refresh
        meeting = Meeting.get(self.meeting.meeting_id)
        self.assertEqual(1, len(meeting.excerpt_documents))
        document = meeting.excerpt_documents[0]
        self.assertEqual(0, document.generated_version)

        self.assertEqual(self.meeting.get_url(), browser.url,
                         'should be on meeting view')

        self.assertEqual(1, len(browser.css('.excerpts li a')),
                         'generated document should be linked')

        self.assertIsNotNone(browser.find(u'Protocol Excerpt-B\xe4rn, Dec 13, 2011'))

    @browsing
    def test_manual_excerpt_form_redirects_to_meeting_on_abort(self, browser):
        browser.login().open(self.meeting.get_url())
        browser.css('.generate-excerpt').first.click()

        browser.find('form.buttons.cancel').click()
        self.assertEqual(self.meeting.get_url(), browser.url)

    @browsing
    def test_validator_excerpt_requires_at_least_one_field(self, browser):
        browser.login().open(self.meeting.get_url())

        browser.css('.generate-excerpt').first.click()
        # de-select pre-selected field-checkboxes
        browser.fill({'form.widgets.include_initial_position:list': False,
                      'form.widgets.include_decision:list': False,
                      'agenda_item-1.include:record': True,
                      'Target dossier': self.dossier})
        browser.find('Save').click()

        self.assertEqual(
            'Please select at least one field for the excerpt.',
            browser.css('#opengever_meeting_excerpt div.error').first.text)

    @browsing
    def test_validator_excerpt_requires_at_least_one_agenda_item(self, browser):
        browser.login().open(self.meeting.get_url())

        browser.css('.generate-excerpt').first.click()
        browser.fill({'Target dossier': self.dossier})
        browser.find('Save').click()

        self.assertEqual(
            'Please select at least one agenda item.',
            browser.css('#opengever_meeting_excerpt div.error').first.text)
