from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import statusmessages
from opengever.testing import IntegrationTestCase
from plone.protect import createToken
import json


class TestMeetingTemplate(IntegrationTestCase):

    features = (
        'meeting',
    )

    @browsing
    def test_adding_meetingtemplate_works_properly(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        browser.open(self.templates)
        factoriesmenu.add('Meeting Template')
        browser.fill({
            'Title': 'Template',
            'Description': u'Template for m\xfc\xfcting',
        }).submit()

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
        self.login(self.dossier_responsible, browser=browser)

        browser.open(self.meeting_template)
        factoriesmenu.add('Paragraph Template')
        browser.fill({
            'Title': 'Template',
            'Description': u'Paragraphtemplate for m\xfc\xfcting',
        }).submit()
        statusmessages.assert_no_error_messages()

        self.assertEquals(['Item created'], statusmessages.info_messages())
        self.assertEquals([u'Meeting T\xc3\xb6mpl\xc3\xb6te'], browser.css('h1').text)

    @browsing
    def test_deleting_paragraphtemplates_works_properly(self, browser):
        self.login(self.administrator, browser)
        browser.open(self.paragraph_template)
        self.assertEqual(3, len(self.meeting_template.objectValues()))
        expected_actions = ['Delete', 'Sharing']
        available_actions = browser.css('#plone-contentmenu-actions .actionMenuContent a').text
        self.assertEqual(expected_actions, available_actions)
        browser.find('Delete').click()
        # Confirmation
        browser.find('Delete').click()
        self.assertEqual(2, len(self.meeting_template.objectValues()))

    @browsing
    def test_add_meeting_from_template(self, browser):
        self.login(self.committee_responsible, browser)
        committee_model = self.committee.load_model()
        previous_meetings = len(committee_model.meetings)

        # create meeting
        browser.open(self.committee, view='add-meeting')

        self.assertEquals(
            [u'Title',
             u'form.widgets.meeting_template',
             u'form.widgets.meeting_template',
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

        self.assertEquals(
                ['', u'Meeting T\xc3\xb6mpl\xc3\xb6te',
                 'nicole.kohler', '31.08.2016'],
                browser.find('Meeting Template').table.lists()[2]
            )

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

    @browsing
    def test_update_paragraph_order(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        self.assertEquals(
            ['paragraphtemplate-1',
             'paragraphtemplate-2',
             'paragraphtemplate-3'],
            [paragraph.getId() for paragraph in self.meeting_template.get_paragraphs()])

        new_order = ['paragraphtemplate-2',
                     'paragraphtemplate-1',
                     'paragraphtemplate-3']

        browser.open(self.meeting_template,
                     view='update_content_order',
                     data={
                         'sortOrder': json.dumps(new_order),
                         '_authenticator': createToken(),
                     })
        statusmessages.assert_no_error_messages()

        self.assertEquals(
            new_order,
            [paragraph.getId() for paragraph in self.meeting_template.get_paragraphs()])

    @browsing
    def test_meeting_template_name_from_title_behaviour(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        self.assertEquals(
            'meetingtemplate-1',
            self.meeting_template.getId())
