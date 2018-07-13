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
