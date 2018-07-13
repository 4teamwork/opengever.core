from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import statusmessages
from opengever.testing import IntegrationTestCase


class TestMeetingTemplate(IntegrationTestCase):

    @browsing
    def test_adding_meetingtemplate_works_properly(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.templates)
        factoriesmenu.add('Meeting Template')
        browser.fill({'Title': 'Template'}).submit()

        self.assertEquals(['Item created'], statusmessages.info_messages())
        self.assertEquals(['Template'], browser.css('h1').text)

    @browsing
    def test_adding_paragraphtemplate_cannot_be_added_to_the_templatefolder(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.templates)

        with self.assertRaises(ValueError):
            factoriesmenu.add('Paragraph Template')

    @browsing
    def test_adding_paragraphtemplate_works_properly(self, browser):
        self.login(self.manager, browser=browser)

        browser.open(self.meeting_template)
        factoriesmenu.add('Paragraph Template')
        browser.fill({'Title': 'Template'}).submit()
        statusmessages.assert_no_error_messages()

        self.assertEquals(['Item created'], statusmessages.info_messages())
        self.assertEquals([u'Meeting T\xc3\xb6mpl\xc3\xb6te'], browser.css('h1').text)

    @browsing
    def test_add_meeting_from_template(self, browser):
        self.login(self.committee_responsible, browser)
        committee_model = self.committee.load_model()
        previous_meetings = len(committee_model.meetings)

        # create meeting
        browser.open(self.committee, view='add-meeting')

        self.assertEquals(
            [u'Title',
             u'Meeting Template',
             u'form.widgets.meeting_template-empty-marker',
             u'form.widgets.committee:list',
             u'form.widgets.committee-empty-marker',
             u'Location',
             u'Start',
             u'End',
             u'form.buttons.save',
             u'form.buttons.button_cancel',
             u'_authenticator'],
            browser.css('form').pop().field_labels)

        browser.fill({
            'Title': u'M\xe4\xe4hting',
            'Meeting Template': u'Meeting T\xc3\xb6mpl\xc3\xb6te',
            'Start': '01.01.2010 10:00',
            'End': '01.01.2010 11:00',
            'Location': 'Somewhere',
        }).submit()

        # create dossier
        browser.find('Save').click()

        # back to meeting page
        self.assertEqual(
            [u'The meeting and its dossier were created successfully'],
            statusmessages.info_messages())

        self.assertEqual(
            'http://nohost/plone/opengever-meeting-committeecontainer/committee-1#meetings',
            browser.url)

        committee_model = self.committee.load_model()
        self.assertEqual(previous_meetings + 1, len(committee_model.meetings))
        meeting = committee_model.meetings[-1]

        expected = [u'Begr\xfcssung', u'Gesch\xf0fte', u'Schlusswort']
        self.assertEquals(expected, [
            paragraph.title
            for paragraph in self.meeting_template.get_paragraphs()
        ])
        self.assertEquals(expected, [
            agenda_item.title
            for agenda_item in meeting.agenda_items
            if agenda_item.is_paragraph
        ])
