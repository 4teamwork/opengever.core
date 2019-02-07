from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testing import freeze
from ooxml_docprops import read_properties
from opengever.dossier.docprops import TemporaryDocFile
from opengever.meeting.command import MIME_DOCX
from opengever.testing import IntegrationTestCase
import pytz


class TestAgendaItemList(IntegrationTestCase):

    features = ('meeting', 'doc-properties')

    def test_default_template_is_configured_on_committee_container(self):
        self.login(self.committee_responsible)

        self.assertEqual(self.sablon_template,
                         self.committee.get_agendaitem_list_template())

    @browsing
    def test_template_can_be_configured_per_committee(self, browser):
        with self.login(self.administrator, browser):
            custom_template = create(
                Builder('sablontemplate')
                .within(self.templates)
                .with_asset_file('sablon_template.docx'))

        with self.login(self.committee_responsible, browser):
            browser.open(self.committee, view='edit')
            browser.fill({'Agendaitem list template': custom_template})
            browser.css('#form-buttons-save').first.click()

            self.assertEqual(custom_template,
                             self.committee.get_agendaitem_list_template())

    @browsing
    def test_agendaitem_list_shows_statusmessage_when_no_template_is_configured(self, browser):
        self.login(self.administrator, browser)
        self.committee_container.agendaitem_list_template = None

        self.login(self.committee_responsible, browser)
        browser.open(self.meeting)
        browser.css('.agenda-item-list-doc .action.generate').first.click()

        self.assertEqual(self.meeting.model.get_url(), browser.url)
        self.assertEqual(
            u'There is no agendaitem list template configured, '
            'agendaitem list could not be generated.',
            error_messages()[0])

    @browsing
    def test_agendaitem_list_can_be_created_and_updated(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.meeting)

        meeting = self.meeting.model
        self.assertIsNone(meeting.agendaitem_list_document)

        browser.css('.document-actions .action.generate').first.click()

        statusmessages.assert_message(
            u'Agenda item list for meeting 9. Sitzung der '
            u'Rechnungspr\xfcfungskommission has been generated '
            u'successfully.')

        self.assertIsNotNone(meeting.agendaitem_list_document)
        self.assertEqual(u'Agendaitem list-9. Sitzung der Rechnungspruefungskommission.docx',
                         meeting.agendaitem_list_document.resolve_document().file.filename)
        self.assertEqual(0, meeting.agendaitem_list_document.generated_version)

        # update already generated agendaitem list
        browser.css('.document-actions .action.generate').first.click()
        statusmessages.assert_message(
            u'Agenda item list for meeting 9. Sitzung der '
            u'Rechnungspr\xfcfungskommission has been updated successfully.')
        self.assertIsNotNone(meeting.agendaitem_list_document)
        self.assertEqual(1, meeting.agendaitem_list_document.generated_version)

    @browsing
    def test_updating_agendaitem_list_updates_docproperties(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.meeting)

        meeting = self.meeting.model

        browser.css('.document-actions .action.generate').first.click()
        self.assertIsNotNone(meeting.agendaitem_list_document)

        document = meeting.agendaitem_list_document.oguid.resolve_object()
        with TemporaryDocFile(document.file) as tmpfile:
            properties = {key: value for (key, value)
                          in read_properties(tmpfile.path)}
            self.assertEqual(
                'Sitzungsdossier 9/2017', properties['ogg.dossier.title'])

        # change dossier title
        self.meeting_dossier.title = u'New dossier title'

        # update agendaitem list
        browser.css('.document-actions .action.generate').first.click()

        document = meeting.agendaitem_list_document.oguid.resolve_object()
        with TemporaryDocFile(document.file) as tmpfile:
            properties = {key: value for (key, value)
                          in read_properties(tmpfile.path)}
            self.assertEqual(
                u'New dossier title', properties['ogg.dossier.title'])

    @browsing
    def test_agendaitem_list_can_be_downloaded(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.meeting)

        browser.css('.document-actions .action.generate').first.click()
        browser.css('.document-actions .action.download').first.click()

        self.assertEqual(200, browser.status_code)
        expected_headers = {
            'content-disposition': 'attachment; filename="Agendaitem list-9. Sitzung der Rechnungspruefungskommission.docx"',
            'content-type': MIME_DOCX,
        }
        self.assertDictContainsSubset(expected_headers, browser.headers)

    @browsing
    def test_json_data(self, browser):
        self.login(self.committee_responsible, browser)
        self.schedule_proposal(self.meeting, self.proposal)
        self.schedule_ad_hoc(self.meeting, 'ad-hoc')

        with freeze(datetime(2017, 11, 10, 13, 0, tzinfo=pytz.utc)):
            browser.open(self.meeting, view='agenda_item_list/as_json')

        expected_agenda_items = [
            {u'attachments': [{u'filename': u'Vertraegsentwurf.docx',
                               u'title': u'Vertr\xe4gsentwurf'}],
             u'decision_number': None,
             u'dossier_reference_number': u'Client1 1.1 / 1',
             u'is_paragraph': False,
             u'number': '1.',
             u'number_raw': 1,
             u'repository_folder_title': u'Vertr\xe4ge und Vereinbarungen',
             u'title': u'Vertr\xe4ge',
             u'description': u'F\xfcr weitere Bearbeitung bewilligen'},
            {u'decision_number': None,
             u'description': None,
             u'dossier_reference_number': None,
             u'is_paragraph': False,
             u'number': '2.',
             u'number_raw': 2,
             u'repository_folder_title': None,
             u'title': u'ad-hoc'}]

        expected_participants = {
            u'members': [{u'email': u'jens-wendler@gmail.com',
                          u'firstname': u'Jens',
                          u'fullname': u'Wendler Jens',
                          u'lastname': u'Wendler',
                          u'role': None},
                         {u'email': u'g.woelfl@hotmail.com',
                          u'firstname': u'Gerda',
                          u'fullname': u'W\xf6lfl Gerda',
                          u'lastname': u'W\xf6lfl',
                          u'role': None}],
            u'other': [],
            u'presidency': {u'email': u'h.schoeller@web.de',
                            u'firstname': u'Heidrun',
                            u'fullname': u'Sch\xf6ller Heidrun',
                            u'lastname': u'Sch\xf6ller',
                            u'role': None},
            u'secretary': {u'email': u'committee.secretary@example.com',
                           u'firstname': u'C\xf6mmittee',
                           u'fullname': u'Secretary C\xf6mmittee',
                           u'lastname': u'Secretary'}}

        expected_metadata = {
            u'committee': {u'name': u'Rechnungspr\xfcfungskommission'},
            u'document': {u'generated': u'10.11.2017'},
            u'mandant': {u'name': u'Hauptmandant'},
            u'meeting': {u'date': u'12.09.2016',
                         u'end_time': u'07:00 PM',
                         u'location': u'B\xfcren an der Aare',
                         u'number': None,
                         u'start_time': u'05:30 PM'},
            u'protocol': {u'type': u'Agendaitem list'}}

        self.assertDictContainsSubset(expected_metadata, browser.json)
        self.assertDictContainsSubset(expected_participants, browser.json['participants'])
        self.assertEqual(expected_agenda_items, browser.json['agenda_items'])
