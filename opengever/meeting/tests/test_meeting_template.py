from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.testing import IntegrationTestCase


class TestMeetingTemplate(IntegrationTestCase):

    @browsing
    def test_adding_meetingtemplate_works_properly(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.templates)
        factoriesmenu.add('Meeting Template')
        browser.fill({'Title': 'Template'}).submit()

        self.assertEquals(['Item created'], info_messages())
        self.assertEquals(['Template'], browser.css('h1').text)

    @browsing
    def test_adding_paragraphtemplate_works_properly(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.meeting_template)
        factoriesmenu.add('Paragraph for Template')
        browser.fill({'Title': 'Template'}).submit()

        self.assertEquals(['Item created'], info_messages())
        self.assertEquals(['Template'], browser.css('h1').text)
