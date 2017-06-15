from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.meeting.command import MIME_DOCX
from opengever.testing import FunctionalTestCase
import transaction


class TestAgendaItemList(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestAgendaItemList, self).setUp()
        self.admin_unit.public_url = 'http://nohost/plone'

        self.root, self.repository_folder = create(Builder('repository_tree'))
        self.dossier = create(Builder('dossier')
                              .within(self.repository_folder))
        self.meeting_dossier = create(Builder('meeting_dossier')
                                      .within(self.repository_folder))

        self.templates = create(Builder('templatefolder'))
        self.sablon_template = create(Builder('sablontemplate')
                                      .within(self.templates)
                                      .with_asset_file('sablon_template.docx'))

        self.container = create(
            Builder('committee_container').having(
                protocol_template=self.sablon_template,
                excerpt_template=self.sablon_template,
                agendaitem_list_template=self.sablon_template))

        self.committee = create(Builder('committee')
                                .within(self.container)
                                .having(repository_folder=self.repository_folder))
        self.committee_model = self.committee.load_model()

    def test_default_template_is_configured_on_committee_container(self):
        self.assertEqual(self.sablon_template,
                         self.committee.get_agendaitem_list_template())

    @browsing
    def test_template_can_be_configured_per_committee(self, browser):
        self.grant("Administrator")
        custom_template = create(
            Builder('sablontemplate')
            .within(self.templates)
            .with_asset_file('sablon_template.docx'))

        browser.login().open(self.committee, view='edit')
        browser.fill({'Agendaitem list template': custom_template})
        browser.css('#form-buttons-save').first.click()
        self.assertEqual([], error_messages())

        self.assertEqual(custom_template,
                         self.committee.get_agendaitem_list_template())

    @browsing
    def test_shows_statusmessage_when_no_template_is_configured(self, browser):
        self.container.agendaitem_list_template = None
        transaction.commit()

        meeting = create(Builder('meeting')
                         .having(committee=self.committee_model)
                         .link_with(self.meeting_dossier))

        browser.login().open(meeting.get_url())
        browser.css('.download-agendaitem-list-btn').first.click()

        self.assertEqual(browser.url, meeting.get_url())
        self.assertEqual(
            u'There is no agendaitem list template configured, '
            'agendaitem list could not be generated.',
            error_messages()[0])

    @browsing
    def test_agendaitem_list_can_be_downloaded(self, browser):
        meeting = create(Builder('meeting')
                         .having(committee=self.committee_model)
                         .link_with(self.meeting_dossier))

        browser.login().open(meeting.get_url())
        browser.css('.download-agendaitem-list-btn').first.click()

        self.assertDictContainsSubset(
            {'status': '200 Ok',
             'content-disposition': 'attachment; filename="Agendaitem list-'
             'community-meeting.docx"',
             'x-frame-options': 'SAMEORIGIN',
             'content-type': MIME_DOCX,
             'x-theme-disabled': 'True'},
            browser.headers)

    @browsing
    def test_json_data(self, browser):
        meeting = create(Builder('meeting')
                         .having(committee=self.committee_model)
                         .link_with(self.meeting_dossier))

        browser.login().open(meeting.get_url(view='agenda_item_list/as_json'))

        self.assertDictContainsSubset(
            {u'protocol': {u'type': u'Agendaitem list'},
             u'participants': {u'other': [], u'members': []},
             u'committee': {u'name': u'My Committee'},
             u'mandant': {u'name': u'Client1'},
             u'meeting': {u'date': u'Dec 13, 2011',
                          u'start_time': u'09:30 AM',
                          u'end_time': u'11:45 AM',
                          u'number': None,
                          u'location': u'B\xe4rn'}},
            browser.json)

    @browsing
    def test_contains_proposal_and_freetext_agendaitems(self, browser):
        self.maxDiff = None
        meeting = create(Builder('meeting')
                         .having(committee=self.committee_model)
                         .link_with(self.meeting_dossier))
        committee = create(Builder('committee'))
        proposal = create(Builder('submitted_proposal')
                          .within(committee)
                          .having(title='Mach doch',
                                  committee=committee,
                                  legal_basis=u'We may do it',
                                  decision_draft=u'Proposal approved',
                                  initial_position=u'We should do it.',
                                  proposed_action=u'Do it.',
                                  considerations=u'Uhm....'))

        create(Builder('agenda_item')
               .having(title=u'foo', number=u'2', meeting=meeting))
        create(Builder('agenda_item')
               .having(meeting=meeting, proposal=proposal,
                       discussion=u'I say Nay!', number=u'1'))

        browser.login().open(meeting.get_url(view='agenda_item_list/as_json'))

        self.assertEqual(
            [{u'decision_number': None,
              u'description': u'Mach doch',
              u'dossier_reference_number': u'123',
              u'html:considerations': u'Uhm....',
              u'html:copy_for_attention': None,
              u'html:decision': u'Proposal approved',
              u'html:decision_draft': u'Proposal approved',
              u'html:disclose_to': None,
              u'html:discussion': u'I say Nay!',
              u'html:initial_position': u'We should do it.',
              u'html:legal_basis': u'We may do it',
              u'html:proposed_action': u'Do it.',
              u'html:publish_in': None,
              u'is_paragraph': False,
              u'number': u'1.',
              u'repository_folder_title': u'repo',
              u'title': u'Mach doch'},
             {u'decision_number': None,
              u'description': u'foo',
              u'dossier_reference_number': None,
              u'html:considerations': None,
              u'html:copy_for_attention': None,
              u'html:decision': None,
              u'html:decision_draft': None,
              u'html:disclose_to': None,
              u'html:discussion': None,
              u'html:initial_position': None,
              u'html:legal_basis': None,
              u'html:proposed_action': None,
              u'html:publish_in': None,
              u'is_paragraph': False,
              u'number': u'2.',
              u'repository_folder_title': None,
              u'title': u'foo'}],
            browser.json.get('agenda_items'))
