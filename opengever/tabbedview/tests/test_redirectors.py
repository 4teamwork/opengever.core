from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.testing import IntegrationTestCase


class RedirectorTests(IntegrationTestCase):

    @browsing
    def test_sablon_template_redirector(self, browser):
        self.login(self.administrator, browser)
        browser.open(self.templates, view='++add++opengever.meeting.sablontemplate')

        browser.fill({
            'Title': u'Sablonv\xferlage',
            'File': ('Sablon Template', 'sablon_template.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
        }).save()
        statusmessages.assert_no_error_messages()

        self.assertEquals('http://nohost/plone/vorlagen#sablontemplates-proxy',
                          browser.url)
