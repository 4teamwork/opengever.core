from ftw.testbrowser import browsing
from ftw.testbrowser.exceptions import FormFieldNotFound
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import statusmessages
from opengever.testing import IntegrationTestCase
from operator import methodcaller


class TestMeetingAppExportView(IntegrationTestCase):
    features = ('meeting', 'word-meeting')

    @browsing
    def test_button_displayed_on_meeting_view(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.meeting)
        self.assertTrue(browser.css('a.actionicon-object_buttons-export-meeting-app'))
        self.assertEquals(
            'Export to meeting application',
            browser.css('a.actionicon-object_buttons-export-meeting-app > .subMenuTitle').first.text)

    @browsing
    def test_manager_visible_fields_in_committee_forms(self, browser):
        """Some fields should only be displayed when the word feature is
        enabled.
        Therefore we test the appearance of all fields.
        """
        fields = ['Title',
                  'Committeeresponsible',
                  'Protocol header template',
                  'Protocol suffix template',
                  'Agenda item header template for the protocol',
                  'Agenda item suffix template for the protocol',
                  'Excerpt header template',
                  'Excerpt suffix template',
                  'Agendaitem list template',
                  'Table of contents template',
                  'Linked repository folder',
                  'Ad hoc agenda item template',
                  'Paragraph template',
                  'Allowed proposal templates',
                  'Meeting app export URL']

        with self.login(self.manager, browser):
            browser.open(self.committee_container)
            factoriesmenu.add('Committee')
            self.assertEquals(
                fields,
                map(methodcaller('normalized_text', recursive=False),
                    browser.css('form#form > div.field > label')))

            browser.open(self.committee, view='edit')
            self.assertEquals(
                fields,
                map(methodcaller('normalized_text', recursive=False),
                    browser.css('form#form > div.field > label')))

    @browsing
    def test_manager_can_edit_meeting_export_url_on_committe(self, browser):
        self.login(self.manager, browser)

        browser.open(self.committee, view='edit')
        form = browser.forms['form']

        self.assertEqual(u'Rechnungspr\xfcfungskommission',
                         form.find_field('Title').value)

        browser.fill({'Meeting app export URL': u'https://some.url'})
        browser.css('#form-buttons-save').first.click()

        statusmessages.assert_message('Changes saved')

    @browsing
    def test_responsible_cannot_edit_meeting_export_url_on_committe(self, browser):
        self.login(self.committee_responsible, browser)

        browser.open(self.committee, view='edit')
        form = browser.forms['form']

        self.assertEqual(u'Rechnungspr\xfcfungskommission',
                         form.find_field('Title').value)

        with self.assertRaises(FormFieldNotFound):
            browser.fill({'Meeting app export URL': u'https://some.url'})

    @browsing
    def test_export_of_meeting_of_committee_without_export_url_is_not_possible(self, browser):
        self.login(self.committee_responsible, browser)

        browser.open(self.meeting, view='export-meeting-app')
        self.assertEquals(
            [u'The committee Rechnungspr\xfcfungskommission has no meeting app export URL.',
             'An unexpected error has occured'],
            statusmessages.error_messages())
